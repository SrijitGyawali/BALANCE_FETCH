# Unit Tests

This directory contains unit tests for The Graph API client and balance clients. These tests make **real API calls** to The Graph API.

## What These Tests Do

These tests verify the functionality of the balance clients by making **real API calls** to The Graph API, similar to the chain-specific integration tests.

## Test Files

### `test_thegraph_client.py`
- **What it tests**: Core `TheGraphClient` class functionality
- **What the code does**:
  - Mocks HTTP responses using `unittest.mock`
  - Tests client initialization
  - Tests native balance parsing
  - Tests token balance parsing
  - Tests error handling (401, 429, network errors)
  - Tests pagination logic
- **Why it's fast**: No real API calls, all responses are mocked

### `test_ethereum_balance_thegraph.py`
- **What it tests**: Ethereum-specific balance client functions
- **What the code does**:
  - Mocks The Graph API responses
  - Tests `get_native_eth_balance_thegraph()` with various scenarios
  - Tests `get_token_balance_ethereum_thegraph()` with mocked responses
  - Tests error handling and edge cases
- **Why it's fast**: No real API calls

### `test_polygon_balance_thegraph.py`
- **What it tests**: Polygon-specific balance client functions
- **What the code does**:
  - Similar to Ethereum tests but for Polygon network
  - Tests MATIC balance fetching
  - Tests token balance fetching on Polygon
- **Why it's fast**: No real API calls

### `test_base_balance_thegraph.py`
- **What it tests**: Base-specific balance client functions
- **What the code does**:
  - Similar to Ethereum/Polygon tests but for Base network
  - Tests Base ETH balance fetching
  - Tests token balance fetching on Base
- **Why it's fast**: No real API calls

## How Unit Tests Work

### Real API Calls

These tests make real API calls to The Graph API, similar to the chain-specific integration tests:

```python
# Example: Real API call
async def test_get_native_balance_success(self, client, api_key):
    result = await client.get_native_balance(
        TEST_ADDRESS_WITH_BALANCE, "ethereum"
    )
    
    # Assert the result from real API
    assert result is not None
    assert result.chain_id == "1"
    assert result.symbol == "ETH"
```

### What Gets Tested

1. **Real API Integration**: Verifies clients work with actual The Graph API
2. **Data Parsing**: Verifies API responses are correctly parsed into our data models
3. **Error Handling**: Tests how errors (401, 429, network errors) are handled with real API
4. **Structure Validation**: Ensures return dictionaries have correct fields
5. **Multi-Chain Support**: Tests Ethereum, Polygon, and Base networks
6. **Pagination**: Tests pagination logic with real multi-page responses

## Running the Tests

### Prerequisites
- `THEGRAPH_API_KEY` must be set in root `.env` file (or `backend/.env` for local development)
- Python dependencies installed (`pip install -r requirements.txt`)

### Run All Unit Tests
```bash
cd backend
pytest tests/unit/ -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_thegraph_client.py -v
```

### Run with Makefile
```bash
make test-unit
```

## Test Performance

- **Fast tests** (1-2 seconds): Native balance tests
- **Slow tests** (60-120 seconds): Multiple token balance tests (due to pagination)
- **May skip**: Tests may skip if API is slow or rate-limited (timeouts set to prevent hanging)

## What to Expect

- ✅ **Passing tests**: All assertions pass, real API responses handled correctly
- ⏭️ **Skipped tests**: API timeout or rate limit (not a failure)
- ❌ **Failing tests**: Code bug or API error (check error message)

## Unit Tests vs Chain-Specific Tests

| Aspect | Unit Tests | Chain-Specific Tests |
|--------|-----------|---------------------|
| **Location** | `tests/unit/` | `tests/ethereum/`, `tests/polygon/`, `tests/base/` |
| **API Calls** | ✅ Real API calls | ✅ Real API calls |
| **Speed** | 🐌 Slow (1-120s) | 🐌 Slow (1-120s) |
| **API Key** | ✅ Required | ✅ Required |
| **Purpose** | Test core client & all chains | Test chain-specific clients |
| **Focus** | TheGraphClient class | Chain-specific balance functions |

## Troubleshooting

### Tests Failing
- Check mock setup is correct
- Verify expected data structure matches actual code
- Review assertion statements

### Import Errors
- Ensure you're running from `backend/` directory
- Check `pythonpath` in `pytest.ini`
- Verify `packages/` directory structure


