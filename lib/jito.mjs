import { SystemProgram, PublicKey } from '@solana/web3.js';
import bs58 from 'bs58';
import { JITO_ENDPOINTS, JITO_TIP_ACCOUNTS, BUNDLE_POLL_COUNT, BUNDLE_POLL_INTERVAL_MS } from './constants.mjs';
import { sleep } from './utils.mjs';

export function jitoTipIx(payer, lamports) {
  const tip = JITO_TIP_ACCOUNTS[Math.floor(Math.random() * JITO_TIP_ACCOUNTS.length)];
  return SystemProgram.transfer({ fromPubkey: payer, toPubkey: new PublicKey(tip), lamports: BigInt(lamports) });
}

export async function sendJitoBundle(serializedTxs) {
  const b58Txs = serializedTxs.map(t => bs58.encode(Buffer.from(t)));
  const body = JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'sendBundle', params: [b58Txs] });
  const results = await Promise.allSettled(
    JITO_ENDPOINTS.map(url =>
      fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, signal: AbortSignal.timeout(10_000) })
        .then(r => r.json())
    )
  );
  for (const r of results) {
    if (r.status === 'fulfilled' && r.value.result) return r.value.result;
  }
  const errors = results.map(r =>
    r.status === 'rejected' ? r.reason.message : (r.value?.error?.message || JSON.stringify(r.value?.error) || 'unknown')
  );
  throw new Error(`all Jito endpoints failed: ${errors.join('; ')}`);
}

async function checkInflightStatus(bundleId) {
  try {
    const res = await fetch(JITO_ENDPOINTS[0], {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'getInflightBundleStatuses', params: [[bundleId]] }),
      signal: AbortSignal.timeout(5000),
    });
    const json = await res.json();
    return json.result?.value?.[0]?.status ?? null;
  } catch { return null; }
}

async function checkBundleLanded(bundleId) {
  try {
    const res = await fetch(JITO_ENDPOINTS[0], {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'getBundleStatuses', params: [[bundleId]] }),
      signal: AbortSignal.timeout(5000),
    });
    const json = await res.json();
    const status = json.result?.value?.[0];
    return status?.confirmation_status === 'confirmed' || status?.confirmation_status === 'finalized';
  } catch { return false; }
}

export async function pollJitoBundleStatus(bundleId) {
  for (let poll = 0; poll < BUNDLE_POLL_COUNT; poll++) {
    await sleep(BUNDLE_POLL_INTERVAL_MS);
    const inflight = await checkInflightStatus(bundleId);
    console.log(`[jito] bundle status (poll ${poll + 1}): ${inflight || 'pending'}`);
    if (inflight === 'Landed') return true;
    if (inflight === 'Invalid' || inflight === 'Failed') {
      if (await checkBundleLanded(bundleId)) return true;
      return false;
    }
  }
  return await checkBundleLanded(bundleId);
}
