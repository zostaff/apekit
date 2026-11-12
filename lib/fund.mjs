import { SystemProgram, PublicKey } from '@solana/web3.js';
import { FEE_RESERVE, MAX_TRANSFERS_PER_TX, RECLAIM_CONCURRENCY, ESTIMATED_FEE_LAMPORTS } from './constants.mjs';
import { sleep, toKeypair, withRetry, BlockhashManager } from './utils.mjs';
import { buildTransaction, confirmSignaturesBatch } from './tx.mjs';

export async function fundWallets(conn, masterKeypair, wallets, solPerWallet) {
  const lamports = BigInt(Math.round(solPerWallet * 1e9));
  const bm = new BlockhashManager(conn);
  const results = [];
  const allSigs = [];

  for (let b = 0; b < wallets.length; b += MAX_TRANSFERS_PER_TX) {
    const chunk = wallets.slice(b, b + MAX_TRANSFERS_PER_TX);
    const blockhash = await bm.get();
    const instructions = chunk.map(w =>
      SystemProgram.transfer({ fromPubkey: masterKeypair.publicKey, toPubkey: new PublicKey(w.publicKey), lamports })
    );
    try {
      const tx = buildTransaction(masterKeypair, instructions, blockhash);
      const sig = await withRetry(() => conn.sendTransaction(tx, { skipPreflight: false, maxRetries: 3 }));
      allSigs.push(sig);
      for (const w of chunk) {
        console.log('[fund] sent:', w.publicKey.slice(0, 8), solPerWallet.toFixed(4), 'SOL');
        results.push({ wallet: w.publicKey, status: 'sent', signature: sig, sol: solPerWallet });
      }
    } catch (err) {
      bm.invalidate();
      for (const w of chunk) {
        console.error('[fund] failed:', w.publicKey.slice(0, 8), err.message);
        results.push({ wallet: w.publicKey, status: 'failed', error: err.message, sol: solPerWallet });
      }
    }
  }

  if (allSigs.length > 0) {
    const conf = await confirmSignaturesBatch(conn, allSigs);
    if (conf.failed.length > 0) console.error('[fund] confirmation failures:', conf.failed.length);
  }

  return results;
}

export async function drainWallets(conn, wallets, masterKeypair) {
  const bm = new BlockhashManager(conn);
  const balances = await Promise.all(
    wallets.map(w => withRetry(() => conn.getBalance(new PublicKey(w.publicKey), 'confirmed')).catch(() => 0))
  );

  const results = new Array(wallets.length);
  let cursor = 0;

  async function worker() {
    while (cursor < wallets.length) {
      const i = cursor++;
      const w = wallets[i];
      const balance = balances[i];
      const send = balance - ESTIMATED_FEE_LAMPORTS;
      if (send < 10_000) { results[i] = { wallet: w.publicKey, status: 'skipped', sol: balance / 1e9 }; continue; }
      try {
        const kp = toKeypair(w);
        const blockhash = await bm.get();
        const ix = SystemProgram.transfer({ fromPubkey: kp.publicKey, toPubkey: masterKeypair.publicKey, lamports: BigInt(send) });
        const tx = buildTransaction(kp, [ix], blockhash);
        const sig = await withRetry(() => conn.sendTransaction(tx, { skipPreflight: false, maxRetries: 3 }));
        results[i] = { wallet: w.publicKey, status: 'sent', signature: sig, sol: send / 1e9 };
        console.log('[drain]', w.publicKey.slice(0, 8), (send / 1e9).toFixed(4), 'SOL');
      } catch (err) {
        results[i] = { wallet: w.publicKey, status: 'failed', error: err.message, sol: 0 };
      }
    }
  }

  await Promise.all(Array.from({ length: Math.min(RECLAIM_CONCURRENCY, wallets.length) }, () => worker()));

  const sentSigs = results.filter(r => r?.status === 'sent' && r.signature).map(r => r.signature);
  if (sentSigs.length > 0) {
    const conf = await confirmSignaturesBatch(conn, sentSigs, 30_000);
    for (const r of results) {
      if (r?.status === 'sent' && r.signature) {
        if (conf.confirmed.includes(r.signature)) r.status = 'confirmed';
        else if (conf.failed.includes(r.signature)) r.status = 'failed-onchain';
      }
    }
  }

  return results;
}
