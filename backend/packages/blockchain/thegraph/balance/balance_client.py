"""
The Graph API balance client.

This module provides balance fetching functions that match the pattern
used by other blockchain balance clients (ethereum, polygon, etc.).

Functions return dictionaries with consistent structure for compatibility
with existing agent code.
"""

import asyncio
import os
from typing import Dict, List, Optional
import httpx
from packages.blockchain.thegraph.utils import (
    get_chain_info,
    format_token_balance,
    calculate_usd_value,
)


async def get_native_balance_thegraph(
    account_address: str, network: str, api_key: Optional[str] = None
) -> Dict:
    """
    Get native token balance using The Graph API.
    
    Matches the signature pattern of existing balance clients:
    - get_native_eth_balance(account_address: str) -> dict
    - get_native_matic_balance(account_address: str) -> dict
    
    Args:
        account_address: Wallet address (0x...)
        network: Network name (ethereum, polygon, base, etc.) or chain ID
        api_key: The Graph API JWT token (optional, uses env var if not provided)
    
    Returns:
        Dictionary with balance information:
        {
            "token_type": "native",
            "token_symbol": "ETH",
            "token_address": "0x0",
            "balance": "1.5",  # Human-readable balance
            "balance_raw": "1500000000000000000",  # Raw balance in wei
            "decimals": 18,
            "chain_name": "Ethereum",
            "chain_id": "1",
            "error": None  # Error message if any
        }
    """
    if not api_key:
        api_key = os.getenv("THEGRAPH_API_KEY")
    
    if not api_key:
        return {
            "error": "THEGRAPH_API_KEY environment variable is not set",
            "token_type": "native",
            "token_symbol": "ETH",
            "token_address": "0x0",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }
    
    chain_info = get_chain_info(network)
    if not chain_info:
        return {
            "error": f"Unsupported network: {network}",
            "token_type": "native",
            "token_symbol": "ETH",
            "token_address": "0x0",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }
    
        query_params = {
            "network": chain_info.network_name,
            "address": account_address,
            "include_null_balances": "true",  # Changed to true to get zero balances
            "limit": "10",
            "page": "1",
        }
    
    url = "https://token-api.thegraph.com/v1/evm/balances/native"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                params=query_params,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            
            if response.status_code == 401:
                return {
                    "error": "The Graph API authentication failed. Please check your API key.",
                    "token_type": "native",
                    "token_symbol": chain_info.native_symbol,
                    "token_address": "0x0",
                    "balance": "0",
                    "balance_raw": "0",
                    "decimals": 18,
                }
            
            if response.status_code == 403:
                return {
                    "error": "The Graph API access forbidden. Please check your API key permissions.",
                    "token_type": "native",
                    "token_symbol": chain_info.native_symbol,
                    "token_address": "0x0",
                    "balance": "0",
                    "balance_raw": "0",
                    "decimals": 18,
                }
            
            if response.status_code == 429:
                return {
                    "error": "The Graph API rate limit exceeded. Please wait and try again.",
                    "token_type": "native",
                    "token_symbol": chain_info.native_symbol,
                    "token_address": "0x0",
                    "balance": "0",
                    "balance_raw": "0",
                    "decimals": 18,
                }
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("data") and len(data["data"]) > 0:
                native_balance = data["data"][0]
                # The Graph API uses "amount" field, not "balance"
                balance_wei = native_balance.get("amount") or native_balance.get("balance", "0")
                
                if balance_wei == "0":
                    return {
                        "token_type": "native",
                        "token_symbol": chain_info.native_symbol,
                        "token_address": "0x0",
                        "balance": "0",
                        "balance_raw": "0",
                        "decimals": 18,
                        "chain_name": chain_info.name,
                        "chain_id": chain_info.chain_id,
                        "error": None,
                    }
                
                # Convert to human-readable format
                balance_eth = float(balance_wei) / 1e18
                balance_str = f"{balance_eth:.18f}".rstrip("0").rstrip(".")
                
                return {
                    "token_type": "native",
                    "token_symbol": chain_info.native_symbol,
                    "token_address": "0x0",
                    "balance": balance_str,
                    "balance_raw": balance_wei,
                    "decimals": 18,
                    "chain_name": chain_info.name,
                    "chain_id": chain_info.chain_id,
                    "error": None,
                }
            
            return {
                "token_type": "native",
                "token_symbol": chain_info.native_symbol,
                "token_address": "0x0",
                "balance": "0",
                "balance_raw": "0",
                "decimals": 18,
                "chain_name": chain_info.name,
                "chain_id": chain_info.chain_id,
                "error": None,
            }
    
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error! status: {e.response.status_code}",
            "token_type": "native",
            "token_symbol": chain_info.native_symbol if chain_info else "ETH",
            "token_address": "0x0",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }
    except Exception as e:
        return {
            "error": f"Error fetching native balance: {str(e)}",
            "token_type": "native",
            "token_symbol": chain_info.native_symbol if chain_info else "ETH",
            "token_address": "0x0",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }


async def get_token_balance_thegraph(
    account_address: str,
    token_symbol: str,
    network: str,
    api_key: Optional[str] = None,
) -> Dict:
    """
    Get balance for a specific ERC-20 token using The Graph API.
    
    Matches the signature pattern of existing balance clients:
    - get_token_balance_ethereum(account_address: str, token_symbol: str) -> dict
    - get_token_balance_polygon(account_address: str, token_symbol: str) -> dict
    
    Args:
        account_address: Wallet address (0x...)
        token_symbol: Token symbol (e.g., "USDC", "DAI")
        network: Network name (ethereum, polygon, base, etc.) or chain ID
        api_key: The Graph API JWT token (optional, uses env var if not provided)
    
    Returns:
        Dictionary with token balance information:
        {
            "token_type": "ERC20",
            "token_symbol": "USDC",
            "token_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "balance": "1000.0",  # Human-readable balance
            "balance_raw": "1000000000",  # Raw balance
            "decimals": 6,
            "usd_value": "1000.00",  # USD value
            "chain_name": "Ethereum",
            "chain_id": "1",
            "error": None  # Error message if any
        }
    """
    if not api_key:
        api_key = os.getenv("THEGRAPH_API_KEY")
    
    if not api_key:
        return {
            "error": "THEGRAPH_API_KEY environment variable is not set",
            "token_type": "ERC20",
            "token_symbol": token_symbol.upper(),
            "token_address": "",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }
    
    chain_info = get_chain_info(network)
    if not chain_info:
        return {
            "error": f"Unsupported network: {network}",
            "token_type": "ERC20",
            "token_symbol": token_symbol.upper(),
            "token_address": "",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }
    
    # Get all tokens and find the one matching the symbol
    all_tokens = await get_all_token_balances_thegraph(
        account_address, network, api_key
    )
    
    if "error" in all_tokens:
        return all_tokens
    
    token_symbol_upper = token_symbol.upper()
    for token in all_tokens.get("tokens", []):
        if token.get("token_symbol", "").upper() == token_symbol_upper:
            return token
    
    return {
        "error": f"Token {token_symbol.upper()} not found for {account_address} on {network}",
        "token_type": "ERC20",
        "token_symbol": token_symbol.upper(),
        "token_address": "",
        "balance": "0",
        "balance_raw": "0",
        "decimals": 18,
    }


async def get_all_token_balances_thegraph(
    account_address: str, network: str, api_key: Optional[str] = None
) -> Dict:
    """
    Get all ERC-20 token balances using The Graph API.
    
    Matches the signature pattern of existing balance clients:
    - get_multiple_token_balances_ethereum(account_address: str, token_symbols: list[str]) -> list[dict]
    
    Args:
        account_address: Wallet address (0x...)
        network: Network name (ethereum, polygon, base, etc.) or chain ID
        api_key: The Graph API JWT token (optional, uses env var if not provided)
    
    Returns:
        Dictionary with all token balances:
        {
            "tokens": [
                {
                    "token_type": "ERC20",
                    "token_symbol": "USDC",
                    "token_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    "balance": "1000.0",
                    "balance_raw": "1000000000",
                    "decimals": 6,
                    "usd_value": "1000.00",
                    "chain_name": "Ethereum",
                    "chain_id": "1",
                    "error": None
                },
                ...
            ],
            "error": None
        }
    """
    if not api_key:
        api_key = os.getenv("THEGRAPH_API_KEY")
    
    if not api_key:
        return {
            "tokens": [],
            "error": "THEGRAPH_API_KEY environment variable is not set",
        }
    
    chain_info = get_chain_info(network)
    if not chain_info:
        return {
            "tokens": [],
            "error": f"Unsupported network: {network}",
        }
    
    all_tokens: List[Dict] = []
    page = 1
    limit = 10
    
    while True:
        try:
            await asyncio.sleep(0.2)  # Rate limiting delay
            
            query_params = {
                "network": chain_info.network_name,
                "address": account_address,
                "limit": str(limit),
                "page": str(page),
                "include_null_balances": "false",
            }
            
            url = "https://token-api.thegraph.com/v1/evm/balances"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=query_params,
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                
                if response.status_code == 401:
                    return {
                        "tokens": [],
                        "error": "The Graph API authentication failed. Please check your API key.",
                    }
                
                if response.status_code == 403:
                    return {
                        "tokens": [],
                        "error": "The Graph API access forbidden. Please check your API key permissions.",
                    }
                
                if response.status_code == 429:
                    await asyncio.sleep(5)  # Wait 5 seconds on rate limit
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if not data.get("data"):
                    break
                
                for balance in data["data"]:
                    decimals = balance.get("decimals", 18)
                    divisor = 10**decimals
                    balance_raw = balance.get("amount", "0")
                    
                    # Format balance
                    balance_num = float(balance_raw) / divisor
                    balance_str = f"{balance_num:.18f}".rstrip("0").rstrip(".")
                    
                    # Calculate USD value
                    price_usd = balance.get("value", 0) or 0
                    usd_value = balance_num * price_usd
                    usd_value_str = f"{usd_value:.2f}"
                    
                    all_tokens.append({
                        "token_type": "ERC20",
                        "token_symbol": balance.get("symbol", "UNKNOWN"),
                        "token_address": balance.get("contract", ""),
                        "token_name": balance.get("name", "Unknown"),
                        "balance": balance_str,
                        "balance_raw": balance_raw,
                        "decimals": decimals,
                        "usd_value": usd_value_str,
                        "chain_name": chain_info.name,
                        "chain_id": chain_info.chain_id,
                        "error": None,
                    })
                
                if len(data["data"]) < limit:
                    break
                
                page += 1
        
        except httpx.HTTPStatusError as e:
            return {
                "tokens": all_tokens,
                "error": f"HTTP error! status: {e.response.status_code}",
            }
        except Exception as e:
            return {
                "tokens": all_tokens,
                "error": f"Error fetching token balances: {str(e)}",
            }
    
    return {
        "tokens": all_tokens,
        "error": None,
    }



