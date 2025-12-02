#!/usr/bin/env python3
"""
CLI tool to test balance fetching from The Graph API.

Usage:
    python test_balance_cli.py <network> <address> [token_symbol]
    
Examples:
    python test_balance_cli.py ethereum 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
    python test_balance_cli.py polygon 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
    python test_balance_cli.py base 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
    python test_balance_cli.py ethereum 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb USDC
"""

import asyncio
import os
import sys
from typing import Optional


async def test_native_balance(network: str, address: str, api_key: str):
    """Test native balance fetching."""
    print(f"\n{'='*60}")
    print(f"Testing Native Balance Fetching")
    print(f"{'='*60}")
    print(f"Network: {network}")
    print(f"Address: {address}")
    print(f"{'='*60}\n")
    
    try:
        if network.lower() == "ethereum" or network == "1":
            from packages.blockchain.ethereum.balance.balance_client_thegraph import (
                get_native_eth_balance_thegraph,
            )
            print(f"📡 Calling API for native balance...")
            result = await get_native_eth_balance_thegraph(address, api_key)
        elif network.lower() == "polygon" or network == "137":
            from packages.blockchain.polygon.balance.balance_client_thegraph import (
                get_native_matic_balance_thegraph,
            )
            print(f"📡 Calling API for native balance...")
            result = await get_native_matic_balance_thegraph(address, api_key)
        elif network.lower() == "base" or network == "8453":
            from packages.blockchain.base.balance.balance_client_thegraph import (
                get_native_base_balance_thegraph,
            )
            print(f"📡 Calling API for native balance...")
            result = await get_native_base_balance_thegraph(address, api_key)
        else:
            print(f"❌ Unsupported network: {network}")
            print("Supported networks: ethereum, polygon, base")
            return
        
        if result is None:
            print("❌ Error: Function returned None")
            print("  This usually means the API call failed or returned no data")
        elif isinstance(result, dict):
            # Check if there's an actual error (not None)
            error_value = result.get("error")
            if error_value is not None and error_value != "":
                print("❌ Error:")
                print(f"  {error_value}")
            else:
                # No error - display the result
                balance = result.get("balance", "0")
                balance_raw = result.get("balance_raw", "0")
                symbol = result.get("token_symbol", "N/A")
                chain_name = result.get("chain_name", "N/A")
                
                if balance == "0":
                    print("ℹ️  Address has zero native balance (this is valid)")
                else:
                    print("✅ Success!")
                
                # Format balance nicely
                try:
                    balance_num = float(balance)
                    if balance_num >= 1:
                        balance_formatted = f"{balance_num:,.6f}".rstrip('0').rstrip('.')
                    else:
                        balance_formatted = f"{balance_num:.8f}".rstrip('0').rstrip('.')
                except (ValueError, TypeError):
                    balance_formatted = balance
                
                print(f"  Chain: {chain_name}")
                print(f"  Symbol: {symbol}")
                print(f"  Balance: {balance_formatted} {symbol}")
                print(f"  Raw Balance: {balance_raw}")
                print(f"  Decimals: {result.get('decimals', 'N/A')}")
                
                # Show balance in different formats
                if balance != "0":
                    try:
                        balance_num = float(balance)
                        if balance_num >= 1e18:
                            print(f"  Formatted: {balance_num/1e18:.2f} {symbol} (in quintillions)")
                        elif balance_num >= 1e15:
                            print(f"  Formatted: {balance_num/1e15:.2f} {symbol} (in quadrillions)")
                        elif balance_num >= 1e12:
                            print(f"  Formatted: {balance_num/1e12:.2f} {symbol} (in trillions)")
                        elif balance_num >= 1e9:
                            print(f"  Formatted: {balance_num/1e9:.2f} {symbol} (in billions)")
                        elif balance_num >= 1e6:
                            print(f"  Formatted: {balance_num/1e6:.2f} {symbol} (in millions)")
                        elif balance_num >= 1e3:
                            print(f"  Formatted: {balance_num/1e3:.2f} {symbol} (in thousands)")
                    except (ValueError, TypeError):
                        pass
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            print(f"  Result: {result}")
    
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_token_balance(network: str, address: str, token_symbol: str, api_key: str):
    """Test token balance fetching."""
    print(f"\n{'='*60}")
    print(f"Testing Token Balance Fetching")
    print(f"{'='*60}")
    print(f"Network: {network}")
    print(f"Address: {address}")
    print(f"Token: {token_symbol}")
    print(f"{'='*60}\n")
    
    try:
        if network.lower() == "ethereum" or network == "1":
            from packages.blockchain.ethereum.balance.balance_client_thegraph import (
                get_token_balance_ethereum_thegraph,
            )
            print(f"📡 Calling API for token balance...")
            result = await get_token_balance_ethereum_thegraph(address, token_symbol, api_key)
        elif network.lower() == "polygon" or network == "137":
            from packages.blockchain.polygon.balance.balance_client_thegraph import (
                get_token_balance_polygon_thegraph,
            )
            print(f"📡 Calling API for token balance...")
            result = await get_token_balance_polygon_thegraph(address, token_symbol, api_key)
        elif network.lower() == "base" or network == "8453":
            from packages.blockchain.base.balance.balance_client_thegraph import (
                get_token_balance_base_thegraph,
            )
            print(f"📡 Calling API for token balance...")
            result = await get_token_balance_base_thegraph(address, token_symbol, api_key)
        else:
            print(f"❌ Unsupported network: {network}")
            return
        
        if result is None:
            print("❌ Error: Function returned None")
            print("  This usually means the API call failed or returned no data")
        elif isinstance(result, dict):
            # Check if there's an actual error (not None)
            error_value = result.get("error")
            if error_value is not None and error_value != "":
                print("❌ Error:")
                print(f"  {error_value}")
            else:
                print("✅ Success!")
                print(f"  Chain: {result.get('chain_name', 'N/A')}")
                print(f"  Token: {result.get('token_symbol', 'N/A')} ({result.get('token_name', 'N/A')})")
                print(f"  Balance: {result.get('balance', '0')} {result.get('token_symbol', '')}")
                print(f"  USD Value: ${result.get('usd_value', '0')}")
                print(f"  Token Address: {result.get('token_address', 'N/A')}")
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            print(f"  Result: {result}")
    
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_all_tokens(network: str, address: str, api_key: str):
    """Test fetching all token balances."""
    print(f"\n{'='*60}")
    print(f"Testing All Token Balances Fetching")
    print(f"{'='*60}")
    print(f"Network: {network}")
    print(f"Address: {address}")
    print(f"{'='*60}\n")
    print("⚠️  Note: This may take 1-2 minutes if the address has many tokens...")
    print("    (The API uses pagination - 10 tokens per page)\n")
    
    try:
        if network.lower() == "ethereum" or network == "1":
            from packages.blockchain.ethereum.balance.balance_client_thegraph import (
                get_multiple_token_balances_ethereum_thegraph,
            )
            print(f"📡 Calling API for all token balances (this may take a while)...")
            print("   Fetching tokens page by page...")
            
            # Add timeout wrapper
            import asyncio
            try:
                result = await asyncio.wait_for(
                    get_multiple_token_balances_ethereum_thegraph(address, api_key=api_key),
                    timeout=120.0  # 2 minute total timeout
                )
            except asyncio.TimeoutError:
                print("\n❌ Timeout: The API call took too long (>2 minutes)")
                print("   This usually means:")
                print("   - The address has many tokens (100+)")
                print("   - The API is slow or rate-limited")
                print("   - Network connection issues")
                print("\n💡 Tip: Try fetching a specific token instead:")
                print(f"   python3 test_balance_cli.py {network} {address} --token USDC")
                return
        elif network.lower() == "polygon" or network == "137":
            from packages.blockchain.polygon.balance.balance_client_thegraph import (
                get_multiple_token_balances_polygon_thegraph,
            )
            print(f"📡 Calling API for all token balances (this may take a while)...")
            print("   Fetching tokens page by page...")
            
            # Add timeout wrapper
            import asyncio
            try:
                result = await asyncio.wait_for(
                    get_multiple_token_balances_polygon_thegraph(address, api_key=api_key),
                    timeout=120.0  # 2 minute total timeout
                )
            except asyncio.TimeoutError:
                print("\n❌ Timeout: The API call took too long (>2 minutes)")
                print("   This usually means the address has many tokens or the API is slow")
                return
        elif network.lower() == "base" or network == "8453":
            from packages.blockchain.base.balance.balance_client_thegraph import (
                get_multiple_token_balances_base_thegraph,
            )
            print(f"📡 Calling API for all token balances (this may take a while)...")
            print("   Fetching tokens page by page...")
            
            # Add timeout wrapper
            import asyncio
            try:
                result = await asyncio.wait_for(
                    get_multiple_token_balances_base_thegraph(address, api_key=api_key),
                    timeout=120.0  # 2 minute total timeout
                )
            except asyncio.TimeoutError:
                print("\n❌ Timeout: The API call took too long (>2 minutes)")
                print("   This usually means the address has many tokens or the API is slow")
                return
        else:
            print(f"❌ Unsupported network: {network}")
            return
        
        if result is None:
            print("❌ Error: Function returned None")
            print("  This usually means the API call failed or returned no data")
        elif isinstance(result, dict):
            # Check if there's an actual error (not None)
            error_value = result.get("error")
            if error_value is not None and error_value != "":
                print("❌ Error:")
                print(f"  {error_value}")
            else:
                tokens = result.get("tokens", [])
                print(f"✅ Success! Found {len(tokens)} token(s)\n")
                
                if tokens:
                    total_usd = 0.0
                    
                    # Create a table-like display
                    print(f"{'Token Name':<30} {'Symbol':<10} {'Balance':<25} {'Price (USD)':<15} {'Value (USD)':<15}")
                    print("-" * 95)
                    
                    for token in tokens:
                        # Handle None values properly - dict.get() returns None if key exists with None value
                        token_name_raw = token.get('token_name') or token.get('TokenName')
                        token_name = (str(token_name_raw)[:28] if token_name_raw else 'Unknown')
                        token_symbol = token.get('token_symbol') or token.get('TokenSymbol') or 'N/A'
                        balance = token.get('balance') or token.get('TokenQuantity') or '0'
                        usd_value_str = token.get('usd_value') or token.get('TokenPriceUSD') or '0'
                        
                        # Calculate price per token
                        try:
                            balance_num = float(balance) if balance else 0
                            usd_value_num = float(usd_value_str) if usd_value_str else 0
                            if balance_num > 0:
                                price_per_token = usd_value_num / balance_num
                                price_str = f"${price_per_token:.6f}"
                            else:
                                price_str = "$0.00"
                        except (ValueError, TypeError, ZeroDivisionError):
                            price_str = "$0.00"
                        
                        # Format balance (remove excessive decimals)
                        try:
                            balance_num = float(balance)
                            if balance_num >= 1:
                                balance_formatted = f"{balance_num:,.6f}".rstrip('0').rstrip('.')
                            else:
                                balance_formatted = f"{balance_num:.8f}".rstrip('0').rstrip('.')
                        except (ValueError, TypeError):
                            balance_formatted = balance
                        
                        # Format USD value
                        try:
                            usd_value_num = float(usd_value_str)
                            if usd_value_num >= 1000:
                                usd_formatted = f"${usd_value_num:,.2f}"
                            else:
                                usd_formatted = f"${usd_value_num:.2f}"
                        except (ValueError, TypeError):
                            usd_formatted = f"${usd_value_str}"
                        
                        print(f"{token_name:<30} {token_symbol:<10} {balance_formatted:<25} {price_str:<15} {usd_formatted:<15}")
                        
                        try:
                            if usd_value_str:
                                total_usd += float(usd_value_str)
                        except (ValueError, TypeError):
                            pass
                    
                    print("-" * 95)
                    if total_usd >= 1000:
                        print(f"{'TOTAL USD VALUE':<30} {'':<10} {'':<25} {'':<15} ${total_usd:,.2f}")
                    else:
                        print(f"{'TOTAL USD VALUE':<30} {'':<10} {'':<25} {'':<15} ${total_usd:.2f}")
                    
                    # Also show detailed view
                    print(f"\n{'='*60}")
                    print("Detailed Token Information:")
                    print(f"{'='*60}\n")
                    
                    for i, token in enumerate(tokens, 1):
                        # Handle None values and different field names
                        token_name = token.get('token_name') or token.get('TokenName') or 'Unknown'
                        token_symbol = token.get('token_symbol') or token.get('TokenSymbol') or 'N/A'
                        token_address = token.get('token_address') or token.get('TokenAddress') or 'N/A'
                        balance = token.get('balance') or token.get('TokenQuantity') or '0'
                        balance_raw = token.get('balance_raw') or token.get('TokenQuantity') or '0'
                        decimals = token.get('decimals') or token.get('TokenDivisor') or 'N/A'
                        usd_value = token.get('usd_value') or token.get('TokenPriceUSD') or '0'
                        
                        print(f"{i}. {token_name} ({token_symbol})")
                        print(f"   Contract Address: {token_address}")
                        print(f"   Balance: {balance} {token_symbol}")
                        print(f"   Raw Balance: {balance_raw}")
                        print(f"   Decimals: {decimals}")
                        print(f"   USD Value: ${usd_value}")
                        
                        # Calculate and show price
                        try:
                            balance_val = token.get('balance') or token.get('TokenQuantity') or '0'
                            usd_value_val = token.get('usd_value') or token.get('TokenPriceUSD') or '0'
                            balance_num = float(balance_val) if balance_val else 0
                            usd_value_num = float(usd_value_val) if usd_value_val else 0
                            if balance_num > 0:
                                price_per_token = usd_value_num / balance_num
                                print(f"   Price per Token: ${price_per_token:.6f}")
                        except (ValueError, TypeError, ZeroDivisionError):
                            pass
                        
                        print()
                else:
                    print("No tokens found for this address.")
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            print(f"  Result: {result}")
    
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()


def load_env_file():
    """Load environment variables from .env file."""
    env_file = ".env"
    if not os.path.exists(env_file):
        env_file = ".env.local"
    
    if os.path.exists(env_file):
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue
                    # Handle both "KEY=value" and "export KEY=value" formats
                    if line.startswith("export "):
                        line = line[7:]  # Remove "export "
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        # Only set if not already in environment
                        if key and value and not os.getenv(key):
                            os.environ[key] = value
        except Exception as e:
            print(f"⚠️  Warning: Could not load .env file: {e}")


async def main():
    """Main function."""
    # Load .env file first
    load_env_file()
    
    # Check for API key
    api_key = os.getenv("THEGRAPH_API_KEY")
    if not api_key:
        print("❌ Error: THEGRAPH_API_KEY environment variable is not set")
        print("\nPlease set it with:")
        print("  export THEGRAPH_API_KEY=your_jwt_token_here")
        print("\nOr add it to your .env or .env.local file (without 'export'):")
        print("  THEGRAPH_API_KEY=your_jwt_token_here")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Parse arguments
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    network = sys.argv[1]
    address = sys.argv[2]
    token_symbol = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Validate address format
    if not address.startswith("0x") or len(address) != 42:
        print(f"❌ Invalid address format: {address}")
        print("Address should be a valid Ethereum address (0x followed by 40 hex characters)")
        sys.exit(1)
    
    # Run tests
    if token_symbol:
        # Test specific token
        await test_token_balance(network, address, token_symbol, api_key)
    else:
        # Test native balance and all tokens
        await test_native_balance(network, address, api_key)
        print("\n")
        await test_all_tokens(network, address, api_key)
    
    print(f"\n{'='*60}")
    print("Test completed!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())

