import { createRequire } from 'node:module';
import { TransactionMessage, VersionedTransaction, PublicKey } from '@solana/web3.js';
import { TX_LIMIT, DEFAULT_TOKEN_PROGRAM, SOL_MINT } from './constants.mjs';
import { sleep, withRetry } from './utils.mjs';

const require = createRequire(import.meta.url);
const { OnlinePumpSdk, PumpSdk, getBuyTokenAmountFromSolAmount, getSellSolAmountFromTokenAmount } = require('@pump-fun/pump-sdk');
const BN = require('bn.js');

export const PUMP_SDK = new PumpSdk();

export function buildTransaction(payer, instructions, recentBlockhash, signers) {
  const msg = new TransactionMessage({ payerKey: payer.publicKey, recentBlockhash, instructions }).compileToV0Message();
  const tx = new VersionedTransaction(msg);
  tx.sign(signers ?? [payer]);
  return tx;
}

export function buildSignedTx(ixs, signer, blockhash, priority) {
  const candidates = [[...priority, ...ixs], ixs];
  let lastSize = 0;
  for (const instructions of candidates) {
    const msg = new TransactionMessage({ payerKey: signer.publicKey, recentBlockhash: blockhash, instructions }).compileToV0Message();
    const tx = new VersionedTransaction(msg);
    let serialized;
    try { serialized = tx.serialize(); } catch { continue; }
    if (serialized.length > TX_LIMIT) { lastSize = serialized.length; continue; }
    tx.sign([signer]);
    return tx;
  }
  throw new Error(`tx exceeds size limit (${lastSize} > ${TX_LIMIT})`);
}

export async function sendTx(conn, ixs, signer, priority, opts = {}) {
  const blockhash = opts.blockhash ?? (await conn.getLatestBlockhash('confirmed')).blockhash;
  const tx = buildSignedTx(ixs, signer, blockhash, priority);
  return conn.sendTransaction(tx, { skipPreflight: false, maxRetries: 3 });
}

export async function confirmSignaturesBatch(conn, sigs, timeoutMs = 30_000) {
  if (sigs.length === 0) return { confirmed: [], unconfirmed: [], failed: [] };
  const confirmed = new Set();
  const failed = new Set();
  const start = Date.now();
  let pollDelay = 500;
  while (Date.now() - start < timeoutMs) {
    const pending = sigs.filter(s => !confirmed.has(s) && !failed.has(s));
    if (pending.length === 0) break;
    try {
      const { value: statuses } = await conn.getSignatureStatuses(pending, { searchTransactionHistory: false });
      for (let i = 0; i < pending.length; i++) {
        const s = statuses[i];
        if (!s) continue;
        if (s.err) failed.add(pending[i]);
        else if (s.confirmationStatus === 'confirmed' || s.confirmationStatus === 'finalized') confirmed.add(pending[i]);
      }
    } catch {}
    if (confirmed.size + failed.size >= sigs.length) break;
    await sleep(pollDelay);
    pollDelay = Math.min(pollDelay * 1.5, 4000);
  }
  return { confirmed: [...confirmed], unconfirmed: sigs.filter(s => !confirmed.has(s) && !failed.has(s)), failed: [...failed] };
}

export async function buildBuyTx(conn, sdk, globals, mint, user, solLamports, slippage, tokenProgram) {
  const amount = new BN(solLamports.toString());
  const s = await sdk.fetchBuyState(mint, user, tokenProgram);
  const tokens = getBuyTokenAmountFromSolAmount({
    global: globals.global, feeConfig: globals.feeConfig,
    mintSupply: s.bondingCurve.tokenTotalSupply, bondingCurve: s.bondingCurve,
    amount, quoteMint: SOL_MINT,
  });
  return PUMP_SDK.buyV2Instructions({
    global: globals.global, bondingCurveAccountInfo: s.bondingCurveAccountInfo,
    bondingCurve: s.bondingCurve, associatedUserAccountInfo: s.associatedUserAccountInfo,
    mint, user, amount: tokens, quoteAmount: amount, slippage, tokenProgram,
  });
}

export async function buildSellTx(conn, sdk, globals, mint, user, tokenAmount, slippage, tokenProgram) {
  const amount = new BN(tokenAmount.toString());
  const s = await sdk.fetchSellState(mint, user, tokenProgram);
  const out = getSellSolAmountFromTokenAmount({
    global: globals.global, feeConfig: globals.feeConfig,
    mintSupply: s.bondingCurve.tokenTotalSupply, bondingCurve: s.bondingCurve, amount,
  });
  return PUMP_SDK.sellV2Instructions({
    global: globals.global, bondingCurveAccountInfo: s.bondingCurveAccountInfo,
    bondingCurve: s.bondingCurve, mint, user, amount, quoteAmount: out, slippage, tokenProgram,
  });
}

export async function getTokenProgram(conn, mint) {
  const info = await conn.getAccountInfo(mint, 'confirmed');
  return info ? info.owner : DEFAULT_TOKEN_PROGRAM;
}
