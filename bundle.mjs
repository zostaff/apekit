import { createRequire } from 'node:module';
import { Connection, PublicKey, TransactionMessage, VersionedTransaction } from '@solana/web3.js';
import { generateWallets, loadMasterKeypair } from './lib/wallets.mjs';
import { sleep, toKeypair, getPriorityFee, priorityIxs } from './lib/utils.mjs';
import { buildBuyTx, buildSignedTx, sendTx, getTokenProgram } from './lib/tx.mjs';
import { jitoTipIx, sendJitoBundle, pollJitoBundleStatus } from './lib/jito.mjs';
import { fundWallets, drainWallets } from './lib/fund.mjs';
import {
  FEE_RESERVE, FUND_MULTIPLIER, FUND_OVERHEAD, POST_FUND_SETTLE_MS,
  BUNDLE_MAX_ATTEMPTS, JITO_DEFAULT_TIP, JITO_MAX_TIP,
} from './lib/constants.mjs';

const require = createRequire(import.meta.url);
const { OnlinePumpSdk } = require('@pump-fun/pump-sdk');

const args = process.argv.slice(2);
const mint = args[0];
const numWallets = parseInt(args[1] || '5', 10);
const totalBudget = parseFloat(args[2] || '0.5');
const mode = args[3] || 'jito';

if (!mint) {
  console.log('Usage: node bundle.mjs <MINT> [wallets=5] [budget=0.5] [mode=jito|staggered]');
  process.exit(1);
}

const conn = new Connection(process.env.RPC_URL, 'confirmed');
const master = loadMasterKeypair();
const slippage = 15;

console.log(`[apekit] bundler`);
console.log(`  mint:     ${mint}`);
console.log(`  wallets:  ${numWallets}`);
console.log(`  budget:   ${totalBudget} SOL`);
console.log(`  mode:     ${mode}`);
console.log(`  master:   ${master.publicKey.toBase58().slice(0, 8)}...`);
console.log();

const mintPk = new PublicKey(mint);
const wallets = generateWallets(numWallets);
const perWallet = totalBudget / numWallets;

const balance = await conn.getBalance(master.publicKey, 'confirmed');
const needed = totalBudget * 1.3 + 0.01;
if (balance / 1e9 < needed) {
  console.error(`insufficient balance: ${(balance / 1e9).toFixed(4)} SOL, need ~${needed.toFixed(4)}`);
  process.exit(1);
}

// PHASE 1: FUND
console.log('[phase 1] funding wallets...');
const fundAmount = perWallet * FUND_MULTIPLIER + FUND_OVERHEAD;
const fundResults = await fundWallets(conn, master, wallets, fundAmount);
const funded = fundResults.filter(r => r.status === 'sent').length;
if (funded === 0) { console.error('all funding txs failed'); process.exit(1); }
console.log(`[phase 1] funded ${funded}/${numWallets}`);
await sleep(POST_FUND_SETTLE_MS);

// PHASE 2: BUY
console.log(`[phase 2] buying (${mode})...`);
const tokenProgram = await getTokenProgram(conn, mintPk);
const sdk = new OnlinePumpSdk(conn);
const globals = { global: await sdk.fetchGlobal(), feeConfig: await sdk.fetchFeeConfig().catch(() => null) };
const microLamports = await getPriorityFee(conn);
const priority = priorityIxs(microLamports);
console.log(`[phase 2] priority fee: ${microLamports} microLamports`);

const keypairs = wallets.map(toKeypair);
const balances = await Promise.all(keypairs.map(kp => conn.getBalance(kp.publicKey, 'confirmed').catch(() => 0)));
const buyResults = [];

if (mode === 'jito') {
  let landed = false;
  for (let attempt = 0; attempt < BUNDLE_MAX_ATTEMPTS && !landed; attempt++) {
    try {
      const { blockhash } = await conn.getLatestBlockhash('confirmed');

      const builds = await Promise.all(keypairs.map(async (kp, i) => {
        const bal = balances[i] || await conn.getBalance(kp.publicKey, 'confirmed').catch(() => 0);
        const buyLamports = BigInt(Math.max(0, bal - FEE_RESERVE));
        if (buyLamports <= 0n) return null;
        const buyIxs = await buildBuyTx(conn, sdk, globals, mintPk, kp.publicKey, buyLamports, slippage, tokenProgram);
        return { kp, buyIxs, buyLamports, index: i };
      }));
      const valid = builds.filter(Boolean);
      if (valid.length === 0) { console.log('no wallets with balance'); break; }

      const signedTxs = valid.map(({ kp, buyIxs }) => buildSignedTx(buyIxs, kp, blockhash, priority));

      const tipLamports = Math.min(JITO_DEFAULT_TIP * (attempt + 1), JITO_MAX_TIP);
      const tipIx = jitoTipIx(master.publicKey, tipLamports);
      const tipMsg = new TransactionMessage({ payerKey: master.publicKey, recentBlockhash: blockhash, instructions: [tipIx] }).compileToV0Message();
      const tipTx = new VersionedTransaction(tipMsg);
      tipTx.sign([master]);
      signedTxs.push(tipTx);

      const bundleId = await sendJitoBundle(signedTxs.map(t => t.serialize()));
      console.log(`[jito] bundle sent (attempt ${attempt + 1}, tip ${tipLamports / 1e9} SOL): ${bundleId}`);

      landed = await pollJitoBundleStatus(bundleId);
      if (landed) {
        console.log('[jito] bundle landed!');
        for (const { index, buyLamports } of valid) {
          buyResults.push({ wallet: wallets[index].publicKey, sol: Number(buyLamports) / 1e9, status: 'landed' });
        }
      }
    } catch (err) {
      console.error(`[jito] attempt ${attempt + 1} error:`, err.message);
    }
  }

  if (!landed) {
    console.log('[jito] failed — falling back to individual sends');
    for (let i = 0; i < keypairs.length; i++) {
      try {
        const bal = await conn.getBalance(keypairs[i].publicKey, 'confirmed');
        const buyLamports = BigInt(Math.max(0, bal - FEE_RESERVE));
        if (buyLamports <= 0n) continue;
        const ixs = await buildBuyTx(conn, sdk, globals, mintPk, keypairs[i].publicKey, buyLamports, slippage, tokenProgram);
        const sig = await sendTx(conn, ixs, keypairs[i], priority);
        buyResults.push({ wallet: wallets[i].publicKey, sol: Number(buyLamports) / 1e9, status: 'sent', signature: sig });
        console.log('[buy]', wallets[i].publicKey.slice(0, 8), (Number(buyLamports) / 1e9).toFixed(4), 'SOL');
      } catch (err) {
        buyResults.push({ wallet: wallets[i].publicKey, status: 'failed', error: err.message });
      }
    }
  }

} else {
  // STAGGERED
  for (let i = 0; i < keypairs.length; i++) {
    try {
      const bal = balances[i] || await conn.getBalance(keypairs[i].publicKey, 'confirmed');
      const buyLamports = BigInt(Math.max(0, bal - FEE_RESERVE));
      if (buyLamports <= 0n) continue;
      const ixs = await buildBuyTx(conn, sdk, globals, mintPk, keypairs[i].publicKey, buyLamports, slippage, tokenProgram);
      const sig = await sendTx(conn, ixs, keypairs[i], priority);
      buyResults.push({ wallet: wallets[i].publicKey, sol: Number(buyLamports) / 1e9, status: 'sent', signature: sig });
      console.log('[buy]', wallets[i].publicKey.slice(0, 8), (Number(buyLamports) / 1e9).toFixed(4), 'SOL');
      const delay = 2000 + Math.random() * 3000;
      if (i < keypairs.length - 1) await sleep(delay);
    } catch (err) {
      buyResults.push({ wallet: wallets[i].publicKey, status: 'failed', error: err.message });
    }
  }
}

const sent = buyResults.filter(r => r.status === 'sent' || r.status === 'landed').length;
console.log(`\n[phase 2] buys: ${sent}/${numWallets}`);

// SAVE WALLET KEYS FOR LATER SELL/DRAIN
const { writeFileSync, mkdirSync } = await import('node:fs');
try { mkdirSync('data', { recursive: true }); } catch {}
writeFileSync('data/wallets.json', JSON.stringify({ mint, wallets, buyResults, createdAt: new Date().toISOString() }, null, 2));
console.log('[apekit] wallet keys saved to data/wallets.json');
console.log('[apekit] run `npm run sell` to sell tokens, `npm run drain` to recover SOL');
