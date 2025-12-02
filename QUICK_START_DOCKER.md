# Quick Start with Docker

The easiest way to run tests without installing dependencies locally.

## Prerequisites

- Docker installed
- Docker Compose installed

## Setup (One Time)

1. **Create root environment file:**
```bash
echo "THEGRAPH_API_KEY=your_jwt_token_here" > .env
echo "NEXT_PUBLIC_THEGRAPH_API_KEY=your_jwt_token_here" >> .env
echo "NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your_project_id_here" >> .env
```

Or copy the example:
```bash
cp .env.example .env
# Then edit .env with your API keys
```

2. **That's it!** No need to install Python, Node, or any dependencies.

## Run Tests

### All Tests
```bash
make docker-test
# or
docker compose -f docker-compose.test.yml run --rm test-all
```

### Specific Test Suite
```bash
# Ethereum tests
make docker-test-ethereum

# Polygon tests
make docker-test-polygon

# Base tests
make docker-test-base

# Unit tests (fast, no API key needed)
make docker-test-unit
```

### Custom Test Command
```bash
# Run specific test file
docker compose -f docker-compose.test.yml run --rm backend-test pytest tests/ethereum/test_balance_thegraph.py::TestEthereumNativeBalance::test_get_native_eth_balance_success -v

# Run with options
docker compose -f docker-compose.test.yml run --rm backend-test pytest tests/ -v -s --tb=short
```

## Advantages

✅ **No Local Setup**: No need to install Python, pip, or dependencies  
✅ **Consistent Environment**: Same Python version everywhere  
✅ **Isolated**: Tests run in isolated containers  
✅ **Easy Cleanup**: Remove containers when done  
✅ **CI/CD Ready**: Same setup works in pipelines  

## Troubleshooting

### "API Key Not Set"
- Ensure `.env` file exists in root directory with `THEGRAPH_API_KEY=your_key`

### "Cannot connect to Docker"
- Start Docker Desktop or Docker daemon
- Check: `docker ps`

### "Port already in use"
- Change port in `docker-compose.yml` if needed

### Clean Everything
```bash
make docker-clean
```

## More Information

See [DOCKER.md](DOCKER.md) for complete Docker documentation.
