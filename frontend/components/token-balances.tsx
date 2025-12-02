'use client';

import { useState, useEffect } from 'react';
import { useAccount } from 'wagmi';
import {
  fetchMultiChainBalancesViaTheGraph,
  formatTokenBalance,
  calculateUSDValue,
  formatUSDValue,
  formatLargeNumber,
  TokenBalance,
  NativeBalance,
} from '@/lib/thegraph-api';

interface TokenBalancesProps {
  apiKey: string;
}

interface ChainBalances {
  chainId: string;
  chainName: string;
  tokens: TokenBalance[];
  nativeBalance: NativeBalance | null;
  chainTotalUSD: number;
}

/**
 * Component to display all token balances for connected wallet across multiple chains
 */
export function TokenBalances({ apiKey }: TokenBalancesProps): JSX.Element {
  const { address, isConnected } = useAccount();
  const [chainBalances, setChainBalances] = useState<ChainBalances[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [totalUSD, setTotalUSD] = useState<number>(0);

  useEffect(() => {
    if (isConnected && address && apiKey) {
      loadMultiChainBalances();
    } else {
      setChainBalances([]);
      setTotalUSD(0);
    }
  }, [isConnected, address, apiKey]);

  async function loadMultiChainBalances(): Promise<void> {
    if (!address || !apiKey) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await fetchMultiChainBalancesViaTheGraph(address, apiKey);
      const tokens: TokenBalance[] = result.tokens;
      const nativeBalances: NativeBalance[] = result.nativeBalances;

      const chainMap = new Map<string, ChainBalances>();

      tokens.forEach((token) => {
        const chainId = token.chainId || '1';
        if (!chainMap.has(chainId)) {
          chainMap.set(chainId, {
            chainId,
            chainName: token.chainName || `Chain ${chainId}`,
            tokens: [],
            nativeBalance: null,
            chainTotalUSD: 0,
          });
        }
        const chainData = chainMap.get(chainId)!;
        chainData.tokens.push(token);
      });

      nativeBalances.forEach((native) => {
        if (!chainMap.has(native.chainId)) {
          chainMap.set(native.chainId, {
            chainId: native.chainId,
            chainName: native.chainName,
            tokens: [],
            nativeBalance: native,
            chainTotalUSD: 0,
          });
        } else {
          const chainData = chainMap.get(native.chainId)!;
          chainData.nativeBalance = native;
        }
      });

      const chains: ChainBalances[] = Array.from(chainMap.values()).map((chain) => {
        const tokenTotal = chain.tokens.reduce((sum, token) => {
          const balance = formatTokenBalance(token.TokenQuantity, token.TokenDivisor);
          const usdValue = calculateUSDValue(balance, token.TokenPriceUSD);
          return sum + usdValue;
        }, 0);

        const nativeValue = chain.nativeBalance
          ? parseFloat(chain.nativeBalance.balance) / 1e18 * parseFloat(chain.nativeBalance.priceUSD || '0')
          : 0;

        return {
          ...chain,
          chainTotalUSD: tokenTotal + nativeValue,
        };
      });

      chains.sort((a, b) => b.chainTotalUSD - a.chainTotalUSD);

      setChainBalances(chains);

      const total = chains.reduce((sum, chain) => sum + chain.chainTotalUSD, 0);
      setTotalUSD(total);
      console.log('📊 Final state:', { 
        chainCount: chains.length, 
        totalUSD, 
        chains: chains.map(c => ({ chain: c.chainName, tokens: c.tokens.length, native: !!c.nativeBalance }))
      });
    } catch (err) {
      console.error('❌ Error fetching balances:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch token balances';
      
      if (errorMessage.includes('authentication failed') || errorMessage.includes('Invalid') || errorMessage.includes('API key')) {
        setError('The Graph API authentication failed. Please check your NEXT_PUBLIC_THEGRAPH_API_KEY in .env.local file.');
      } else if (errorMessage.includes('rate limit')) {
        setError('The Graph API rate limit exceeded. Please wait a moment and try again.');
      } else {
        setError(errorMessage);
      }
      
      console.error('Error loading multi-chain balances:', err);
    } finally {
      setIsLoading(false);
    }
  }

  if (!isConnected) {
    return (
      <div className="token-balances-empty">
        <p>Please connect your wallet to view token balances</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="token-balances-loading">
        <p>Loading token balances...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="token-balances-error">
        <p>Error: {error}</p>
        <button onClick={loadMultiChainBalances}>Retry</button>
      </div>
    );
  }

  if (chainBalances.length === 0 && !isLoading) {
    return (
      <div className="token-balances-empty">
        <p>No tokens found for this address across supported chains</p>
      </div>
    );
  }

  return (
    <div className="token-balances">
      <div className="token-balances-header">
        <h2>Multi-Chain Token Holdings</h2>
            <p className="total-usd">Total Value: {formatUSDValue(totalUSD)}</p>
      </div>
      <div className="chains-list">
        {chainBalances.map((chain) => (
          <div key={chain.chainId} className="chain-section">
            <div className="chain-header">
              <h3>{chain.chainName}</h3>
              <p className="chain-total">Chain Total: {formatUSDValue(chain.chainTotalUSD)}</p>
            </div>
            <div className="token-list">
              {chain.nativeBalance && (
                <div className="native-balance">
                  <span className="token-name">{chain.nativeBalance.symbol} (Native)</span>
                  <span className="token-balance">
                    {formatLargeNumber(parseFloat(chain.nativeBalance.balance) / 1e18, 8)} {chain.nativeBalance.symbol}
                  </span>
                </div>
              )}
              {!chain.nativeBalance && (
                <div className="native-balance zero-balance">
                  <span className="token-name">Native Token</span>
                  <span className="token-balance">0 (No native balance found)</span>
                </div>
              )}
              {chain.tokens.length > 0 && (
                <table>
                  <thead>
                    <tr>
                      <th>Token</th>
                      <th>Symbol</th>
                      <th>Balance</th>
                      <th>Price (USD)</th>
                      <th>Value (USD)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chain.tokens.map((token) => {
                      const balance = formatTokenBalance(token.TokenQuantity, token.TokenDivisor);
                      const price = parseFloat(token.TokenPriceUSD);
                      const usdValue = calculateUSDValue(balance, token.TokenPriceUSD);
                      const balanceNum = parseFloat(balance);

                      return (
                        <tr key={`${chain.chainId}-${token.TokenAddress}`}>
                          <td>{token.TokenName || 'Unknown'}</td>
                          <td>{token.TokenSymbol}</td>
                          <td>{isFinite(balanceNum) ? formatLargeNumber(balanceNum, 8) : balance}</td>
                          <td>{isFinite(price) ? formatUSDValue(price, 6).replace('$', '') : '$0.00'}</td>
                          <td>{formatUSDValue(usdValue)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
              {chain.tokens.length === 0 && !chain.nativeBalance && (
                <p className="no-tokens">No tokens found on this chain</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}




