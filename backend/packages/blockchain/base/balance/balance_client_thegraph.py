"""
Base balance client using The Graph API.

This module provides Base-specific balance fetching functions using The Graph API.
Matches the pattern used by other blockchain balance clients.
"""

import asyncio
import os
from typing import Dict, List, Optional
import httpx
from packages.blockchain.thegraph.utils import get_chain_info


async def get_native_base_balance_thegraph(
    account_address: str, api_key: Optional[str] = None
) -> Dict:
    """
    Get native ETH balance on Base using The Graph API.
    
    Matches the signature pattern of existing balance clients.
    
    Args:
        account_address: Base address (0x...)
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
            "chain_name": "Base",
            "chain_id": "8453",
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
    
    chain_info = get_chain_info("base")
    if not chain_info:
        return {
            "error": "Base network info not found",
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
                    "token_symbol": "ETH",
                    "token_address": "0x0",
                    "balance": "0",
                    "balance_raw": "0",
                    "decimals": 18,
                }
            
            if response.status_code == 403:
                return {
                    "error": "The Graph API access forbidden. Please check your API key permissions.",
                    "token_type": "native",
                    "token_symbol": "ETH",
                    "token_address": "0x0",
                    "balance": "0",
                    "balance_raw": "0",
                    "decimals": 18,
                }
            
            if response.status_code == 429:
                return {
                    "error": "The Graph API rate limit exceeded. Please wait and try again.",
                    "token_type": "native",
                    "token_symbol": "ETH",
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
                        "token_symbol": "ETH",
                        "token_address": "0x0",
                        "balance": "0",
                        "balance_raw": "0",
                        "decimals": 18,
                        "chain_name": "Base",
                        "chain_id": "8453",
                        "error": None,
                    }
                
                # Convert to human-readable format
                balance_eth = float(balance_wei) / 1e18
                balance_str = f"{balance_eth:.18f}".rstrip("0").rstrip(".")
                
                return {
                    "token_type": "native",
                    "token_symbol": "ETH",
                    "token_address": "0x0",
                    "balance": balance_str,
                    "balance_raw": balance_wei,
                    "decimals": 18,
                    "chain_name": "Base",
                    "chain_id": "8453",
                    "error": None,
                }
            
            return {
                "token_type": "native",
                "token_symbol": "ETH",
                "token_address": "0x0",
                "balance": "0",
                "balance_raw": "0",
                "decimals": 18,
                "chain_name": "Base",
                "chain_id": "8453",
                "error": None,
            }
    
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error! status: {e.response.status_code}",
            "token_type": "native",
            "token_symbol": "ETH",
            "token_address": "0x0",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }
    except Exception as e:
        return {
            "error": f"Error fetching Base ETH balance: {str(e)}",
            "token_type": "native",
            "token_symbol": "ETH",
            "token_address": "0x0",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }


async def get_token_balance_base_thegraph(
    account_address: str, token_symbol: str, api_key: Optional[str] = None
) -> Dict:
    """
    Get balance for a specific ERC-20 token on Base using The Graph API.
    
    Args:
        account_address: Base address (0x...)
        token_symbol: Token symbol (e.g., "USDC", "DAI")
        api_key: The Graph API JWT token (optional, uses env var if not provided)
    
    Returns:
        Dictionary with token balance information
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
    
    # Get all tokens and find the one matching the symbol
    all_tokens = await get_multiple_token_balances_base_thegraph(
        account_address, api_key=api_key
    )
    
    if "error" in all_tokens and all_tokens.get("error"):
        # If there's an error, return it with proper structure
        return {
            "error": all_tokens.get("error"),
            "token_type": "ERC20",
            "token_symbol": token_symbol.upper(),
            "token_address": "",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
            "chain_name": "Base",
            "chain_id": "8453",
        }
    
    token_symbol_upper = token_symbol.upper()
    for token in all_tokens.get("tokens", []):
        token_sym = token.get("token_symbol") or ""
        if isinstance(token_sym, str) and token_sym.upper() == token_symbol_upper:
            # Ensure token has all required fields
            if "token_type" not in token:
                token["token_type"] = "ERC20"
            if "chain_name" not in token:
                token["chain_name"] = "Base"
            if "chain_id" not in token:
                token["chain_id"] = "8453"
            return token
    
    return {
        "error": f"Token {token_symbol.upper()} not found for {account_address} on Base",
        "token_type": "ERC20",
        "token_symbol": token_symbol.upper(),
        "token_address": "",
        "balance": "0",
        "balance_raw": "0",
        "decimals": 18,
        "chain_name": "Base",
        "chain_id": "8453",
    }


async def get_multiple_token_balances_base_thegraph(
    account_address: str, token_symbols: Optional[List[str]] = None, api_key: Optional[str] = None
) -> Dict:
    """
    Get all ERC-20 token balances on Base using The Graph API.
    
    Args:
        account_address: Base address (0x...)
        token_symbols: Optional list of token symbols to filter (if None, returns all)
        api_key: The Graph API JWT token (optional, uses env var if not provided)
    
    Returns:
        Dictionary with all token balances
    """
    if not api_key:
        api_key = os.getenv("THEGRAPH_API_KEY")
    
    if not api_key:
        return {
            "tokens": [],
            "error": "THEGRAPH_API_KEY environment variable is not set",
        }
    
    all_tokens: List[Dict] = []
    page = 1
    limit = 10
    max_pages = 100  # Safety limit to prevent infinite loops
    
    while page <= max_pages:
        try:
            await asyncio.sleep(0.2)  # Rate limiting delay
            
            query_params = {
                "network": "base",
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
                    
                    token_data = {
                        "token_type": "ERC20",
                        "token_symbol": balance.get("symbol", "UNKNOWN"),
                        "token_address": balance.get("contract", ""),
                        "token_name": balance.get("name", "Unknown"),
                        "balance": balance_str,
                        "balance_raw": balance_raw,
                        "decimals": decimals,
                        "usd_value": usd_value_str,
                        "chain_name": "Base",
                        "chain_id": "8453",
                        "error": None,
                    }
                    
                    # Filter by token_symbols if provided
                    if token_symbols is None or token_data["token_symbol"].upper() in [t.upper() for t in token_symbols]:
                        all_tokens.append(token_data)
                
                # Break if we got fewer items than limit (last page)
                if len(data["data"]) < limit:
                    break
                
                # Break if we got no items
                if len(data["data"]) == 0:
                    break
                
                page += 1
        
        except httpx.TimeoutException:
            return {
                "tokens": all_tokens,
                "error": "Request timeout. The API took too long to respond.",
            }
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
    
    # If we hit max pages, return what we have with a warning
    if page > max_pages:
        return {
            "tokens": all_tokens,
            "error": f"Reached maximum page limit ({max_pages}). There may be more tokens. Consider filtering by token_symbols.",
        }
    
    return {
        "tokens": all_tokens,
        "error": None,
    }



