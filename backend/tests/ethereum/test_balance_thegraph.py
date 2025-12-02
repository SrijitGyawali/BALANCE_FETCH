"""
Tests for Ethereum balance client using The Graph API.

These tests make real API calls to The Graph API.
Requires THEGRAPH_API_KEY environment variable to be set (can be in .env file).
"""

import pytest
import os
from dotenv import load_dotenv
from packages.blockchain.ethereum.balance.balance_client_thegraph import (
    get_native_eth_balance_thegraph,
    get_token_balance_ethereum_thegraph,
    get_multiple_token_balances_ethereum_thegraph,
)

# Load environment variables from .env file
load_dotenv()

# Test addresses with known balances
TEST_ADDRESS_WITH_BALANCE = "0x1fA33c1CA2d733C895BeFf7a3d468Cee317Be253"
TEST_ADDRESS_ZERO = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module")
def api_key():
    """Get API key from environment."""
    key = os.getenv("THEGRAPH_API_KEY")
    if not key:
        pytest.skip("THEGRAPH_API_KEY environment variable not set")
    return key


@pytest.fixture(scope="module")
def test_address():
    """Test address with known balance."""
    return TEST_ADDRESS_WITH_BALANCE


class TestEthereumNativeBalance:
    """Tests for Ethereum native balance fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_native_eth_balance_success(self, api_key, test_address):
        """Test successful ETH balance fetch with real API."""
        result = await get_native_eth_balance_thegraph(test_address, api_key)

        assert result is not None
        assert "error" not in result or result.get("error") is None
        # Check actual return structure from the implementation
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["token_address"] == "0x0"
        assert result["chain_name"] == "Ethereum"
        assert result["chain_id"] == "1"
        assert "balance" in result  # Human-readable balance (string)
        assert "balance_raw" in result  # Raw balance in wei (string)
        assert result["decimals"] == 18
        # Balance should be a valid number (string representation)
        assert result["balance"] is not None
        assert result["balance_raw"] is not None
        print(f"✅ ETH Balance: {result['balance']} ETH (raw: {result['balance_raw']} wei)")

    @pytest.mark.asyncio
    async def test_get_native_eth_balance_zero_address(self, api_key):
        """Test ETH balance fetch for zero address."""
        # Note: The zero address (0x0000...) can actually have a balance in some cases
        # So we just verify the structure is correct, not that balance is zero
        result = await get_native_eth_balance_thegraph(TEST_ADDRESS_ZERO, api_key)

        assert result is not None
        # Check actual return structure
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["chain_name"] == "Ethereum"
        assert result["chain_id"] == "1"
        assert "balance" in result
        assert "balance_raw" in result
        # Error should be None (zero balance is valid, not an error)
        assert result.get("error") is None or result.get("error") == ""
        print(f"✅ Zero address balance: {result['balance']} ETH (raw: {result['balance_raw']} wei)")

    @pytest.mark.asyncio
    async def test_get_native_eth_balance_no_api_key(self, test_address):
        """Test ETH balance fetch without API key."""
        # Temporarily unset the API key to test error handling
        import os
        original_key = os.environ.get("THEGRAPH_API_KEY")
        try:
            # Remove from environment
            if "THEGRAPH_API_KEY" in os.environ:
                del os.environ["THEGRAPH_API_KEY"]
            
            # Function returns error dict instead of raising exception
            result = await get_native_eth_balance_thegraph(test_address, api_key=None)
            assert result is not None
            assert "error" in result
            assert result["error"] is not None
            assert "THEGRAPH_API_KEY" in result["error"]
            print(f"✅ Correctly handled missing API key: {result['error']}")
        finally:
            # Restore original API key
            if original_key:
                os.environ["THEGRAPH_API_KEY"] = original_key


class TestEthereumTokenBalance:
    """Tests for Ethereum token balance fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_token_balance_ethereum_usdc(self, api_key, test_address):
        """Test USDC token balance fetch with real API."""
        # Add delay to avoid rate limiting from previous tests
        import asyncio
        await asyncio.sleep(1.0)  # Wait 1 second to avoid rate limiting
        
        # Add timeout to prevent hanging
        try:
            result = await asyncio.wait_for(
                get_token_balance_ethereum_thegraph(test_address, "USDC", api_key),
                timeout=60.0  # Increased to 60 seconds (was 30)
            )
        except asyncio.TimeoutError:
            pytest.skip("USDC token balance fetch timed out (API may be slow or rate-limited)")
            return

        assert result is not None
        # May have error if token not found, or success if found
        if "error" not in result or result.get("error") is None or result.get("error") == "":
            # Check actual return structure from the implementation
            assert result["token_type"] == "ERC20"
            assert result["token_symbol"] == "USDC"
            assert "token_address" in result
            assert "balance" in result  # Human-readable balance
            assert "balance_raw" in result  # Raw balance
            assert "decimals" in result
            print(f"✅ USDC Balance: {result.get('balance', 'N/A')} USDC")
            print(f"   Address: {result.get('token_address', 'N/A')}")
        else:
            # If error, check error structure
            assert "error" in result
            assert result["token_type"] == "ERC20"
            assert result["token_symbol"] == "USDC"
            print(f"ℹ️  USDC not found for this address: {result.get('error')}")

    @pytest.mark.asyncio
    async def test_get_token_balance_ethereum_unknown_token(self, api_key, test_address):
        """Test token balance fetch for unknown token."""
        import asyncio
        # Add delay to avoid rate limiting from previous tests
        await asyncio.sleep(1.0)  # Wait 1 second to avoid rate limiting
        
        try:
            result = await asyncio.wait_for(
                get_token_balance_ethereum_thegraph(
                    test_address, "UNKNOWNTOKEN123", api_key
                ),
                timeout=60.0  # Increased to 60 seconds (was 30)
            )
        except asyncio.TimeoutError:
            pytest.skip("Unknown token balance fetch timed out (API may be slow)")
            return

        assert result is not None
        # Should return error dict with proper structure
        assert "error" in result
        assert result["token_type"] == "ERC20"
        assert result["token_symbol"] == "UNKNOWNTOKEN123"
        assert result["error"] is not None
        assert "not found" in result["error"].lower() or "error" in result["error"].lower()
        assert result["balance"] == "0"
        assert result["balance_raw"] == "0"
        print(f"✅ Correctly handled unknown token: {result.get('error')}")


class TestEthereumMultipleTokenBalances:
    """Tests for Ethereum multiple token balances fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_multiple_token_balances_ethereum_success(
        self, api_key, test_address
    ):
        """Test fetching all token balances with real API."""
        # Add delay to avoid rate limiting from previous tests
        import asyncio
        await asyncio.sleep(2.0)  # Wait 2 seconds to avoid rate limiting
        
        # Add timeout to prevent hanging (match CLI timeout)
        try:
            result = await asyncio.wait_for(
                get_multiple_token_balances_ethereum_thegraph(test_address, api_key=api_key),
                timeout=120.0  # Increased to 120 seconds to match CLI (was 60)
            )
        except asyncio.TimeoutError:
            pytest.skip("Multiple token balances fetch timed out (API may be slow or rate-limited)")
            return

        assert result is not None
        assert "tokens" in result
        assert "error" not in result or result.get("error") is None

        tokens = result.get("tokens", [])
        print(f"✅ Found {len(tokens)} token(s) for address {test_address}")

        if tokens:
            # Check actual token structure from the implementation
            for i, token in enumerate(tokens[:5], 1):
                assert "token_type" in token
                assert token["token_type"] == "ERC20"
                assert "token_symbol" in token
                assert "token_address" in token
                assert "balance" in token  # Human-readable balance
                assert "balance_raw" in token  # Raw balance
                assert "decimals" in token
                assert "chain_name" in token
                assert "chain_id" in token
                symbol = token.get("token_symbol", "N/A")
                balance = token.get("balance", "0")
                usd_value = token.get("usd_value", "0")
                print(f"  {i}. {symbol}: {balance} (USD: ${usd_value})")

    @pytest.mark.asyncio
    async def test_get_multiple_token_balances_ethereum_with_filter(
        self, api_key, test_address
    ):
        """Test fetching filtered token balances with real API."""
        # Add delay to avoid rate limiting from previous tests
        import asyncio
        await asyncio.sleep(2.0)  # Wait 2 seconds to avoid rate limiting
        
        # Add timeout to prevent hanging (match CLI timeout)
        try:
            result = await asyncio.wait_for(
                get_multiple_token_balances_ethereum_thegraph(
                    test_address, token_symbols=["USDC", "USDT"], api_key=api_key
                ),
                timeout=120.0  # Increased to 120 seconds to match CLI (was 60)
            )
        except asyncio.TimeoutError:
            pytest.skip("Filtered token balances fetch timed out (API may be slow or rate-limited)")
            return

        assert result is not None
        assert "tokens" in result

        tokens = result.get("tokens", [])
        print(f"✅ Found {len(tokens)} filtered token(s)")

        # All returned tokens should be USDC or USDT (if they exist)
        if tokens:
            for token in tokens:
                symbol = token.get("token_symbol", "")
                assert symbol in ["USDC", "USDT"]
                # Check token structure
                assert token["token_type"] == "ERC20"
                assert "balance" in token
                assert "balance_raw" in token
                print(f"  - {symbol}: {token.get('balance', '0')}")
        else:
            print("  ℹ️  No USDC/USDT tokens found for this address")

    @pytest.mark.asyncio
    async def test_get_multiple_token_balances_ethereum_zero_address(self, api_key):
        """Test fetching token balances for zero address."""
        # Note: The zero address (0x0000...) is commonly used as a burn address
        # and can accumulate tokens over time. It's not actually "empty".
        # The zero address has 500+ tokens, so it may hit the max_pages limit.
        result = await get_multiple_token_balances_ethereum_thegraph(
            TEST_ADDRESS_ZERO, api_key=api_key
        )

        assert result is not None
        assert "tokens" in result
        # Zero address can have tokens (it's used as a burn address)
        # We just verify the structure is correct
        tokens = result.get("tokens", [])
        
        # Zero address has 500+ tokens, so it may hit max_pages limit (50 pages = 500 tokens)
        # This is acceptable - we just verify we got tokens and the structure is correct
        error = result.get("error")
        if error and "maximum page limit" in error.lower():
            # This is expected for zero address (has too many tokens)
            print(f"ℹ️  Zero address has {len(tokens)} tokens (hit max_pages limit, which is expected)")
        else:
            # No error or different error - verify no error
            assert error is None or error == ""
        
        # Verify we got some tokens (zero address definitely has tokens)
        assert len(tokens) > 0, "Zero address should have at least some tokens"
        
        # Verify token structure
        for token in tokens[:3]:  # Check first 3 tokens
            assert "token_type" in token
            assert token["token_type"] == "ERC20"
            assert "token_symbol" in token
            assert "token_address" in token
            assert "balance" in token
        
        print(f"✅ Zero address has {len(tokens)} tokens (used as burn address, can accumulate tokens)")

