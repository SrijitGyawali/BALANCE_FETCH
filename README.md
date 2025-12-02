# Get Balance - Multi-Chain Token Balance Viewer

A full-stack application for viewing token balances across multiple blockchain networks (Ethereum, Polygon, Base) using The Graph Token API.

## Project Structure

```
GET_BALANCE/
├── frontend/          # Next.js web application (UI)
├── backend/           # Python A2A integration (balance clients & tests)
└── Makefile          # Build and test automation
```

## Quick Start

### Frontend (UI)

```bash
cd frontend
npm install
cp .env.example .env.local  # Add your API keys
npm run dev
```

Visit http://localhost:3000

### Backend (Python)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your API key
pytest tests/ -v
```

## Features

### Frontend
- 🔗 Wallet connection (MetaMask, WalletConnect, etc.)
- 💰 Multi-chain token balance display
- 🔍 Address checker for any Ethereum address
- 📊 Real-time USD value calculations
- 🎨 Modern, responsive UI

### Backend
- 🔗 Multi-chain balance clients (Ethereum, Polygon, Base)
- 💰 Native and ERC-20 token balance fetching
- 🧪 Comprehensive test suite
- ⚡ Async/await support
- 🔍 CLI tool for testing

## Prerequisites

- **Node.js 18+** (for frontend)
- **Python 3.10+** (for backend)
- **The Graph API Key** - [Get one here](https://thegraph.com/studio/apikeys/)
- **Reown Project ID** - [Get one here](https://dashboard.reown.com) (for frontend wallet connection)

## Setup

### 1. Create Root Environment File

Create `.env` in the root directory:
```env
# The Graph API Key (used by both frontend and backend)
THEGRAPH_API_KEY=your_jwt_token_here
NEXT_PUBLIC_THEGRAPH_API_KEY=your_jwt_token_here

# WalletConnect / Reown Project ID (for frontend)
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your_project_id_here
```

Or copy the example:
```bash
cp .env.example .env
# Then edit .env with your API keys
```

### 2. Frontend Setup (Optional - for local development)

```bash
cd frontend
npm install
```

### 3. Backend Setup (Optional - for local development)

```bash
cd backend
pip install -r requirements.txt
```

## Usage

### Frontend

```bash
cd frontend
npm run dev
```

### Backend

```bash
cd backend

# Run tests
pytest tests/ -v

# Use CLI tool
python test_balance_cli.py ethereum 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

## Makefile Commands

From the root directory:

```bash
make install          # Install all dependencies (frontend + backend)
make dev              # Run frontend development server
make test             # Run all backend tests
make test-ethereum    # Run Ethereum tests
make test-polygon     # Run Polygon tests
make test-base        # Run Base tests
make clean            # Clean build artifacts
```

See `make help` for all available commands.

## Docker Setup (Recommended)

Docker makes it easy to run tests without installing dependencies locally.

### Quick Start with Docker

```bash
# Run all tests in Docker
make docker-test

# Run specific test suite
make docker-test-ethereum
make docker-test-polygon
make docker-test-base
make docker-test-unit

# Start frontend in Docker
make docker-dev
```

### Docker Commands

```bash
# Build Docker images
make docker-build

# Run all tests
docker-compose -f docker-compose.test.yml run --rm test-all

# Run specific tests
docker-compose -f docker-compose.test.yml run --rm test-ethereum
docker-compose -f docker-compose.test.yml run --rm test-unit

# Clean up
make docker-clean
```

See [DOCKER.md](DOCKER.md) for detailed Docker documentation.

## Supported Networks

- **Ethereum** (Mainnet) - Chain ID: 1
- **Polygon** - Chain ID: 137
- **Base** - Chain ID: 8453

## Documentation

- **Frontend**: See `frontend/README.md`
- **Backend**: See `backend/README.md`

## License

MIT
