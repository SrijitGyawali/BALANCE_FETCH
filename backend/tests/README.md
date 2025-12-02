# Test Suite Overview

This directory contains the complete test suite for the balance fetching functionality using The Graph Token API.

## Test Structure

```
tests/
├── ethereum/          # Ethereum chain-specific integration tests (real API calls)
├── polygon/           # Polygon chain-specific integration tests (real API calls)
├── base/              # Base chain-specific integration tests (real API calls)
├── unit/              # Unit tests with real API calls
└── integration/       # A2A agent tool integration tests (removed for now)
```

## Test Types

### 1. Chain-Specific Integration Tests
**Location**: `tests/ethereum/`, `tests/polygon/`, `tests/base/`

- **Purpose**: Test real API integration for each blockchain network
- **API Calls**: ✅ Real API calls to The Graph API
- **Speed**: 🐌 Slow (1-120 seconds per test)
- **Requirements**: `THEGRAPH_API_KEY` in `.env` file
- **What they test**:
  - Native token balance fetching
  - ERC-20 token balance fetching
  - Multiple token balance fetching with pagination
  - Error handling with real API responses

**See individual README files in each directory for details.**

### 2. Unit Tests
**Location**: `tests/unit/`

- **Purpose**: Test core client functionality and all chains
- **API Calls**: ✅ Real API calls to The Graph API
- **Speed**: 🐌 Slow (1-120 seconds per test)
- **Requirements**: `THEGRAPH_API_KEY` in `.env` file
- **What they test**:
  - TheGraphClient core functionality
  - Native balance fetching (all chains)
  - Token balance fetching (all chains)
  - Pagination logic
  - Error handling with real API

**See `tests/unit/README.md` for details.**

### 3. Integration Tests
**Location**: `tests/integration/`

- **Status**: ⚠️ **Removed for now**
- **Reason**: Required `langchain` dependency not included
- **Future**: May be re-added when A2A integration is actively developed

**See `tests/integration/README.md` for details.**

## Running Tests

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test Type
```bash
# Chain-specific tests (real API calls)
pytest tests/ethereum/ -v
pytest tests/polygon/ -v
pytest tests/base/ -v

# Unit tests (real API calls)
pytest tests/unit/ -v

# Integration tests (removed for now)
# pytest tests/integration/ -v
```

### Run with Makefile
```bash
# All backend tests
make test-backend

# Specific chain tests
make test-ethereum
make test-polygon
make test-base

# Unit tests only
make test-unit

# All tests (chains + unit)
make test-all
```

## Test Performance

| Test Type | Speed | API Calls | API Key Required |
|-----------|-------|-----------|------------------|
| Chain Tests | 🐌 Slow (1-120s) | ✅ Real | ✅ Yes |
| Unit Tests | 🐌 Slow (1-120s) | ✅ Real | ✅ Yes |
| Integration Tests | ⚠️ Removed | - | - |

## Test Addresses

### Ethereum
- **With Balance**: `0x1fA33c1CA2d733C895BeFf7a3d468Cee317Be253` (~49 tokens)
- **Zero Address**: `0x0000000000000000000000000000000000000000` (burn address)

### Polygon
- **With Balance**: `0xde881c6c4f469cca1dfc226dcdc98f98d5e17840` (~79 tokens)
- **Zero Address**: `0x0000000000000000000000000000000000000000` (burn address)

### Base
- **With Balance**: `0x5DE176348c089B9709bAF01C5d0EDBbb82f2A8A6` (~6 tokens)
- **Zero Address**: `0x0000000000000000000000000000000000000000` (burn address)

## What to Expect

### ✅ Passing Tests
- All assertions pass
- Correct data structure returned
- No errors in output

### ⏭️ Skipped Tests
- API timeout (tests have timeouts to prevent hanging)
- Rate limiting (API may be slow)
- Missing API key (for chain tests)
- **Note**: Skipped tests are NOT failures

### ❌ Failing Tests
- Code bug
- API error
- Incorrect assertions
- **Action**: Check error message and fix issue

## Prerequisites

### For Chain Tests (Real API Calls)
1. `THEGRAPH_API_KEY` in root `.env` file (or `backend/.env` for local development)
2. Valid API key with credits
3. Network connectivity

### For Unit Tests (Real API Calls)
1. `THEGRAPH_API_KEY` in root `.env` file (or `backend/.env` for local development)
2. Valid API key with credits
3. Network connectivity

## Troubleshooting

### Tests Skipping
- **Chain tests**: Check API key is set and valid
- **All tests**: Check API has credits remaining
- Wait a few minutes and retry (rate limiting)

### Tests Failing
- Review error messages in test output
- Check API key is correct
- Verify network connectivity
- Check The Graph API status

### Import Errors
- Ensure you're running from `backend/` directory
- Check `pythonpath` in `pytest.ini`
- Verify directory structure

## Test Coverage

- ✅ Native token balance fetching (all chains)
- ✅ ERC-20 token balance fetching (all chains)
- ✅ Multiple token balance fetching with pagination
- ✅ Error handling (401, 429, network errors)
- ✅ Data structure validation
- ⚠️ A2A agent tool integration (tests removed for now)
- ✅ Edge cases (zero address, missing API key, etc.)

## Best Practices

1. **Run unit tests first** (fast, no API key needed)
2. **Run chain tests when needed** (slow, requires API key)
3. **Check skipped tests** (may indicate API issues)
4. **Review error messages** (helpful for debugging)
5. **Use Makefile commands** (simpler than direct pytest)

## Additional Resources

- **Ethereum Tests**: See `tests/ethereum/README.md`
- **Polygon Tests**: See `tests/polygon/README.md`
- **Base Tests**: See `tests/base/README.md`
- **Unit Tests**: See `tests/unit/README.md`
- **Integration Tests**: See `tests/integration/README.md`


