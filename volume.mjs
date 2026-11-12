import { createRequire } from 'node:module';
import { Connection, PublicKey } from '@solana/web3.js';
import { generateWallets, loadMasterKeypair } from './lib/wallets.mjs';
import { sleep, toKeypair, getPriorityFee, priorityIxs } from './lib/utils.mjs';
import { buildBuyTx, buildSellTx, sendTx, getTokenProgram } from './lib/tx.mjs';
import { fundWallets, drainWallets } from './lib/fund.mjs';
import { FEE_RESERVE, FUND_MULTIPLIER, POST_FUND_SETTLE_MS, MIN_PRIORITY_FEE } from './lib/constants.mjs';

const require = createRequire(import.meta.url);
const { OnlinePumpSdk } = require('@pump-fun/pump-sdk');
const { getAssociatedTokenAddressSync, createCloseAccountInstruction } = require('@solana/spl-token');

const args = process.argv.slice(2);
const mint = args[0];
const numWallets = parseInt(args[1] || '12', 10);
const totalBudget = parseFloat(args[2] || '0.5');
const durationMin = parseFloat(args[3] || '15');
const buyBias = parseFloat(args[4] || '0.65');

if (!mint) {
  console.log('Usage: node volume.mjs <MINT> [wallets=12] [budget=0.5] [duration_min=15] [buy_bias=0.65]');
  process.exit(1);
}

const conn = new Connection(process.env.RPC_URL, 'confirmed');
const master = loadMasterKeypair();
const mintPk = new PublicKey(mint);
const slippagePct = 15;

console.log(`[apekit] volume bot`);
console.log(`  mint:      ${mint}`);
console.log(`  wallets:   ${numWallets}`);
console.log(`  budget:    ${totalBudget} SOL`);
console.log(`  duration:  ${durationMin} min`);
console.log(`  buy bias:  ${(buyBias * 100).toFixed(0)}%`);
console.log();

const wallets = generateWallets(numWallets);
const stats = { buys: 0, sells: 0, cycles: 0, solSpent: 0 };

const balance = await conn.getBalance(master.publicKey, 'confirmed');
const needed = totalBudget * FUND_MULTIPLIER + 0.01;
if (balance / 1e9 < needed) {
  console.error(`insufficient balance: ${(balance / 1e9).toFixed(4)} SOL, need ~${needed.toFixed(4)}`);
  process.exit(1);
}

// PHASE 1: FUND
console.log('[phase 1] funding wallets...');
const solPerWallet = totalBudget * FUND_MULTIPLIER / numWallets;
await fundWallets(conn, master, wallets, solPerWallet);
await sleep(POST_FUND_SETTLE_MS);

// PHASE 2: SETUP
const [tokenProgram, baseFee] = await Promise.all([getTokenProgram(conn, mintPk), getPriorityFee(conn)]);
const sdk = new OnlinePumpSdk(conn);
const globals = { global: await sdk.fetchGlobal(), feeConfig: await sdk.fetchFeeConfig().catch(() => null) };

// PHASE 3: INITIAL BUYS
console.log('[phase 2] initial buys (staggered)...');
const ws = wallets.map((w, i) => ({
  idx: i, w, kp: toKeypair(w), hasTokens: false, lastUsedAt: 0,
}));

for (const s of ws) {
  try {
    const bal = await conn.getBalance(s.kp.publicKey, 'confirmed');
    const buyPortion = 0.3 + Math.random() * 0.2;
    const buyLamports = Math.floor((bal - FEE_RESERVE) * buyPortion);
    if (buyLamports < 5_000_000) continue;
    const priority = priorityIxs(baseFee);
    const ixs = await buildBuyTx(conn, sdk, globals, mintPk, s.kp.publicKey, buyLamports, slippagePct, tokenProgram);
    await sendTx(conn, ixs, s.kp, priority);
    s.hasTokens = true;
    stats.buys++;
    stats.solSpent += buyLamports / 1e9;
    console.log(`[buy] ${s.w.publicKey.slice(0, 8)}... ${(buyLamports / 1e9).toFixed(4)} SOL`);
    await sleep(2000 + Math.random() * 4000);
  } catch (err) {
    console.error(`[buy] ${s.w.publicKey.slice(0, 8)}... failed: ${err.message}`);
  }
}

const boughtCount = ws.filter(s => s.hasTokens).length;
if (boughtCount === 0) { console.error('no wallets bought — exiting'); process.exit(1); }
console.log(`[phase 2] initial buys done: ${boughtCount}/${numWallets}`);

// PHASE 4: CHURN
console.log(`[phase 3] volume churn for ${durationMin} min...`);
const endTime = Date.now() + durationMin * 60_000;
let prevIdx = -1;
let pauseCounter = 6 + Math.floor(Math.random() * 5);
let consecutiveErrors = 0;

while (Date.now() < endTime) {
  const pool = ws.filter(w => w.idx !== prevIdx);
  pool.sort((a, b) => a.lastUsedAt - b.lastUsedAt);
  const pick = pool[Math.floor(Math.random() * Math.min(3, pool.length))];
  prevIdx = pick.idx;
  pick.lastUsedAt = Date.now();

  const isBuy = !pick.hasTokens || Math.random() < buyBias;
  const fee = baseFee + Math.floor((Math.random() - 0.3) * baseFee * 0.6);
  const priority = priorityIxs(Math.max(MIN_PRIORITY_FEE, fee));

  const baseTradeSol = totalBudget / numWallets * 0.15;

  try {
    if (stats.cycles % 15 === 0 && stats.cycles > 0) {
      globals.global = await sdk.fetchGlobal();
    }

    if (isBuy) {
      const bal = await conn.getBalance(pick.kp.publicKey, 'confirmed');
      const buyLamports = Math.min(
        Math.floor((baseTradeSol + Math.random() * baseTradeSol) * 1e9),
        Math.floor((bal - FEE_RESERVE) * 0.8)
      );
      if (buyLamports < 5_000_000) { await sleep(1000); continue; }
      const ixs = await buildBuyTx(conn, sdk, globals, mintPk, pick.kp.publicKey, buyLamports, slippagePct, tokenProgram);
      await sendTx(conn, ixs, pick.kp, priority);
      pick.hasTokens = true;
      stats.buys++;
      stats.solSpent += buyLamports / 1e9;
      console.log(`[buy]  ${pick.w.publicKey.slice(0, 8)}... ${(buyLamports / 1e9).toFixed(4)} SOL`);
      consecutiveErrors = 0;
    } else {
      const ata = getAssociatedTokenAddressSync(mintPk, pick.kp.publicKey, true, tokenProgram);
      const bal = await conn.getTokenAccountBalance(ata, 'confirmed').catch(() => null);
      const tokenAmount = BigInt(bal?.value?.amount ?? '0');
      if (tokenAmount === 0n) { pick.hasTokens = false; continue; }
      const portion = 0.3 + Math.random() * 0.3;
      const sellAmount = tokenAmount * BigInt(Math.floor(portion * 100)) / 100n;
      if (sellAmount === 0n) continue;
      const ixs = await buildSellTx(conn, sdk, globals, mintPk, pick.kp.publicKey, sellAmount, slippagePct, tokenProgram);
      await sendTx(conn, ixs, pick.kp, priority);
      stats.sells++;
      console.log(`[sell] ${pick.w.publicKey.slice(0, 8)}... ${(portion * 100).toFixed(0)}%`);
      consecutiveErrors = 0;
    }
  } catch (err) {
    consecutiveErrors++;
    console.error(`[fail] ${pick.w.publicKey.slice(0, 8)}...: ${err.message}`);
    if (consecutiveErrors >= 5) {
      console.error('[volume] 5 consecutive errors — stopping');
      break;
    }
  }

  stats.cycles++;

  let delayMs;
  if (stats.cycles >= pauseCounter) {
    delayMs = 10_000 + Math.random() * 10_000;
    pauseCounter = stats.cycles + 5 + Math.floor(Math.random() * 4);
    console.log(`[pause] ${(delayMs / 1000).toFixed(0)}s`);
  } else {
    delayMs = 1000 + Math.random() * 4000;
  }
  await sleep(delayMs);
}

// PHASE 5: CLEANUP
console.log('\n[phase 4] selling remaining tokens...');
for (const s of ws.filter(s => s.hasTokens)) {
  try {
    const ata = getAssociatedTokenAddressSync(mintPk, s.kp.publicKey, true, tokenProgram);
    const bal = await conn.getTokenAccountBalance(ata, 'confirmed').catch(() => null);
    const amount = BigInt(bal?.value?.amount ?? '0');
    if (amount === 0n) continue;
    const ixs = await buildSellTx(conn, sdk, globals, mintPk, s.kp.publicKey, amount, 25, tokenProgram);
    await sendTx(conn, ixs, s.kp, priorityIxs(baseFee));
    console.log('[sell] cleanup', s.w.publicKey.slice(0, 8));
    await sleep(2000);
    try {
      const closeIx = createCloseAccountInstruction(ata, s.kp.publicKey, s.kp.publicKey, [], tokenProgram);
      await sendTx(conn, [closeIx], s.kp, priorityIxs(baseFee));
    } catch {}
  } catch (err) {
    console.error('[sell] cleanup failed:', s.w.publicKey.slice(0, 8), err.message);
  }
}

console.log('[phase 5] draining wallets...');
await drainWallets(conn, wallets, master);

console.log('\n[apekit] volume bot done');
console.log(`  buys:      ${stats.buys}`);
console.log(`  sells:     ${stats.sells}`);
console.log(`  cycles:    ${stats.cycles}`);
console.log(`  SOL spent: ${stats.solSpent.toFixed(4)}`);
