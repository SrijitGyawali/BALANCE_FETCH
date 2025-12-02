"""
Ethereum balance client using The Graph API.

This module provides Ethereum-specific balance fetching functions using The Graph API.
Matches the pattern used by other blockchain balance clients.
"""

import asyncio
import os
from typing import Dict, List, Optional
import httpx
from packages.blockchain.thegraph.utils import get_chain_info


async def get_native_eth_balance_thegraph(
    account_address: str, api_key: Optional[str] = None
) -> Dict:
    """
    Get native ETH balance using The Graph API.
    
    Matches the signature pattern of existing balance clients:
    - get_native_eth_balance(account_address: str) -> dict
    
    Args:
        account_address: Ethereum address (0x...)
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
    
    chain_info = get_chain_info("ethereum")
    if not chain_info:
        return {
            "error": "Ethereum network info not found",
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
                        "chain_name": "Ethereum",
                        "chain_id": "1",
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
                    "chain_name": "Ethereum",
                    "chain_id": "1",
                    "error": None,
                }
            
            return {
                "token_type": "native",
                "token_symbol": "ETH",
                "token_address": "0x0",
                "balance": "0",
                "balance_raw": "0",
                "decimals": 18,
                "chain_name": "Ethereum",
                "chain_id": "1",
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
            "error": f"Error fetching ETH balance: {str(e)}",
            "token_type": "native",
            "token_symbol": "ETH",
            "token_address": "0x0",
            "balance": "0",
            "balance_raw": "0",
            "decimals": 18,
        }


async def get_token_balance_ethereum_thegraph(
    account_address: str, token_symbol: str, api_key: Optional[str] = None
) -> Dict:
    """
    Get balance for a specific ERC-20 token on Ethereum using The Graph API.
    
    Matches the signature pattern of existing balance clients:
    - get_token_balance_ethereum(account_address: str, token_symbol: str) -> dict
    
    Args:
        account_address: Ethereum address (0x...)
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
    all_tokens = await get_multiple_token_balances_ethereum_thegraph(
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
            "chain_name": "Ethereum",
            "chain_id": "1",
        }
    
    token_symbol_upper = token_symbol.upper()
    for token in all_tokens.get("tokens", []):
        if token.get("token_symbol", "").upper() == token_symbol_upper:
            # Ensure token has all required fields
            if "token_type" not in token:
                token["token_type"] = "ERC20"
            if "chain_name" not in token:
                token["chain_name"] = "Ethereum"
            if "chain_id" not in token:
                token["chain_id"] = "1"
            return token
    
    return {
        "error": f"Token {token_symbol.upper()} not found for {account_address} on Ethereum",
        "token_type": "ERC20",
        "token_symbol": token_symbol.upper(),
        "token_address": "",
        "balance": "0",
        "balance_raw": "0",
        "decimals": 18,
        "chain_name": "Ethereum",
        "chain_id": "1",
    }


async def get_multiple_token_balances_ethereum_thegraph(
    account_address: str, token_symbols: Optional[List[str]] = None, api_key: Optional[str] = None
) -> Dict:
    """
    Get all ERC-20 token balances on Ethereum using The Graph API.
    
    Matches the signature pattern of existing balance clients:
    - get_multiple_token_balances_ethereum(account_address: str, token_symbols: list[str]) -> list[dict]
    
    Args:
        account_address: Ethereum address (0x...)
        token_symbols: Optional list of token symbols to filter (if None, returns all)
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
    
    all_tokens: List[Dict] = []
    page = 1
    limit = 10
    max_pages = 50  # Reduced from 100 to limit total requests
    
    # Progress indicator (only print if running in CLI context)
    import sys
    is_cli = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    while page <= max_pages:
        try:
            if is_cli and page == 1:
                print("   📄 Fetching page 1...", end="", flush=True)
            elif is_cli:
                print(f"\r   📄 Fetching page {page}... (found {len(all_tokens)} tokens so far)", end="", flush=True)
            
            await asyncio.sleep(0.5)  # Increased rate limiting delay to 0.5s
            
            query_params = {
                "network": "mainnet",
                "address": account_address,
                "limit": str(limit),
                "page": str(page),
                "include_null_balances": "false",
            }
            
            url = "https://token-api.thegraph.com/v1/evm/balances"
            
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:  # Reduced timeout to 15s per request
                    response = await client.get(
                        url,
                        params=query_params,
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
                # Network error - return what we have so far
                return {
                    "tokens": all_tokens,
                    "error": f"Network error during pagination: {str(e)}",
                }
            
            # Check response status codes
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
                if is_cli:
                    print(f"\r   ⚠️  Rate limited! Waiting 10 seconds...", end="", flush=True)
                await asyncio.sleep(10)  # Increased wait time on rate limit (was 5)
                if is_cli:
                    print(f"\r   🔄 Retrying page {page}...", end="", flush=True)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("data") or len(data["data"]) == 0:
                if is_cli:
                    print()  # New line after progress indicator
                break
                
            page_tokens = len(data["data"])
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
                        "chain_name": "Ethereum",
                        "chain_id": "1",
                        "error": None,
                    }
                    
                    # Filter by token_symbols if provided
                    if token_symbols is None or token_data["token_symbol"].upper() in [t.upper() for t in token_symbols]:
                        all_tokens.append(token_data)
            
            if is_cli:
                print(f"\r   ✅ Page {page}: Found {page_tokens} tokens (Total: {len(all_tokens)})", end="", flush=True)
            
            # Break if we got fewer items than limit (last page)
            if len(data["data"]) < limit:
                if is_cli:
                    print()  # New line after progress indicator
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
    
    if is_cli and len(all_tokens) > 0:
        print()  # Final new line after progress indicators
    
    return {
        "tokens": all_tokens,
        "error": None,
    }



