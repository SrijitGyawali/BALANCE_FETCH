# Ethereum Balance Client Tests

This directory contains integration tests for the Ethereum balance client using The Graph Token API.

## What These Tests Do

These tests verify that the Ethereum balance client (`packages.blockchain.ethereum.balance.balance_client_thegraph`) correctly fetches native ETH and ERC-20 token balances from The Graph API.

## Test Structure

### Test Classes

1. **`TestEthereumNativeBalance`** - Tests for native ETH balance fetching
2. **`TestEthereumTokenBalance`** - Tests for specific ERC-20 token balance fetching
3. **`TestEthereumMultipleTokenBalances`** - Tests for fetching all token balances

## Test Details

### 1. Native ETH Balance Tests

#### `test_get_native_eth_balance_success`
- **What it tests**: Fetches native ETH balance for a known address
- **What the code does**:
  1. Calls `get_native_eth_balance_thegraph()` with a test address
  2. Verifies the response structure:
     - `token_type` is "native"
     - `token_symbol` is "ETH"
     - `chain_name` is "Ethereum"
     - `chain_id` is "1"
     - `balance` (human-readable) and `balance_raw` (wei) are present
     - No error is returned
- **Expected result**: Returns valid ETH balance with correct structure

#### `test_get_native_eth_balance_zero_address`
- **What it tests**: Fetches ETH balance for the zero address (0x0000...)
- **What the code does**:
  1. Calls the function with the zero address (used as burn address)
  2. Verifies structure is correct (zero address can have balance)
  3. Ensures no error is returned (zero balance is valid)
- **Expected result**: Returns valid structure (balance may be non-zero as zero address accumulates tokens)

#### `test_get_native_eth_balance_no_api_key`
- **What it tests**: Error handling when API key is missing
- **What the code does**:
  1. Temporarily removes `THEGRAPH_API_KEY` from environment
  2. Calls the function without API key
  3. Verifies error message mentions "THEGRAPH_API_KEY"
- **Expected result**: Returns error dictionary with appropriate error message

### 2. Token Balance Tests

#### `test_get_token_balance_ethereum_usdc`
- **What it tests**: Fetches USDC token balance for a specific address
- **What the code does**:
  1. Calls `get_token_balance_ethereum_thegraph()` with address and "USDC"
  2. If token found:
     - Verifies `token_type` is "ERC20"
     - Verifies `token_symbol` is "USDC"
     - Checks all required fields are present
  3. If token not found:
     - Verifies error structure is correct
- **Expected result**: Returns token balance or appropriate error

#### `test_get_token_balance_ethereum_unknown_token`
- **What it tests**: Error handling for unknown token symbols
- **What the code does**:
  1. Calls function with a non-existent token symbol
  2. Verifies error message indicates token not found
  3. Checks error structure includes `token_type` and `token_symbol`
- **Expected result**: Returns error dictionary with "not found" message

### 3. Multiple Token Balance Tests

#### `test_get_multiple_token_balances_ethereum_success`
- **What it tests**: Fetches ALL ERC-20 token balances for an address
- **What the code does**:
  1. Calls `get_multiple_token_balances_ethereum_thegraph()` with address
  2. Handles pagination (API returns 10 tokens per page)
  3. Verifies:
     - Returns list of tokens in `tokens` field
     - Each token has correct structure
     - No overall error
- **Expected result**: Returns all tokens with correct structure
- **Note**: This test can be slow (60-120 seconds) due to pagination

#### `test_get_multiple_token_balances_ethereum_with_filter`
- **What it tests**: Fetches filtered token balances (USDC and USDT only)
- **What the code does**:
  1. Calls function with `token_symbols=["USDC", "USDT"]`
  2. Verifies only USDC/USDT tokens are returned
  3. Checks each token structure
- **Expected result**: Returns only filtered tokens

#### `test_get_multiple_token_balances_ethereum_zero_address`
- **What it tests**: Fetches tokens for zero address (burn address)
- **What the code does**:
  1. Calls function with zero address
  2. Verifies structure (zero address can have tokens)
  3. Checks tokens list (may be empty or contain tokens)
- **Expected result**: Returns valid structure (may have tokens as zero address is used for burns)

## Test Addresses

- **`TEST_ADDRESS_WITH_BALANCE`**: `0x1fA33c1CA2d733C895BeFf7a3d468Cee317Be253`
  - Has ~49 ERC-20 tokens
  - Has native ETH balance
  - Used for most tests

- **`TEST_ADDRESS_ZERO`**: `0x0000000000000000000000000000000000000000`
  - Zero/burn address
  - Can have tokens and balance (used for burns)
  - Tests edge cases

## Running the Tests

### Prerequisites
- `THEGRAPH_API_KEY` must be set in root `.env` file (or `backend/.env` for local development)
- Python dependencies installed (`pip install -r requirements.txt`)

### Run All Ethereum Tests
```bash
cd backend
pytest tests/ethereum/ -v
```

### Run Specific Test
```bash
pytest tests/ethereum/test_balance_thegraph.py::TestEthereumNativeBalance::test_get_native_eth_balance_success -v
```

### Run with Makefile
```bash
make test-ethereum
```

## Test Performance

- **Fast tests** (1-2 seconds): Native balance tests
- **Slow tests** (60-120 seconds): Multiple token balance tests (due to pagination)
- **May skip**: Tests may skip if API is slow or rate-limited (timeouts set to prevent hanging)

## What to Expect

- ✅ **Passing tests**: All assertions pass, correct data structure returned
- ⏭️ **Skipped tests**: API timeout or rate limit (not a failure)
- ❌ **Failing tests**: Code bug or API error (check error message)

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


