'use client';

import { useState } from 'react';
import {
  fetchMultiChainBalancesViaTheGraph,
  formatTokenBalance,
  calculateUSDValue,
  formatUSDValue,
  formatLargeNumber,
  TokenBalance,
  NativeBalance,
} from '@/lib/thegraph-api';

interface ChainBalances {
  chainId: string;
  chainName: string;
  tokens: TokenBalance[];
  nativeBalance: NativeBalance | null;
  chainTotalUSD: number;
}

interface AddressCheckerProps {
  apiKey: string;
}

export function AddressChecker({ apiKey }: AddressCheckerProps): JSX.Element {
  const [address, setAddress] = useState<string>('');
  const [chainBalances, setChainBalances] = useState<ChainBalances[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [totalUSD, setTotalUSD] = useState<number>(0);
  const [checkedAddress, setCheckedAddress] = useState<string>('');

  function isValidAddress(addr: string): boolean {
    return /^0x[a-fA-F0-9]{40}$/.test(addr);
  }

  async function checkAddress(): Promise<void> {
    if (!address || !apiKey) {
      setError('Please enter an address and ensure API key is configured');
      return;
    }

    if (!isValidAddress(address)) {
      setError('Invalid Ethereum address format. Please enter a valid 0x address.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setCheckedAddress(address);

    try {
      console.log('🔍 Checking address:', address);
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
    } catch (err) {
      console.error('❌ Error checking address:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch balances';
      
      if (errorMessage.includes('authentication failed') || errorMessage.includes('Invalid') || errorMessage.includes('API key')) {
        setError('The Graph API authentication failed. Please check your NEXT_PUBLIC_THEGRAPH_API_KEY in .env.local file.');
      } else if (errorMessage.includes('rate limit')) {
        setError('The Graph API rate limit exceeded. Please wait a moment and try again.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyPress(e: React.KeyboardEvent<HTMLInputElement>): void {
    if (e.key === 'Enter') {
      checkAddress();
    }
  }

  return (
    <div className="address-checker">
      <div className="address-checker-header">
        <h2>Check Any Address</h2>
        <p className="description">Enter an Ethereum address to view its balances across all supported chains</p>
      </div>

      <div className="address-input-section">
        <input
          type="text"
          placeholder="0x..."
          value={address}
          onChange={(e) => setAddress(e.target.value.trim())}
          onKeyPress={handleKeyPress}
          className="address-input"
          disabled={isLoading}
        />
        <button
          onClick={checkAddress}
          disabled={isLoading || !address || !isValidAddress(address)}
          className="check-button"
        >
          {isLoading ? 'Checking...' : 'Check Address'}
        </button>
      </div>

      {error && (
        <div className="address-checker-error">
          <p>Error: {error}</p>
          <button onClick={checkAddress}>Retry</button>
        </div>
      )}

      {checkedAddress && !isLoading && (
        <div className="checked-address-info">
          <p>Checking: <code>{checkedAddress}</code></p>
        </div>
      )}

      {chainBalances.length > 0 && !isLoading && (
        <div className="address-balances-results">
      {totalUSD > 0 && (
        <div className="total-usd">
          <h3>Total Value: {formatUSDValue(totalUSD)}</h3>
        </div>
      )}

          {chainBalances.map((chain) => (
            <div key={chain.chainId} className="chain-balance-section">
              <h3 className="chain-name">{chain.chainName}</h3>

              {chain.nativeBalance ? (
                <div className="native-balance">
                  <p>
                    <strong>Native Balance ({chain.nativeBalance.symbol}):</strong>{' '}
                    {formatLargeNumber(parseFloat(chain.nativeBalance.balance) / 1e18, 8)}{' '}
                    {chain.nativeBalance.symbol}
                  </p>
                </div>
              ) : (
                <div className="native-balance zero-balance">
                  <p>
                    <strong>Native Balance:</strong> 0 (No native balance found)
                  </p>
                </div>
              )}

              {chain.tokens.length > 0 ? (
                <div className="tokens-list">
                  <h4>Tokens ({chain.tokens.length}):</h4>
                  <ul>
                    {chain.tokens.map((token, index) => {
                      const balance = formatTokenBalance(token.TokenQuantity, token.TokenDivisor);
                      const usdValue = calculateUSDValue(balance, token.TokenPriceUSD);
                      const balanceNum = parseFloat(balance);
                      return (
                        <li key={index} className="token-item">
                          <div className="token-info">
                            <span className="token-symbol">{token.TokenSymbol}</span>
                            <span className="token-name">{token.TokenName}</span>
                          </div>
                          <div className="token-balance">
                            <span>{isFinite(balanceNum) ? formatLargeNumber(balanceNum, 8) : balance}</span>
                            {usdValue > 0 && usdValue < 1e15 && (
                              <span className="token-usd">{formatUSDValue(usdValue)}</span>
                            )}
                            {usdValue >= 1e15 && (
                              <span className="token-usd token-usd-warning" title="Suspiciously large value - may be a scam token">
                                {formatUSDValue(usdValue)}
                              </span>
                            )}
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : (
                <p className="no-tokens">No tokens found on this chain</p>
              )}

              <div className="chain-total">
                <p>Chain Total: {formatUSDValue(chain.chainTotalUSD)}</p>
              </div>
            </div>
          ))}

          {chainBalances.length === 0 && (
            <p className="no-balances">No balances found for this address</p>
          )}
        </div>
      )}
    </div>
  );
}


