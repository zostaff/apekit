import { PublicKey } from '@solana/web3.js';

export const FEE_RESERVE = 10_000_000;
export const FUND_MULTIPLIER = 1.3;
export const FUND_OVERHEAD = 0.005;
export const MAX_TRANSFERS_PER_TX = 10;
export const RECLAIM_CONCURRENCY = 5;
export const ESTIMATED_FEE_LAMPORTS = 5000;
export const BUNDLE_MAX_ATTEMPTS = 5;
export const BUNDLE_POLL_COUNT = 10;
export const BUNDLE_POLL_INTERVAL_MS = 3000;
export const POST_FUND_SETTLE_MS = 2000;
export const DEFAULT_BLOCKHASH_TTL_MS = 10_000;
export const DEFAULT_PRIORITY_FEE = 5_000;
export const MIN_PRIORITY_FEE = 1_000;
export const MAX_PRIORITY_FEE = 100_000;
export const PRIORITY_FEE_CACHE_TTL_MS = 10_000;
export const COMPUTE_UNIT_LIMIT = 600_000;
export const TX_LIMIT = 1232;
export const SOL_MINT = new PublicKey('So11111111111111111111111111111111111111112');
export const DEFAULT_TOKEN_PROGRAM = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');

export const JITO_ENDPOINTS = [
  'https://mainnet.block-engine.jito.wtf/api/v1/bundles',
  'https://amsterdam.mainnet.block-engine.jito.wtf/api/v1/bundles',
  'https://tokyo.mainnet.block-engine.jito.wtf/api/v1/bundles',
];

export const JITO_TIP_ACCOUNTS = [
  '96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5',
  'HFqU5x63VTqvQss8hp11i4bPg7v3Nit2hAZNRcJL1rRx',
  'Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY',
  'ADaUMid9yfUytqMBgopwjb2DTLSLtrihvYF8i8nQafEe',
  'DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh',
  'ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt',
  'DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL',
  '3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT',
];

export const JITO_DEFAULT_TIP = 1_000_000;
export const JITO_MAX_TIP = 10_000_000;
