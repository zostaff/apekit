import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { Connection, PublicKey } from '@solana/web3.js';
import { loadMasterKeypair } from './lib/wallets.mjs';
import { sleep, toKeypair, getPriorityFee, priorityIxs } from './lib/utils.mjs';
import { buildSellTx, sendTx, getTokenProgram } from './lib/tx.mjs';
import { FEE_RESERVE, ESTIMATED_FEE_LAMPORTS } from './lib/constants.mjs';
import { fundWallets } from './lib/fund.mjs';

const require = createRequire(import.meta.url);
const { OnlinePumpSdk } = require('@pump-fun/pump-sdk');
const { getAssociatedTokenAddressSync, createCloseAccountInstruction } = require('@solana/spl-token');

let data;
try { data = JSON.parse(readFileSync('data/wallets.json', 'utf8')); }
catch { console.error('no data/wallets.json — run bundle.mjs first'); process.exit(1); }

const conn = new Connection(process.env.RPC_URL, 'confirmed');
const master = loadMasterKeypair();
const mintPk = new PublicKey(data.mint);
const slippage = 25;

console.log(`[apekit] sell all`);
console.log(`  mint:    ${data.mint}`);
console.log(`  wallets: ${data.wallets.length}`);
console.log();

const tokenProgram = await getTokenProgram(conn, mintPk);
const sdk = new OnlinePumpSdk(conn);
const globals = { global: await sdk.fetchGlobal(), feeConfig: await sdk.fetchFeeConfig().catch(() => null) };
const fee = await getPriorityFee(conn);
const priority = priorityIxs(fee);

let sold = 0;
for (const w of data.wallets) {
  const kp = toKeypair(w);
  try {
    const ata = getAssociatedTokenAddressSync(mintPk, kp.publicKey, true, tokenProgram);
    const bal = await conn.getTokenAccountBalance(ata, 'confirmed').catch(() => null);
    const amount = BigInt(bal?.value?.amount ?? '0');
    if (amount === 0n) { console.log('[skip]', w.publicKey.slice(0, 8), '— no tokens'); continue; }

    const solBal = await conn.getBalance(kp.publicKey, 'confirmed');
    if (solBal < ESTIMATED_FEE_LAMPORTS * 2) {
      console.log('[fund]', w.publicKey.slice(0, 8), '— topping up for gas');
      await fundWallets(conn, master, [w], 0.002);
      await sleep(2000);
    }

    const ixs = await buildSellTx(conn, sdk, globals, mintPk, kp.publicKey, amount, slippage, tokenProgram);
    const sig = await sendTx(conn, ixs, kp, priority);
    sold++;
    console.log('[sold]', w.publicKey.slice(0, 8), `tokens: ${amount}`, sig);
    await sleep(1500);

    try {
      const closeIx = createCloseAccountInstruction(ata, kp.publicKey, kp.publicKey, [], tokenProgram);
      await sendTx(conn, [closeIx], kp, priorityIxs(fee));
    } catch {}
  } catch (err) {
    console.error('[fail]', w.publicKey.slice(0, 8), err.message);
  }
}

console.log(`\n[apekit] sold from ${sold}/${data.wallets.length} wallets`);
console.log('[apekit] run `npm run drain` to recover SOL');
