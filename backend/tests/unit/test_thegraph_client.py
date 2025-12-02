"""
Unit tests for The Graph API client using real API calls.

These tests make real API calls to The Graph API.
Requires THEGRAPH_API_KEY environment variable to be set (can be in .env file).
"""

import pytest
import os
import asyncio
import pytest_asyncio
from dotenv import load_dotenv
from packages.blockchain.thegraph.client import TheGraphClient

# Load environment variables from .env file
load_dotenv()

# Test addresses with known balances
TEST_ADDRESS_WITH_BALANCE = "0x1fA33c1CA2d733C895BeFf7a3d468Cee317Be253"  # Ethereum address
TEST_ADDRESS_ZERO = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module")
def api_key():
    """Get API key from environment."""
    key = os.getenv("THEGRAPH_API_KEY")
    if not key:
        pytest.skip("THEGRAPH_API_KEY environment variable not set")
    return key


@pytest_asyncio.fixture
async def client(api_key):
    """Create a test client with proper cleanup."""
    client = TheGraphClient(api_key=api_key)
    yield client
    await client.close()


class TestTheGraphClient:
    """Test suite for TheGraphClient with real API calls."""

    def test_init_with_api_key(self, api_key):
        """Test client initialization with API key."""
        client = TheGraphClient(api_key=api_key)
        assert client.api_key == api_key
        assert client._client is not None
        # Clean up
        import asyncio
        asyncio.run(client.close())

    def test_init_without_api_key(self):
        """Test client initialization without API key raises error."""
        import os
        original_key = os.environ.get("THEGRAPH_API_KEY")
        try:
            if "THEGRAPH_API_KEY" in os.environ:
                del os.environ["THEGRAPH_API_KEY"]
            with pytest.raises(ValueError, match="API key is required"):
                TheGraphClient()
        finally:
            if original_key:
                os.environ["THEGRAPH_API_KEY"] = original_key

    def test_init_from_env_var(self):
        """Test client initialization from environment variable."""
        key = os.getenv("THEGRAPH_API_KEY")
        if not key:
            pytest.skip("THEGRAPH_API_KEY environment variable not set")
        client = TheGraphClient()
        assert client.api_key == key
        # Clean up
        import asyncio
        asyncio.run(client.close())

    @pytest.mark.asyncio
    async def test_get_native_balance_success(self, client, api_key):
        """Test successful native balance fetch with real API."""
        result = await client.get_native_balance(
            TEST_ADDRESS_WITH_BALANCE, "ethereum"
        )

        assert result is not None
        assert result.chain_id == "1"
        assert result.chain_name == "Ethereum"
        assert result.balance is not None
        assert result.symbol == "ETH"
        print(f"✅ Native balance: {result.balance} {result.symbol}")

    @pytest.mark.asyncio
    async def test_get_native_balance_zero_address(self, client):
        """Test native balance fetch for zero address with real API."""
        # Zero address can have balance (used as burn address)
        result = await client.get_native_balance(
            TEST_ADDRESS_ZERO, "ethereum"
        )

        # Zero address may or may not have balance
        if result:
            assert result.chain_id == "1"
            assert result.chain_name == "Ethereum"
            assert result.symbol == "ETH"
            print(f"✅ Zero address balance: {result.balance} {result.symbol}")
        else:
            print("ℹ️  Zero address has no native balance")

    @pytest.mark.asyncio
    async def test_get_native_balance_unsupported_network(self, client):
        """Test native balance fetch with unsupported network."""
        result = await client.get_native_balance(
            TEST_ADDRESS_WITH_BALANCE, "unsupported"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_native_balance_polygon(self, client):
        """Test native balance fetch on Polygon with real API."""
        result = await client.get_native_balance(
            "0xde881c6c4f469cca1dfc226dcdc98f98d5e17840", "polygon"
        )

        assert result is not None
        assert result.chain_id == "137"
        assert result.chain_name == "Polygon"
        assert result.symbol == "MATIC"
        print(f"✅ Polygon native balance: {result.balance} {result.symbol}")

    @pytest.mark.asyncio
    async def test_get_native_balance_base(self, client):
        """Test native balance fetch on Base with real API."""
        result = await client.get_native_balance(
            "0x5DE176348c089B9709bAF01C5d0EDBbb82f2A8A6", "base"
        )

        assert result is not None
        assert result.chain_id == "8453"
        assert result.chain_name == "Base"
        assert result.symbol == "ETH"
        print(f"✅ Base native balance: {result.balance} {result.symbol}")

    @pytest.mark.asyncio
    async def test_get_token_balances_success(self, client):
        """Test successful token balances fetch with real API."""
        await asyncio.sleep(1)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                client.get_token_balances(
                    TEST_ADDRESS_WITH_BALANCE, "ethereum"
                ),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            pytest.skip("Token balances fetch timed out (API may be slow)")
            return

        assert result is not None
        assert isinstance(result, list)
        # Address may or may not have tokens
        if len(result) > 0:
            token = result[0]
            assert token.token_symbol is not None
            assert token.token_address is not None
            print(f"✅ Found {len(result)} token(s), first: {token.token_symbol}")
        else:
            print("ℹ️  Address has no ERC-20 tokens")

    @pytest.mark.asyncio
    async def test_get_all_token_balances_pagination(self, client):
        """Test pagination in get_all_token_balances with real API."""
        await asyncio.sleep(2)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                client.get_all_token_balances(
                    TEST_ADDRESS_WITH_BALANCE, "ethereum"
                ),
                timeout=120.0
            )
        except asyncio.TimeoutError:
            pytest.skip("All token balances fetch timed out (API may be slow)")
            return

        assert result is not None
        assert isinstance(result, list)
        print(f"✅ Found {len(result)} total token(s)")

    @pytest.mark.asyncio
    async def test_get_token_balance_by_symbol_found(self, client):
        """Test get_token_balance_by_symbol when token is found with real API."""
        await asyncio.sleep(1)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                client.get_token_balance_by_symbol(
                    TEST_ADDRESS_WITH_BALANCE, "USDC", "ethereum"
                ),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            pytest.skip("Token balance by symbol fetch timed out")
            return

        # Token may or may not be found
        if result:
            assert result.token_symbol == "USDC"
            print(f"✅ Found USDC token: {result.token_quantity}")
        else:
            print("ℹ️  USDC token not found for this address")

    @pytest.mark.asyncio
    async def test_get_token_balance_by_symbol_not_found(self, client):
        """Test get_token_balance_by_symbol when token is not found with real API."""
        await asyncio.sleep(1)  # Rate limiting delay
        try:
            result = await asyncio.wait_for(
                client.get_token_balance_by_symbol(
                    TEST_ADDRESS_WITH_BALANCE, "NONEXISTENTTOKEN123", "ethereum"
                ),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            pytest.skip("Token balance by symbol fetch timed out")
            return

        # Should return None for non-existent token
        assert result is None
        print("✅ Correctly returned None for non-existent token")

    @pytest.mark.asyncio
    async def test_close_client(self, client):
        """Test client close method."""
        # Client should close without error
        await client.close()
        # Verify client is closed (can't make new requests)
        # This is a basic test - actual close verification would require checking internal state

    @pytest.mark.asyncio
    async def test_context_manager(self, api_key):
        """Test client as async context manager with real API."""
        async with TheGraphClient(api_key=api_key) as client:
            assert client is not None
            # Test that we can make a call
            result = await client.get_native_balance(
                TEST_ADDRESS_WITH_BALANCE, "ethereum"
            )
            assert result is not None
            print("✅ Context manager works correctly")
