# Polygon Balance Client Tests

This directory contains integration tests for the Polygon balance client using The Graph Token API.

## What These Tests Do

These tests verify that the Polygon balance client (`packages.blockchain.polygon.balance.balance_client_thegraph`) correctly fetches native MATIC and ERC-20 token balances from The Graph API.

## Test Structure

### Test Classes

1. **`TestPolygonNativeBalance`** - Tests for native MATIC balance fetching
2. **`TestPolygonTokenBalance`** - Tests for specific ERC-20 token balance fetching
3. **`TestPolygonMultipleTokenBalances`** - Tests for fetching all token balances

## Test Details

### 1. Native MATIC Balance Tests

#### `test_get_native_matic_balance_success`
- **What it tests**: Fetches native MATIC balance for a known address
- **What the code does**:
  1. Calls `get_native_matic_balance_thegraph()` with a test address
  2. Verifies the response structure:
     - `token_type` is "native"
     - `token_symbol` is "MATIC"
     - `chain_name` is "Polygon"
     - `chain_id` is "137"
     - `balance` (human-readable) and `balance_raw` (wei) are present
     - No error is returned
- **Expected result**: Returns valid MATIC balance with correct structure

#### `test_get_native_matic_balance_zero_address`
- **What it tests**: Fetches MATIC balance for the zero address (0x0000...)
- **What the code does**:
  1. Calls the function with the zero address (used as burn address)
  2. Verifies structure is correct (zero address can have balance)
  3. Ensures no error is returned (zero balance is valid)
- **Expected result**: Returns valid structure (balance may be non-zero)

### 2. Token Balance Tests

#### `test_get_token_balance_polygon_usdc`
- **What it tests**: Fetches USDC token balance on Polygon for a specific address
- **What the code does**:
  1. Calls `get_token_balance_polygon_thegraph()` with address and "USDC"
  2. If token found:
     - Verifies `token_type` is "ERC20"
     - Verifies `token_symbol` is "USDC"
     - Checks all required fields are present
  3. If token not found:
     - Verifies error structure is correct
- **Expected result**: Returns token balance or appropriate error
- **Note**: Includes 1-second delay to avoid rate limiting

### 3. Multiple Token Balance Tests

#### `test_get_multiple_token_balances_polygon_success`
- **What it tests**: Fetches ALL ERC-20 token balances for an address on Polygon
- **What the code does**:
  1. Calls `get_multiple_token_balances_polygon_thegraph()` with address
  2. Handles pagination (API returns 10 tokens per page)
  3. Verifies:
     - Returns list of tokens in `tokens` field
     - Each token has correct structure (`token_type`, `token_symbol`, `balance`, etc.)
     - No overall error
- **Expected result**: Returns all tokens (including zero balances) with correct structure
- **Note**: 
  - This test can be slow (60-120 seconds) due to pagination
  - Includes 2-second delay before test to avoid rate limiting
  - Uses `include_null_balances=true` to fetch all tokens (matches Polygonscan count)

## Test Addresses

- **`TEST_ADDRESS_WITH_BALANCE`**: `0xde881c6c4f469cca1dfc226dcdc98f98d5e17840`
  - Has ~79 ERC-20 tokens (including zero balances)
  - Has native MATIC balance
  - Used for most tests

- **`TEST_ADDRESS_ZERO`**: `0x0000000000000000000000000000000000000000`
  - Zero/burn address
  - Can have tokens and balance (used for burns)
  - Tests edge cases

## Running the Tests

### Prerequisites
- `THEGRAPH_API_KEY` must be set in root `.env` file (or `backend/.env` for local development)
- Python dependencies installed (`pip install -r requirements.txt`)

### Run All Polygon Tests
```bash
cd backend
pytest tests/polygon/ -v
```

### Run Specific Test
```bash
pytest tests/polygon/test_balance_thegraph.py::TestPolygonNativeBalance::test_get_native_matic_balance_success -v
```

### Run with Makefile
```bash
make test-polygon
```

## Test Performance

- **Fast tests** (1-2 seconds): Native balance tests
- **Slow tests** (60-120 seconds): Multiple token balance tests (due to pagination)
- **May skip**: Tests may skip if API is slow or rate-limited (timeouts set to prevent hanging)

## What to Expect

- ✅ **Passing tests**: All assertions pass, correct data structure returned
- ⏭️ **Skipped tests**: API timeout or rate limit (not a failure)
- ❌ **Failing tests**: Code bug or API error (check error message)

## Key Differences from Ethereum Tests

1. **Chain ID**: Uses "137" instead of "1"
2. **Native Token**: MATIC instead of ETH
3. **Network Name**: "polygon" in API calls
4. **Token Count**: Test address has ~79 tokens (more than Ethereum test address)

## Troubleshooting

### Tests Skipping
- Check API key is valid in root `.env` file (or `backend/.env`)
- Check API has credits remaining
- Wait a few minutes and retry (rate limiting)

### Tests Failing
- Verify API key is correct in root `.env` file
- Check network connectivity
- Review error messages in test output
- Check The Graph API status

### Token Count Mismatch
- The test uses `include_null_balances=true` to match Polygonscan
- Some tokens may have zero balances but are still returned
- This is expected behavior


