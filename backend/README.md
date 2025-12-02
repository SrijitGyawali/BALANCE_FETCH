# Backend - The Graph API Balance Client (A2A Integration)

Python backend for fetching token and native balances across multiple blockchain networks using The Graph Token API. Designed for integration with A2A (Agent-to-Agent) applications.

## Features

- 🔗 Multi-chain support (Ethereum, Polygon, Base)
- 💰 Native token balance fetching
- 🪙 ERC-20 token balance fetching (single and multiple)
- 📊 Chain-specific balance clients
- 🧪 Comprehensive test suite
- ⚡ Async/await support
- 🔍 CLI tool for testing

## Prerequisites

- Python 3.10+
- pip
- The Graph API key ([Get one here](https://thegraph.com/studio/apikeys/)) - Free tier available ($25/month credit)

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory (or `backend/.env` for local development):

**Option 1: Use root `.env` file (recommended for Docker)**
```env
# In root directory .env file
THEGRAPH_API_KEY=your_jwt_token_here
```

**Option 2: Use backend-specific `.env` file**
```env
# In backend/.env file
THEGRAPH_API_KEY=your_jwt_token_here
```

**Important**: 
- Use the **API TOKEN (Authentication JWT)** from The Graph dashboard.
- If using Docker, the root `.env` file will be used automatically.
- For local development, either location works (root `.env` takes precedence if both exist).

## Project Structure

```
backend/
├── packages/
│   └── blockchain/
│       ├── ethereum/
│       │   └── balance/
│       │       └── balance_client_thegraph.py
│       ├── polygon/
│       │   └── balance/
│       │       └── balance_client_thegraph.py
│       ├── base/
│       │   └── balance/
│       │       └── balance_client_thegraph.py
│       └── thegraph/
│           ├── client.py          # Core The Graph API client
│           ├── models.py          # Pydantic data models
│           └── utils.py           # Utility functions
├── agents/
│   └── balance/
│       └── agent_integration_example.py  # A2A integration example
├── tests/
│   ├── ethereum/                 # Ethereum-specific tests
│   ├── polygon/                   # Polygon-specific tests
│   ├── base/                      # Base-specific tests
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── test_balance_cli.py           # CLI tool for testing
├── requirements.txt
└── pytest.ini
```

## Usage

### Python API

```python
from packages.blockchain.ethereum.balance.balance_client_thegraph import (
    get_native_eth_balance_thegraph,
    get_token_balance_ethereum_thegraph,
    get_multiple_token_balances_ethereum_thegraph,
)

# Get native ETH balance
result = await get_native_eth_balance_thegraph(
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    api_key="your_jwt_token"
)

# Get specific token balance
result = await get_token_balance_ethereum_thegraph(
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "USDC",
    api_key="your_jwt_token"
)

# Get all token balances
result = await get_multiple_token_balances_ethereum_thegraph(
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    api_key="your_jwt_token"
)
```

### CLI Tool

```bash
# Test native balance
python test_balance_cli.py ethereum 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

# Test specific token
python test_balance_cli.py ethereum 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb --token USDC

# Test all tokens
python test_balance_cli.py ethereum 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb --all-tokens
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Chain-Specific Tests

```bash
# Ethereum tests
pytest tests/ethereum/ -v

# Polygon tests
pytest tests/polygon/ -v

# Base tests
pytest tests/base/ -v
```

### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

## Supported Networks

- **Ethereum** (Chain ID: 1)
- **Polygon** (Chain ID: 137)
- **Base** (Chain ID: 8453)

## API Reference

### The Graph Token API

- **Base URL**: `https://token-api.thegraph.com/v1/evm`
- **Endpoints**:
  - `/balances/native` - Native token balances
  - `/balances` - ERC-20 token balances
- **Authentication**: Bearer token (JWT)
- **Rate Limits**: 200 requests/minute (free tier)

## Dependencies

- `httpx` - Async HTTP client
- `pydantic` - Data validation
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `python-dotenv` - Environment variable loading

## A2A Integration

See `agents/balance/agent_integration_example.py` for examples of integrating these balance clients into your A2A agent tools.

## Troubleshooting

### Import Errors
- Ensure you're running from the `backend/` directory
- Check that `packages/` directory is in Python path
- Verify all `__init__.py` files exist

### API Errors
- Verify `THEGRAPH_API_KEY` is set in `.env` file
- Check API key is valid and has credits
- Review rate limits (200 requests/minute)

### Test Failures
- Ensure `.env` file exists with valid API key
- Check network connectivity
- Some tests may skip if API is slow (this is expected)


