import { Keypair, ComputeBudgetProgram } from '@solana/web3.js';
import bs58 from 'bs58';
import {
  DEFAULT_BLOCKHASH_TTL_MS, DEFAULT_PRIORITY_FEE, MIN_PRIORITY_FEE,
  MAX_PRIORITY_FEE, PRIORITY_FEE_CACHE_TTL_MS, COMPUTE_UNIT_LIMIT,
} from './constants.mjs';

export function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

export function toKeypair(w) { return Keypair.fromSecretKey(bs58.decode(w.secretKey)); }

export async function withRetry(fn, { retries = 3, baseDelayMs = 500, maxDelayMs = 5000 } = {}) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try { return await fn(); }
    catch (err) {
      lastErr = err;
      if (attempt < retries) {
        const delay = Math.min(baseDelayMs * 2 ** attempt, maxDelayMs);
        await sleep(delay + Math.random() * delay * 0.2);
      }
    }
  }
  throw lastErr;
}

export class BlockhashManager {
  constructor(conn, ttlMs = DEFAULT_BLOCKHASH_TTL_MS) {
    this._conn = conn; this._ttlMs = ttlMs;
    this._blockhash = null; this._fetchedAt = 0; this._pending = null;
  }
  async get() {
    if (this._blockhash && Date.now() - this._fetchedAt < this._ttlMs) return this._blockhash;
    if (!this._pending) this._pending = this._fetch();
    return this._pending;
  }
  async _fetch() {
    try {
      const { blockhash } = await withRetry(() => this._conn.getLatestBlockhash('confirmed'));
      this._blockhash = blockhash; this._fetchedAt = Date.now();
      return blockhash;
    } finally { this._pending = null; }
  }
  invalidate() { this._blockhash = null; this._fetchedAt = 0; }
}

let _feeCache = null;

export async function getPriorityFee(conn) {
  if (_feeCache && Date.now() - _feeCache.ts < PRIORITY_FEE_CACHE_TTL_MS) return _feeCache.fee;
  try {
    const fees = await conn.getRecentPrioritizationFees();
    if (!fees.length) return DEFAULT_PRIORITY_FEE;
    const values = fees.map(f => f.prioritizationFee).sort((a, b) => a - b);
    const k = Math.min(Math.floor(values.length * 0.75), values.length - 1);
    const fee = Math.max(MIN_PRIORITY_FEE, Math.min(values[k], MAX_PRIORITY_FEE));
    _feeCache = { fee, ts: Date.now() };
    return fee;
  } catch { return DEFAULT_PRIORITY_FEE; }
}

export function priorityIxs(microLamports) {
  return [
    ComputeBudgetProgram.setComputeUnitLimit({ units: COMPUTE_UNIT_LIMIT }),
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports }),
  ];
}
