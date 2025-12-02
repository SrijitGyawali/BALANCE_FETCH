# Docker Setup Guide

This guide explains how to use Docker to run tests and the application easily.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose (included with Docker Desktop, or use `docker compose` command)

**Note**: Modern Docker includes Compose V2. Use `docker compose` (with space) or `docker-compose` (with hyphen) - both work.

## Quick Start

### 1. Setup Environment Variables

Create a single `.env` file in the root directory:

**Root** (`.env`):
```env
THEGRAPH_API_KEY=your_jwt_token_here
NEXT_PUBLIC_THEGRAPH_API_KEY=your_jwt_token_here
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your_project_id_here
```

Or copy the example:
```bash
cp .env.example .env
# Then edit .env with your API keys
```

### 2. Run Tests

#### Run All Tests
```bash
# Using docker compose (V2 - recommended)
docker compose -f docker-compose.test.yml run --rm test-all

# Or using docker-compose (V1 - if installed separately)
docker-compose -f docker-compose.test.yml run --rm test-all
```

#### Run Specific Test Suite
```bash
# Ethereum tests
docker compose -f docker-compose.test.yml run --rm test-ethereum

# Polygon tests
docker compose -f docker-compose.test.yml run --rm test-polygon

# Base tests
docker compose -f docker-compose.test.yml run --rm test-base

# Unit tests
docker compose -f docker-compose.test.yml run --rm test-unit

# Integration tests
docker compose -f docker-compose.test.yml run --rm test-integration
```

#### Run Custom Test Command
```bash
# Run specific test file
docker compose -f docker-compose.test.yml run --rm backend-test pytest tests/ethereum/test_balance_thegraph.py -v

# Run with specific options
docker compose -f docker-compose.test.yml run --rm backend-test pytest tests/ -v -s --tb=short
```

**Note**: Replace `docker compose` with `docker-compose` if you have the standalone version installed.

## Docker Commands

### Build Images

```bash
# Build backend image
docker-compose -f docker-compose.test.yml build backend-test

# Build all images
docker-compose build
```

### Run Tests Interactively

```bash
# Start container and get shell access
docker-compose -f docker-compose.test.yml run --rm backend-test /bin/bash

# Then run tests manually inside container
pytest tests/ethereum/ -v
```

### View Test Output

```bash
# Run tests and see output in real-time
docker-compose -f docker-compose.test.yml run --rm test-all

# Run tests with verbose output
docker-compose -f docker-compose.test.yml run --rm backend-test pytest tests/ -v -s
```

### Clean Up

```bash
# Remove containers
docker-compose -f docker-compose.test.yml down

# Remove containers and volumes
docker-compose -f docker-compose.test.yml down -v

# Remove images
docker-compose -f docker-compose.test.yml down --rmi all
```

## Development Setup

### Run Frontend in Docker

```bash
# Start frontend development server
docker-compose up frontend

# Or in detached mode
docker-compose up -d frontend
```

Visit http://localhost:3000

### Run Both Frontend and Backend

```bash
# Start both services
docker-compose up

# Or in detached mode
docker-compose up -d
```

## Docker Compose Files

### `docker-compose.yml`
Main compose file for development:
- `backend`: Backend service for tests
- `frontend`: Frontend development server

### `docker-compose.test.yml`
Test-specific compose file:
- `backend-test`: Base test service
- `test-all`: Run all tests
- `test-ethereum`: Run Ethereum tests
- `test-polygon`: Run Polygon tests
- `test-base`: Run Base tests
- `test-unit`: Run unit tests
- `test-integration`: Run integration tests

## Environment Variables

### Backend
- `THEGRAPH_API_KEY`: The Graph API JWT token (required for chain tests)

### Frontend
- `NEXT_PUBLIC_THEGRAPH_API_KEY`: The Graph API JWT token
- `NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID`: Reown/WalletConnect project ID

### Using Environment Variables

```bash
# Pass environment variable directly
THEGRAPH_API_KEY=your_key docker compose -f docker-compose.test.yml run --rm test-all

# Or use .env file (recommended)
# Create .env in root directory with THEGRAPH_API_KEY=your_key
```

## Troubleshooting

### Tests Failing with "API Key Not Set"
- Ensure `.env` file exists in root directory with `THEGRAPH_API_KEY`
- Or pass environment variable: `THEGRAPH_API_KEY=key docker compose ...`

### Permission Errors
```bash
# Fix permissions (Linux/Mac)
sudo chown -R $USER:$USER backend/ frontend/
```

### Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.test.yml logs backend-test

# Rebuild image
docker-compose -f docker-compose.test.yml build --no-cache backend-test
```

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "3001:3000"  # Use port 3001 instead
```

### Clean Everything and Start Fresh
```bash
# Stop and remove everything
docker-compose down -v
docker-compose -f docker-compose.test.yml down -v

# Remove all images
docker rmi $(docker images -q get-balance*)

# Rebuild
docker-compose -f docker-compose.test.yml build --no-cache
```

## Advantages of Docker

1. **Consistent Environment**: Same Python/Node versions across all machines
2. **No Local Setup**: No need to install Python, Node, or dependencies locally
3. **Isolated**: Tests run in isolated containers
4. **Easy Cleanup**: Remove containers when done
5. **CI/CD Ready**: Same setup works in CI/CD pipelines

## Example Workflows

### Daily Testing
```bash
# Quick test run
docker-compose -f docker-compose.test.yml run --rm test-unit

# Full test suite
docker-compose -f docker-compose.test.yml run --rm test-all
```

### Development
```bash
# Start frontend
docker-compose up frontend

# In another terminal, run tests
docker-compose -f docker-compose.test.yml run --rm test-ethereum
```

### CI/CD Pipeline
```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    docker-compose -f docker-compose.test.yml build
    docker-compose -f docker-compose.test.yml run --rm test-all
```

## Makefile Integration

You can also use Makefile commands that use Docker:

```bash
# Add to Makefile (optional)
test-docker:
	docker-compose -f docker-compose.test.yml run --rm test-all

test-ethereum-docker:
	docker-compose -f docker-compose.test.yml run --rm test-ethereum
```

## Best Practices

1. **Use .env files**: Store API keys in `.env` files (not committed to git)
2. **Clean up regularly**: Remove unused containers and images
3. **Rebuild when needed**: Rebuild images when dependencies change
4. **Use volumes**: Code changes are reflected immediately (volumes mounted)
5. **Check logs**: Use `docker-compose logs` to debug issues

