"""
Unit tests for Ethereum balance client using The Graph API with real API calls.

These tests make real API calls to The Graph API.
Requires THEGRAPH_API_KEY environment variable to be set (can be in .env file).
"""

import pytest
import os
import asyncio
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
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["token_address"] == "0x0"
        assert result["chain_name"] == "Ethereum"
        assert result["chain_id"] == "1"
        assert "balance" in result
        assert "balance_raw" in result
        assert result["decimals"] == 18
        print(f"✅ ETH Balance: {result['balance']} ETH")

    @pytest.mark.asyncio
    async def test_get_native_eth_balance_zero_address(self, api_key):
        """Test ETH balance fetch for zero address with real API."""
        result = await get_native_eth_balance_thegraph(TEST_ADDRESS_ZERO, api_key)

        assert result is not None
        assert result["token_type"] == "native"
        assert result["token_symbol"] == "ETH"
        assert result["chain_name"] == "Ethereum"
        assert result["chain_id"] == "1"
        assert "balance" in result
        assert "balance_raw" in result
        assert result.get("error") is None or result.get("error") == ""
        print(f"✅ Zero address balance: {result['balance']} ETH")

    @pytest.mark.asyncio
    async def test_get_native_eth_balance_no_api_key(self, test_address):
        """Test ETH balance fetch without API key."""
        import os
        original_key = os.environ.get("THEGRAPH_API_KEY")
        try:
            if "THEGRAPH_API_KEY" in os.environ:
                del os.environ["THEGRAPH_API_KEY"]

            result = await get_native_eth_balance_thegraph(test_address, api_key=None)
            assert result is not None
            assert "error" in result
            assert result["error"] is not None
            assert "THEGRAPH_API_KEY" in result["error"]
            print(f"✅ Correctly handled missing API key: {result['error']}")
        finally:
            if original_key:
                os.environ["THEGRAPH_API_KEY"] = original_key


class TestEthereumTokenBalance:
    """Tests for Ethereum token balance fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_token_balance_ethereum_usdc(self, api_key, test_address):
        """Test USDC token balance fetch with real API."""
        await asyncio.sleep(1)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                get_token_balance_ethereum_thegraph(test_address, "USDC", api_key),
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

    @pytest.mark.asyncio
    async def test_get_token_balance_ethereum_unknown_token(self, api_key, test_address):
        """Test token balance fetch for unknown token with real API."""
        await asyncio.sleep(1)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                get_token_balance_ethereum_thegraph(
                    test_address, "UNKNOWNTOKEN123", api_key
                ),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            pytest.skip("Unknown token balance fetch timed out")
            return

        assert result is not None
        assert "error" in result
        assert result["token_type"] == "ERC20"
        assert result["token_symbol"] == "UNKNOWNTOKEN123"
        assert result["error"] is not None
        print(f"✅ Correctly handled unknown token: {result.get('error')}")


class TestEthereumMultipleTokenBalances:
    """Tests for Ethereum multiple token balances fetching with real API."""

    @pytest.mark.asyncio
    async def test_get_multiple_token_balances_ethereum_success(
        self, api_key, test_address
    ):
        """Test fetching all token balances with real API."""
        await asyncio.sleep(2)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                get_multiple_token_balances_ethereum_thegraph(test_address, api_key=api_key),
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
