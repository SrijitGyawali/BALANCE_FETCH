# Base Balance Client Tests

This directory contains integration tests for the Base balance client using The Graph Token API.

## What These Tests Do

These tests verify that the Base balance client (`packages.blockchain.base.balance.balance_client_thegraph`) correctly fetches native ETH (on Base) and ERC-20 token balances from The Graph API.

## Test Structure

### Test Classes

1. **`TestBaseNativeBalance`** - Tests for native Base ETH balance fetching
2. **`TestBaseTokenBalance`** - Tests for specific ERC-20 token balance fetching
3. **`TestBaseMultipleTokenBalances`** - Tests for fetching all token balances

## Test Details

### 1. Native Base ETH Balance Tests

#### `test_get_native_base_balance_success`
- **What it tests**: Fetches native ETH balance on Base for a known address
- **What the code does**:
  1. Calls `get_native_base_balance_thegraph()` with a test address
  2. Verifies the response structure:
     - `token_type` is "native"
     - `token_symbol` is "ETH" (Base uses ETH as native token)
     - `chain_name` is "Base"
     - `chain_id` is "8453"
     - `balance` (human-readable) and `balance_raw` (wei) are present
     - No error is returned
- **Expected result**: Returns valid ETH balance with correct structure

#### `test_get_native_base_balance_zero_address`
- **What it tests**: Fetches Base ETH balance for the zero address (0x0000...)
- **What the code does**:
  1. Calls the function with the zero address (used as burn address)
  2. Verifies structure is correct (zero address can have balance)
  3. Ensures no error is returned (zero balance is valid)
- **Expected result**: Returns valid structure (balance may be non-zero as zero address accumulates tokens)

### 2. Token Balance Tests

#### `test_get_token_balance_base_usdc`
- **What it tests**: Fetches USDC token balance on Base for a specific address
- **What the code does**:
  1. Calls `get_token_balance_base_thegraph()` with address and "USDC"
  2. Includes 1-second delay to avoid rate limiting
  3. Uses 60-second timeout to prevent hanging
  4. If token found:
     - Verifies `token_type` is "ERC20"
     - Verifies `token_symbol` is "USDC"
     - Checks all required fields are present
  5. If token not found:
     - Verifies error structure is correct
- **Expected result**: Returns token balance or appropriate error
- **Note**: May skip if API is slow or rate-limited

### 3. Multiple Token Balance Tests

#### `test_get_multiple_token_balances_base_success`
- **What it tests**: Fetches ALL ERC-20 token balances for an address on Base
- **What the code does**:
  1. Calls `get_multiple_token_balances_base_thegraph()` with address
  2. Includes 2-second delay before test to avoid rate limiting
  3. Uses 120-second timeout to prevent hanging
  4. Handles pagination (API returns 10 tokens per page)
  5. Verifies:
     - Returns list of tokens in `tokens` field
     - Each token has correct structure
     - No overall error
- **Expected result**: Returns all tokens with correct structure
- **Note**: This test can be slow (60-120 seconds) due to pagination

## Test Addresses

- **`TEST_ADDRESS_WITH_BALANCE`**: `0x5DE176348c089B9709bAF01C5d0EDBbb82f2A8A6`
  - Has ~6 ERC-20 tokens
  - Has native Base ETH balance
  - Used for most tests

- **`TEST_ADDRESS_ZERO`**: `0x0000000000000000000000000000000000000000`
  - Zero/burn address
  - Can have tokens and balance (used for burns)
  - Tests edge cases

## Running the Tests

### Prerequisites
- `THEGRAPH_API_KEY` must be set in root `.env` file (or `backend/.env` for local development)
- Python dependencies installed (`pip install -r requirements.txt`)

### Run All Base Tests
```bash
cd backend
pytest tests/base/ -v
```

### Run Specific Test
```bash
pytest tests/base/test_balance_thegraph.py::TestBaseNativeBalance::test_get_native_base_balance_success -v
```

### Run with Makefile
```bash
make test-base
```

## Test Performance

- **Fast tests** (1-2 seconds): Native balance tests
- **Slow tests** (60-120 seconds): Multiple token balance tests (due to pagination)
- **May skip**: Tests may skip if API is slow or rate-limited (timeouts set to prevent hanging)

## What to Expect

- ✅ **Passing tests**: All assertions pass, correct data structure returned
- ⏭️ **Skipped tests**: API timeout or rate limit (not a failure)
- ❌ **Failing tests**: Code bug or API error (check error message)

## Key Differences from Ethereum/Polygon Tests

1. **Chain ID**: Uses "8453" instead of "1" or "137"
2. **Native Token**: ETH (same as Ethereum, but on Base network)
3. **Network Name**: "base" in API calls
4. **Token Count**: Test address has fewer tokens (~6) than Ethereum/Polygon test addresses

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

### Missing `token_type` Field
- Ensure error cases return proper structure with `token_type`, `chain_name`, and `chain_id`
- Check that `get_token_balance_base_thegraph` handles all return paths correctly


