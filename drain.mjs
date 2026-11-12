import { readFileSync } from 'node:fs';
import { Connection } from '@solana/web3.js';
import { loadMasterKeypair } from './lib/wallets.mjs';
import { drainWallets } from './lib/fund.mjs';

let data;
try { data = JSON.parse(readFileSync('data/wallets.json', 'utf8')); }
catch { console.error('no data/wallets.json — run bundle.mjs first'); process.exit(1); }

const conn = new Connection(process.env.RPC_URL, 'confirmed');
const master = loadMasterKeypair();

console.log(`[apekit] drain`);
console.log(`  wallets: ${data.wallets.length}`);
console.log(`  master:  ${master.publicKey.toBase58().slice(0, 8)}...`);
console.log();

const results = await drainWallets(conn, data.wallets, master);

const recovered = results.filter(r => r.status === 'confirmed' || r.status === 'sent');
const totalSol = recovered.reduce((s, r) => s + (r.sol || 0), 0);
console.log(`\n[apekit] drained ${recovered.length}/${data.wallets.length} wallets`);
console.log(`[apekit] recovered ~${totalSol.toFixed(4)} SOL`);
