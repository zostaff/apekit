# apekit

pump.fun bundler + volume bot.

Multi-wallet token buying via Jito MEV bundles or staggered individual sends, plus automated volume generation with configurable buy/sell cycling.

## Setup

```bash
npm install
cp .env.example .env
```

Add your RPC endpoint and master wallet private key to `.env`:

```
RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
MASTER_KEY=your_base58_private_key
```

## Bundler

Buy a token from N wallets simultaneously.

```bash
# Jito bundle mode (atomic, all buys land in one block)
node bundle.mjs <MINT> 5 0.5 jito

# Staggered mode (individual sends with random delays)
node bundle.mjs <MINT> 5 0.5 staggered
```

**Arguments:**
| # | Parameter | Default | Description |
|---|-----------|---------|-------------|
| 1 | `MINT` | — | Token mint address |
| 2 | `wallets` | 5 | Number of buy wallets |
| 3 | `budget` | 0.5 | Total SOL to spend |
| 4 | `mode` | jito | `jito` or `staggered` |

**How it works:**
1. Generates fresh wallets
2. Funds them from your master wallet
3. Builds buy transactions for each wallet
4. Sends as a Jito bundle (atomic) or individually (staggered)
5. Saves wallet keys to `data/wallets.json`

Jito mode sends all buys as a single MEV bundle — they either all land in the same block or none do. If the bundle fails after 5 attempts, it falls back to individual sends.

Staggered mode sends buys one at a time with 2-5 second random delays between them.

## Volume Bot

Generate trading volume on a token with multi-wallet buy/sell cycles.

```bash
node volume.mjs <MINT> 12 0.5 15 0.65
```

**Arguments:**
| # | Parameter | Default | Description |
|---|-----------|---------|-------------|
| 1 | `MINT` | — | Token mint address |
| 2 | `wallets` | 12 | Number of trading wallets |
| 3 | `budget` | 0.5 | Total SOL budget |
| 4 | `duration` | 15 | Duration in minutes |
| 5 | `buy_bias` | 0.65 | Buy probability (0-1) |

**How it works:**
1. Generates and funds wallets
2. Makes initial buys across all wallets (30-50% of each wallet's balance)
3. Runs buy/sell cycles for the specified duration:
   - Picks wallets using least-recently-used rotation (never same wallet twice in a row)
   - 65% chance to buy, 35% to sell (configurable)
   - Random trade sizes and timing
   - Periodic pauses every 6-10 cycles to look organic
   - Variable priority fees with jitter
4. Sells all remaining tokens
5. Drains SOL back to master wallet

## Sell & Drain

After bundling, sell tokens and recover SOL:

```bash
# Sell all tokens from bundled wallets
npm run sell

# Drain remaining SOL back to master
npm run drain
```

## Architecture

```
apekit/
├── bundle.mjs          # Bundler — Jito or staggered buys
├── volume.mjs          # Volume bot — buy/sell cycling
├── sell.mjs            # Sell all tokens from wallets
├── drain.mjs           # Drain SOL back to master
└── lib/
    ├── constants.mjs   # Config, Jito endpoints, tip accounts
    ├── wallets.mjs     # Wallet generation
    ├── utils.mjs       # Helpers, blockhash manager, priority fees
    ├── tx.mjs          # Transaction building, pump.fun SDK integration
    ├── jito.mjs        # Jito bundle sending + status polling
    └── fund.mjs        # Wallet funding + draining
```

## Technical Notes

- Uses pump.fun V3 API via `@pump-fun/pump-sdk`
- Token-2022 compatible (600K compute units)
- Jito bundles sent to all 3 endpoints in parallel (mainnet, amsterdam, tokyo)
- Bundle status polling uses `getInflightBundleStatuses` with `getBundleStatuses` fallback
- Tip escalation: starts at 0.001 SOL, increases per retry up to 0.01 SOL
- Priority fees fetched from chain (p75) and cached for 10s

## Dependencies

- `@solana/web3.js` — Solana SDK
- `@solana/spl-token` — Token operations
- `@pump-fun/pump-sdk` — pump.fun bonding curve math + instructions
- `bn.js` — BigNumber for SDK compatibility
- `bs58` — Base58 encoding for keys
