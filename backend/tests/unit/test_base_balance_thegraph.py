"""
Unit tests for Base balance client using The Graph API with real API calls.

These tests make real API calls to The Graph API.
Requires THEGRAPH_API_KEY environment variable to be set (can be in .env file).
"""

import pytest
import os
import asyncio
from dotenv import load_dotenv
from packages.blockchain.base.balance.balance_client_thegraph import (
    get_native_base_balance_thegraph,
    get_token_balance_base_thegraph,
    get_multiple_token_balances_base_thegraph,
)

# Load environment variables from .env file
load_dotenv()

# Test addresses with known balances
TEST_ADDRESS_WITH_BALANCE = "0x5DE176348c089B9709bAF01C5d0EDBbb82f2A8A6"
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
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["token_address"] == "0x0"
        assert result["chain_name"] == "Base"
        assert result["chain_id"] == "8453"
        assert "balance" in result
        assert "balance_raw" in result
        assert result["decimals"] == 18
        print(f"✅ Base ETH Balance: {result['balance']} ETH")

    @pytest.mark.asyncio
    async def test_get_native_base_balance_zero_address(self, api_key):
        """Test Base ETH balance fetch for zero address with real API."""
        result = await get_native_base_balance_thegraph(TEST_ADDRESS_ZERO, api_key)

        assert result is not None
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["chain_name"] == "Base"
        assert result["chain_id"] == "8453"
        assert "balance" in result
        assert "balance_raw" in result
        assert result.get("error") is None or result.get("error") == ""
        print(f"✅ Zero address balance: {result['balance']} ETH")


class TestBaseTokenBalance:
    """Tests for Base token balance fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_token_balance_base_usdc(self, api_key, test_address):
        """Test USDC token balance fetch on Base with real API."""
        await asyncio.sleep(1)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                get_token_balance_base_thegraph(test_address, "USDC", api_key),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            pytest.skip("USDC token balance fetch timed out")
            return

        assert result is not None
        if "error" not in result or result.get("error") is None or result.get("error") == "":
            assert result["token_type"] == "ERC20"
            assert result["token_symbol"] == "USDC"
            assert "token_address" in result
            assert "balance" in result
            print(f"✅ USDC Balance: {result.get('balance', 'N/A')} USDC")
        else:
            assert "error" in result
            assert result["token_type"] == "ERC20"
            print(f"ℹ️  USDC not found: {result.get('error')}")


class TestBaseMultipleTokenBalances:
    """Tests for Base multiple token balances fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_multiple_token_balances_base_success(
        self, api_key, test_address
    ):
        """Test fetching all token balances on Base with real API."""
        await asyncio.sleep(2)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                get_multiple_token_balances_base_thegraph(test_address, api_key=api_key),
                timeout=120.0
            )
        except asyncio.TimeoutError:
            pytest.skip("Multiple token balances fetch timed out")
            return

        assert result is not None
        assert "tokens" in result
        assert "error" not in result or result.get("error") is None

        tokens = result.get("tokens", [])
        print(f"✅ Found {len(tokens)} token(s)")

        if tokens:
            for i, token in enumerate(tokens[:5], 1):
                assert "token_type" in token
                assert token["token_type"] == "ERC20"
                assert "token_symbol" in token
                assert "token_address" in token
                assert "balance" in token
                symbol = token.get("token_symbol", "N/A")
                balance = token.get("balance", "0")
                print(f"  {i}. {symbol}: {balance}")
