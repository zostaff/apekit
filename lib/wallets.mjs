import { Keypair } from '@solana/web3.js';
import bs58 from 'bs58';

export function generateWallets(count) {
  return Array.from({ length: count }, () => {
    const kp = Keypair.generate();
    return { publicKey: kp.publicKey.toBase58(), secretKey: bs58.encode(kp.secretKey) };
  });
}

export function loadMasterKeypair() {
  const key = process.env.MASTER_KEY;
  if (!key) throw new Error('MASTER_KEY not set in .env');
  return Keypair.fromSecretKey(bs58.decode(key));
}
