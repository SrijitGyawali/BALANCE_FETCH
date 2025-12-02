# Frontend - Wallet Token Balances UI

A Next.js web3 application that displays all ERC-20 token balances for a connected Ethereum wallet using wagmi, Reown AppKit, and The Graph Token API.

## Features

- 🔗 Wallet connection using wagmi and Reown AppKit
- 💰 Display all ERC-20 token holdings across multiple chains
- 💵 Calculate total USD value of holdings
- 📊 Beautiful, responsive UI
- ⚡ Real-time balance fetching
- 🌐 Support for 500+ wallets via WalletConnect
- 🔍 Address checker to view any address's balances

## Prerequisites

- Node.js 18+ and npm/yarn
- The Graph API key ([Get one here](https://thegraph.com/studio/apikeys/)) - Free tier available ($25/month credit)
- Reown Project ID ([Get one here](https://dashboard.reown.com)) - Required for wallet connections

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create a `.env.local` file in the `frontend/` directory, OR use the root `.env` file:

**Option 1: Use root `.env` file (recommended for Docker)**
```env
# In root directory .env file
NEXT_PUBLIC_THEGRAPH_API_KEY=YourTheGraphApiToken
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=YOUR_REOWN_PROJECT_ID
```

**Option 2: Use frontend-specific `.env.local` file**
```env
# In frontend/.env.local file
NEXT_PUBLIC_THEGRAPH_API_KEY=YourTheGraphApiToken
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=YOUR_REOWN_PROJECT_ID
```

**Important**: 
- Use the **API TOKEN (Authentication JWT)** from The Graph dashboard, not the API Key.
- For Next.js client-side components, use `NEXT_PUBLIC_THEGRAPH_API_KEY` (required)
- If using Docker, the root `.env` file will be used automatically

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Run development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with wagmi config
│   ├── page.tsx            # Main page component
│   └── globals.css         # Global styles
├── components/
│   ├── wallet-connect.tsx  # Wallet connection component
│   ├── token-balances.tsx   # Token balances display component
│   └── address-checker.tsx  # Address balance checker component
├── lib/
│   ├── wagmi-config.tsx    # Wagmi configuration
│   ├── thegraph-api.ts     # The Graph Token API service
│   └── env-utils.ts        # Environment variable utilities
├── package.json
└── tsconfig.json
```

## Supported Chains

- Ethereum (Mainnet)
- Polygon
- Base

## Technologies

- **Next.js 14** - React framework
- **wagmi** - React Hooks for Ethereum
- **Reown AppKit** - Wallet connection SDK (formerly WalletConnect)
- **viem** - TypeScript Ethereum library
- **TypeScript** - Type safety
- **The Graph Token API** - Token balance data

## API Reference

This app uses **The Graph Token API**:

- **Free tier**: $25/month credit, 10 items per query, 200 requests/minute
- **Endpoints**:
  - `/v1/evm/balances` - ERC-20 token balances
  - `/v1/evm/balances/native` - Native token balances
- **Documentation**: [The Graph Token API](https://thegraph.com/docs/en/token-api/)

## Troubleshooting

### Wallet Connection Issues
- Ensure `NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID` is set correctly
- Check browser console for errors
- Try refreshing the page

### Balance Fetching Issues
- Verify `NEXT_PUBLIC_THEGRAPH_API_KEY` is set correctly
- Check API key is valid and has credits
- Check browser console for API errors

### Build Issues
- Delete `.next` folder and rebuild: `rm -rf .next && npm run build`
- Clear node_modules: `rm -rf node_modules && npm install`


