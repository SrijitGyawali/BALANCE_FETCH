"""
The Graph API balance client.

This module provides balance fetching functions that match the pattern
used by other blockchain balance clients (ethereum, polygon, etc.).
"""

from packages.blockchain.thegraph.balance.balance_client import (
    get_native_balance_thegraph,
    get_token_balance_thegraph,
    get_all_token_balances_thegraph,
)

__all__ = [
    "get_native_balance_thegraph",
    "get_token_balance_thegraph",
    "get_all_token_balances_thegraph",
]




