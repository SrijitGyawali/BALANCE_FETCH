"""
Utility functions for The Graph API client.
"""

from typing import Dict
from packages.blockchain.thegraph.models import ChainInfo

# Supported chains mapping
SUPPORTED_CHAINS: Dict[str, ChainInfo] = {
    "1": ChainInfo(
        chain_id="1",
        name="Ethereum",
        native_symbol="ETH",
        network_name="mainnet",
    ),
    "137": ChainInfo(
        chain_id="137",
        name="Polygon",
        native_symbol="MATIC",
        network_name="polygon",
    ),
    "8453": ChainInfo(
        chain_id="8453",
        name="Base",
        native_symbol="ETH",
        network_name="base",
    ),
    "42161": ChainInfo(
        chain_id="42161",
        name="Arbitrum",
        native_symbol="ETH",
        network_name="arbitrum-one",
    ),
    "10": ChainInfo(
        chain_id="10",
        name="Optimism",
        native_symbol="ETH",
        network_name="optimism",
    ),
    "56": ChainInfo(
        chain_id="56",
        name="BSC",
        native_symbol="BNB",
        network_name="bsc",
    ),
    "43114": ChainInfo(
        chain_id="43114",
        name="Avalanche",
        native_symbol="AVAX",
        network_name="avalanche",
    ),
}

# Network name to chain ID mapping (for agent network names)
NETWORK_NAME_TO_CHAIN_ID: Dict[str, str] = {
    "ethereum": "1",
    "polygon": "137",
    "base": "8453",
    "arbitrum": "42161",
    "optimism": "10",
    "bsc": "56",
    "avalanche": "43114",
}


def get_chain_info(network: str) -> ChainInfo | None:
    """
    Get chain information by network name or chain ID.

    Args:
        network: Network name (e.g., "ethereum", "polygon") or chain ID (e.g., "1", "137")

    Returns:
        ChainInfo if found, None otherwise
    """
    network_lower = network.lower()

    # Try chain ID first
    if network_lower in SUPPORTED_CHAINS:
        return SUPPORTED_CHAINS[network_lower]

    # Try network name mapping
    if network_lower in NETWORK_NAME_TO_CHAIN_ID:
        chain_id = NETWORK_NAME_TO_CHAIN_ID[network_lower]
        return SUPPORTED_CHAINS.get(chain_id)

    return None


def format_token_balance(quantity: str, divisor: str) -> str:
    """
    Format token quantity based on divisor (decimals).

    Args:
        quantity: Raw token quantity as string
        divisor: Token divisor (10^decimals) as string

    Returns:
        Formatted token balance as string
    """
    if not quantity or quantity == "0":
        return "0"

    try:
        quantity_int = int(quantity)
        divisor_int = int(divisor)

        if divisor_int == 0:
            return str(quantity_int)

        whole_part = quantity_int // divisor_int
        fractional_part = quantity_int % divisor_int

        if fractional_part == 0:
            return str(whole_part)

        # Format fractional part
        fractional_str = str(fractional_part).zfill(len(str(divisor_int)) - 1)
        fractional_str = fractional_str.rstrip("0")

        if fractional_str:
            return f"{whole_part}.{fractional_str}"
        return str(whole_part)

    except (ValueError, ZeroDivisionError) as e:
        return f"Error formatting balance: {str(e)}"


def calculate_usd_value(balance: str, price_usd: str) -> float:
    """
    Calculate USD value of token balance.

    Args:
        balance: Formatted token balance as string
        price_usd: Token price in USD as string

    Returns:
        USD value as float
    """
    try:
        balance_num = float(balance)
        price_num = float(price_usd)
        return balance_num * price_num
    except (ValueError, TypeError):
        return 0.0


def format_usd_value(value: float) -> str:
    """
    Format USD value for display.

    Args:
        value: USD value as float

    Returns:
        Formatted USD string
    """
    if not isinstance(value, (int, float)) or value != value:  # Check for NaN
        return "$0.00"

    if value == 0:
        return "$0.00"

    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    if abs_value < 0.000001:
        return f"{sign}${value:.2e}"

    if abs_value < 0.01:
        return f"{sign}${value:.6f}"

    if abs_value >= 1e18:
        quintillions = abs_value / 1e18
        return f"{sign}${quintillions:,.2f}Qi"

    if abs_value >= 1e15:
        quadrillions = abs_value / 1e15
        return f"{sign}${quadrillions:,.2f}Qa"

    if abs_value >= 1e12:
        trillions = abs_value / 1e12
        return f"{sign}${trillions:,.2f}T"

    if abs_value >= 1e9:
        billions = abs_value / 1e9
        return f"{sign}${billions:,.2f}B"

    if abs_value >= 1e6:
        millions = abs_value / 1e6
        return f"{sign}${millions:,.2f}M"

    if abs_value >= 1e3:
        thousands = abs_value / 1e3
        return f"{sign}${thousands:,.2f}K"

    return f"{sign}${value:,.2f}"





