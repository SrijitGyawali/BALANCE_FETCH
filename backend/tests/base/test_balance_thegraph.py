"""
Tests for Base balance client using The Graph API.

These tests make real API calls to The Graph API.
Requires THEGRAPH_API_KEY environment variable to be set (can be in .env file).
"""

import pytest
import os
from dotenv import load_dotenv
from packages.blockchain.base.balance.balance_client_thegraph import (
    get_native_base_balance_thegraph,
    get_token_balance_base_thegraph,
    get_multiple_token_balances_base_thegraph,
)

# Load environment variables from .env file
load_dotenv()

# Test addresses with known balances
TEST_ADDRESS_WITH_BALANCE = "0x5DE176348c089B9709bAF01C5d0EDBbb82f2A8A6"  # Common test address
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


class TestBaseNativeBalance:
    """Tests for Base native balance fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_native_base_balance_success(self, api_key, test_address):
        """Test successful Base ETH balance fetch with real API."""
        result = await get_native_base_balance_thegraph(test_address, api_key)

        assert result is not None
        assert "error" not in result or result.get("error") is None
        # Check actual return structure from the implementation
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["token_address"] == "0x0"
        assert result["chain_name"] == "Base"
        assert result["chain_id"] == "8453"
        assert "balance" in result  # Human-readable balance (string)
        assert "balance_raw" in result  # Raw balance in wei (string)
        assert result["decimals"] == 18
        assert result["balance"] is not None
        assert result["balance_raw"] is not None
        print(f"✅ Base ETH Balance: {result['balance']} ETH (raw: {result['balance_raw']} wei)")

    @pytest.mark.asyncio
    async def test_get_native_base_balance_zero_address(self, api_key):
        """Test Base ETH balance fetch for zero address."""
        # Note: The zero address (0x0000...) can actually have a balance in some cases
        # So we just verify the structure is correct, not that balance is zero
        result = await get_native_base_balance_thegraph(TEST_ADDRESS_ZERO, api_key)

        assert result is not None
        # Check actual return structure
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["chain_name"] == "Base"
        assert result["chain_id"] == "8453"
        assert "balance" in result
        assert "balance_raw" in result
        # Error should be None (zero balance is valid, not an error)
        assert result.get("error") is None or result.get("error") == ""
        print(f"✅ Zero address balance: {result['balance']} ETH (raw: {result['balance_raw']} wei)")


class TestBaseTokenBalance:
    """Tests for Base token balance fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_token_balance_base_usdc(self, api_key, test_address):
        """Test USDC token balance fetch with real API."""
        # Add delay to avoid rate limiting from previous tests
        import asyncio
        await asyncio.sleep(1.0)  # Wait 1 second to avoid rate limiting
        
        # Add timeout to prevent hanging
        try:
            result = await asyncio.wait_for(
                get_token_balance_base_thegraph(test_address, "USDC", api_key),
                timeout=60.0  # 60 second timeout
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


class TestBaseMultipleTokenBalances:
    """Tests for Base multiple token balances fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_multiple_token_balances_base_success(
        self, api_key, test_address
    ):
        """Test fetching all token balances with real API."""
        # Add delay to avoid rate limiting from previous tests
        import asyncio
        await asyncio.sleep(2.0)  # Wait 2 seconds to avoid rate limiting
        
        # Add timeout to prevent hanging (match CLI timeout)
        try:
            result = await asyncio.wait_for(
                get_multiple_token_balances_base_thegraph(test_address, api_key=api_key),
                timeout=120.0  # 120 second timeout to match CLI
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

