"""
Example integration of The Graph API with A2A Balance Agent.

This file shows how to update your agent.py to use The Graph API client
instead of stubbed functions.

Replace the stubbed tools in your agent.py with the implementations below.
"""

import os
from typing import Optional
from langchain.tools import tool
from packages.blockchain.thegraph import TheGraphClient
from packages.blockchain.thegraph.utils import (
    format_token_balance,
    calculate_usd_value,
    format_usd_value,
)

# Default network for balance queries
DEFAULT_NETWORK = "ethereum"


@tool
async def get_balance(address: str, network: str = DEFAULT_NETWORK) -> str:
    """
    Get the native token balance of a cryptocurrency address on a specific network.

    Args:
        address: Ethereum address (0x...)
        network: Network name (ethereum, polygon, base, etc.) or chain ID

    Returns:
        Formatted string with balance information
    """
    api_key = os.getenv("THEGRAPH_API_KEY")
    if not api_key:
        return "Error: THEGRAPH_API_KEY environment variable is not set."

    try:
        async with TheGraphClient(api_key=api_key) as client:
            native_balance = await client.get_native_balance(address, network)

            if not native_balance:
                return f"No native balance found for {address} on {network}."

            # Format balance
            balance_eth = float(native_balance.balance) / 1e18
            formatted_balance = f"{balance_eth:.6f}".rstrip("0").rstrip(".")

            return (
                f"Balance for {address} on {native_balance.chain_name}: "
                f"{formatted_balance} {native_balance.symbol}"
            )

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error fetching balance: {str(e)}"


@tool
async def get_token_balance(
    address: str, token: str, network: str = DEFAULT_NETWORK
) -> str:
    """
    Get the balance of a specific ERC-20 token for an address on a network.

    Args:
        address: Ethereum address (0x...)
        token: Token symbol (e.g., USDC, DAI, WETH)
        network: Network name (ethereum, polygon, base, etc.) or chain ID

    Returns:
        Formatted string with token balance information
    """
    api_key = os.getenv("THEGRAPH_API_KEY")
    if not api_key:
        return "Error: THEGRAPH_API_KEY environment variable is not set."

    try:
        async with TheGraphClient(api_key=api_key) as client:
            token_balance = await client.get_token_balance_by_symbol(
                address, token, network
            )

            if not token_balance:
                return (
                    f"Token {token.upper()} not found for {address} on {network}. "
                    f"The address may not hold this token."
                )

            # Format balance
            balance = format_token_balance(
                token_balance.token_quantity, token_balance.token_divisor
            )
            usd_value = calculate_usd_value(balance, token_balance.token_price_usd)
            formatted_usd = format_usd_value(usd_value)

            return (
                f"Token balance for {address} on {token_balance.chain_name}: "
                f"{balance} {token_balance.token_symbol} "
                f"({formatted_usd})"
            )

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error fetching token balance: {str(e)}"


@tool
async def get_all_token_balances(
    address: str, network: str = DEFAULT_NETWORK
) -> str:
    """
    Get all ERC-20 token balances for an address on a network.

    Args:
        address: Ethereum address (0x...)
        network: Network name (ethereum, polygon, base, etc.) or chain ID

    Returns:
        Formatted string with all token balances
    """
    api_key = os.getenv("THEGRAPH_API_KEY")
    if not api_key:
        return "Error: THEGRAPH_API_KEY environment variable is not set."

    try:
        async with TheGraphClient(api_key=api_key) as client:
            tokens = await client.get_all_token_balances(address, network)

            if not tokens:
                return f"No token balances found for {address} on {network}."

            # Format response
            lines = [
                f"Token balances for {address} on {network}:",
                f"Found {len(tokens)} token(s):",
                "",
            ]

            total_usd = 0.0
            for token in tokens:
                balance = format_token_balance(
                    token.token_quantity, token.token_divisor
                )
                usd_value = calculate_usd_value(balance, token.token_price_usd)
                total_usd += usd_value
                formatted_usd = format_usd_value(usd_value)

                lines.append(
                    f"  - {token.token_symbol} ({token.token_name}): "
                    f"{balance} ({formatted_usd})"
                )

            lines.append("")
            lines.append(f"Total USD Value: {format_usd_value(total_usd)}")

            return "\n".join(lines)

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error fetching token balances: {str(e)}"


# Example usage in your agent.py:
#
# from agents.balance.agent_integration_example import (
#     get_balance,
#     get_token_balance,
#     get_all_token_balances,
# )
#
# # In your agent setup:
# tools = [get_balance, get_token_balance, get_all_token_balances]
# agent = create_agent(tools=tools, ...)





