"""
The Graph Token API client for fetching blockchain balances.

This client provides methods to fetch native token balances and ERC-20 token
balances across multiple blockchain networks using The Graph Token API.
"""

import asyncio
import os
from typing import Optional, List
import httpx
from packages.blockchain.thegraph.models import (
    NativeBalance,
    TokenBalance,
    TheGraphTokenResponse,
    TheGraphNativeResponse,
)
from packages.blockchain.thegraph.utils import (
    get_chain_info,
    format_token_balance,
)


class TheGraphClient:
    """
    Client for The Graph Token API.

    This client handles fetching native and ERC-20 token balances
    across multiple blockchain networks.
    """

    BASE_URL = "https://token-api.thegraph.com/v1/evm"
    DEFAULT_LIMIT = 10
    REQUEST_DELAY = 0.2  # 200ms delay between requests

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize The Graph API client.

        Args:
            api_key: The Graph API JWT token. If not provided, will try to
                     get from THEGRAPH_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("THEGRAPH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "The Graph API key is required. "
                "Provide it as parameter or set THEGRAPH_API_KEY environment variable."
            )

        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def get_native_balance(
        self, address: str, network: str
    ) -> Optional[NativeBalance]:
        """
        Get native token balance for an address on a specific network.

        Args:
            address: Wallet address (0x...)
            network: Network name (e.g., "ethereum", "polygon") or chain ID

        Returns:
            NativeBalance if found, None otherwise
        """
        chain_info = get_chain_info(network)
        if not chain_info:
            return None

        query_params = {
            "network": chain_info.network_name,
            "address": address,
            "include_null_balances": "true",  # Changed to true to get zero balances
            "limit": "10",
            "page": "1",
        }

        url = f"{self.BASE_URL}/balances/native"
        try:
            response = await self._client.get(url, params=query_params)
            response.raise_for_status()

            data = TheGraphNativeResponse(**response.json())

            if data.data and len(data.data) > 0:
                native_balance = data.data[0]
                # The Graph API uses "amount" field, not "balance"
                balance_wei = native_balance.amount or native_balance.balance or "0"
                if balance_wei and balance_wei != "0":
                    balance_eth = float(balance_wei) / 1e18

                    if balance_eth == 0:
                        return None

                    return NativeBalance(
                        chain_id=chain_info.chain_id,
                        chain_name=chain_info.name,
                        balance=balance_wei,
                        symbol=chain_info.native_symbol,
                        price_usd="0",
                    )

            return None

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "The Graph API authentication failed. Please check your API key."
                )
            if e.response.status_code == 403:
                raise ValueError(
                    "The Graph API access forbidden. Please check your API key permissions."
                )
            if e.response.status_code == 429:
                raise ValueError(
                    "The Graph API rate limit exceeded. Please wait and try again."
                )
            raise ValueError(f"HTTP error! status: {e.response.status_code}")

        except Exception as e:
            raise ValueError(f"Error fetching native balance: {str(e)}")

    async def get_token_balances(
        self,
        address: str,
        network: str,
        limit: int = DEFAULT_LIMIT,
        page: int = 1,
    ) -> List[TokenBalance]:
        """
        Get ERC-20 token balances for an address on a specific network.

        Args:
            address: Wallet address (0x...)
            network: Network name (e.g., "ethereum", "polygon") or chain ID
            limit: Number of items per query (max 10 for free tier)
            page: Page number for pagination

        Returns:
            List of TokenBalance objects
        """
        chain_info = get_chain_info(network)
        if not chain_info:
            return []

        query_params = {
            "network": chain_info.network_name,
            "address": address,
            "limit": str(limit),
            "page": str(page),
            "include_null_balances": "false",
        }

        url = f"{self.BASE_URL}/balances"
        try:
            response = await self._client.get(url, params=query_params)
            response.raise_for_status()

            data = TheGraphTokenResponse(**response.json())

            if data.data:
                tokens: List[TokenBalance] = []
                for balance in data.data:
                    decimals = balance.decimals or 18
                    divisor = str(10**decimals)

                    tokens.append(
                        TokenBalance(
                            token_address=balance.contract,
                            token_name=balance.name or "Unknown",
                            token_symbol=balance.symbol or "UNKNOWN",
                            token_quantity=balance.amount,
                            token_divisor=divisor,
                            token_price_usd=str(balance.value or 0),
                            chain_id=chain_info.chain_id,
                            chain_name=chain_info.name,
                        )
                    )

                return tokens

            return []

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "The Graph API authentication failed. Please check your API key."
                )
            if e.response.status_code == 403:
                raise ValueError(
                    "The Graph API access forbidden. Please check your API key permissions."
                )
            if e.response.status_code == 429:
                raise ValueError(
                    "The Graph API rate limit exceeded. Please wait and try again."
                )
            raise ValueError(f"HTTP error! status: {e.response.status_code}")

        except Exception as e:
            raise ValueError(f"Error fetching token balances: {str(e)}")

    async def get_all_token_balances(
        self, address: str, network: str
    ) -> List[TokenBalance]:
        """
        Get all ERC-20 token balances across multiple pages.

        Args:
            address: Wallet address (0x...)
            network: Network name (e.g., "ethereum", "polygon") or chain ID

        Returns:
            List of all TokenBalance objects
        """
        all_tokens: List[TokenBalance] = []
        page = 1

        while True:
            try:
                await asyncio.sleep(self.REQUEST_DELAY)
                tokens = await self.get_token_balances(
                    address, network, limit=self.DEFAULT_LIMIT, page=page
                )

                if not tokens:
                    break

                all_tokens.extend(tokens)

                if len(tokens) < self.DEFAULT_LIMIT:
                    break

                page += 1

            except ValueError as e:
                error_message = str(e)
                if "rate limit" in error_message.lower():
                    await asyncio.sleep(5)  # Wait 5 seconds on rate limit
                    continue
                raise

        return all_tokens

    async def get_token_balance_by_symbol(
        self, address: str, token_symbol: str, network: str
    ) -> Optional[TokenBalance]:
        """
        Get balance for a specific token by symbol.

        Args:
            address: Wallet address (0x...)
            token_symbol: Token symbol (e.g., "USDC", "DAI")
            network: Network name (e.g., "ethereum", "polygon") or chain ID

        Returns:
            TokenBalance if found, None otherwise
        """
        all_tokens = await self.get_all_token_balances(address, network)

        token_symbol_upper = token_symbol.upper()
        for token in all_tokens:
            if token.token_symbol.upper() == token_symbol_upper:
                return token

        return None



