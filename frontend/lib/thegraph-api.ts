interface TokenBalance {
  TokenAddress: string;
  TokenName: string;
  TokenSymbol: string;
  TokenQuantity: string;
  TokenDivisor: string;
  TokenPriceUSD: string;
  chainId?: string;
  chainName?: string;
}

interface NativeBalance {
  chainId: string;
  chainName: string;
  balance: string;
  symbol: string;
  priceUSD: string;
}

interface TheGraphTokenBalance {
  last_update: string;
  last_update_block_num: number;
  last_update_timestamp: number;
  address: string;
  contract: string;
  amount: string;
  value: number;
  name: string;
  symbol: string;
  decimals: number;
  network: string;
}

interface TheGraphTokenResponse {
  data: TheGraphTokenBalance[];
}

interface TheGraphNativeBalance {
  address: string;
  balance: string;
  network: string;
}

interface TheGraphNativeResponse {
  data: TheGraphNativeBalance[];
}

interface ChainInfo {
  chainId: string;
  name: string;
  nativeSymbol: string;
  networkName: string;
}

export const SUPPORTED_CHAINS: ChainInfo[] = [
  { chainId: '1', name: 'Ethereum', nativeSymbol: 'ETH', networkName: 'mainnet' },
];

/**
 * Fetches native token balance using The Graph API
 * @param address - Wallet address
 * @param apiKey - The Graph API key
 * @param chainId - Chain ID
 * @returns Promise with native balance information
 */
export async function fetchNativeBalanceViaTheGraph(
  address: string,
  apiKey: string,
  chainId: string,
): Promise<NativeBalance | null> {
  if (!apiKey) {
    throw new Error('The Graph API key is required');
  }

  const chainInfo = SUPPORTED_CHAINS.find((chain) => chain.chainId === chainId);
  if (!chainInfo) {
    return null;
  }

  const queryParams = new URLSearchParams({
    network: chainInfo.networkName,
    address: address,
    include_null_balances: 'false',
    limit: '10',
    page: '1',
  });
  const url = `https://token-api.thegraph.com/v1/evm/balances/native?${queryParams.toString()}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('The Graph API authentication failed. Please check your API key.');
      }
      if (response.status === 403) {
        throw new Error('The Graph API access forbidden. Please check your API key permissions.');
      }
      if (response.status === 429) {
        throw new Error('The Graph API rate limit exceeded. Please wait and try again.');
      }
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const data: TheGraphNativeResponse = await response.json();

    if (data.data && Array.isArray(data.data) && data.data.length > 0) {
      const nativeBalance = data.data[0];
      if (nativeBalance.balance) {
        const balanceWei = nativeBalance.balance;
        const balanceEth = parseFloat(balanceWei) / 1e18;

        if (balanceEth === 0) {
          return null;
        }

        return {
          chainId,
          chainName: chainInfo.name,
          balance: balanceWei,
          symbol: chainInfo.nativeSymbol,
          priceUSD: '0',
        };
      }
    }

    return null;
  } catch (error) {
    console.error(`Error fetching native balance via The Graph for chain ${chainId}:`, error);
    return null;
  }
}

/**
 * Fetches ERC-20 token balances using The Graph API
 * @param address - Wallet address
 * @param apiKey - The Graph API key
 * @param chainId - Chain ID
 * @param limit - Number of items per query (max 10 for free tier)
 * @param page - Page number for pagination
 * @returns Promise with array of token balances
 */
export async function fetchTokenBalancesViaTheGraph(
  address: string,
  apiKey: string,
  chainId: string,
  limit: number = 10,
  page: number = 1,
): Promise<TokenBalance[]> {
  if (!apiKey) {
    throw new Error('The Graph API key is required');
  }

  const chainInfo = SUPPORTED_CHAINS.find((chain) => chain.chainId === chainId);
  if (!chainInfo) {
    return [];
  }

  const queryParams = new URLSearchParams({
    network: chainInfo.networkName,
    address: address,
    limit: limit.toString(),
    page: page.toString(),
    include_null_balances: 'false',
  });
  const url = `https://token-api.thegraph.com/v1/evm/balances?${queryParams.toString()}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('The Graph API authentication failed. Please check your API key.');
      }
      if (response.status === 403) {
        throw new Error('The Graph API access forbidden. Please check your API key permissions.');
      }
      if (response.status === 429) {
        throw new Error('The Graph API rate limit exceeded. Please wait and try again.');
      }
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const data: TheGraphTokenResponse = await response.json();

    if (data.data && Array.isArray(data.data)) {
      const tokens: TokenBalance[] = data.data.map((balance) => {
        const decimals = balance.decimals || 18;
        const divisor = Math.pow(10, decimals).toString();

        return {
          TokenAddress: balance.contract,
          TokenName: balance.name || 'Unknown',
          TokenSymbol: balance.symbol || 'UNKNOWN',
          TokenQuantity: balance.amount,
          TokenDivisor: divisor,
          TokenPriceUSD: balance.value?.toString() || '0',
          chainId,
          chainName: chainInfo.name,
        };
      });

      return tokens;
    }

    return [];
  } catch (error) {
    console.error(`Error fetching token balances via The Graph for chain ${chainId}:`, error);
    throw error;
  }
}

/**
 * Fetches all token balances across multiple pages using The Graph API
 * @param address - Wallet address
 * @param apiKey - The Graph API key
 * @param chainId - Chain ID
 * @returns Promise with array of all token balances
 */
export async function fetchAllTokenBalancesViaTheGraph(
  address: string,
  apiKey: string,
  chainId: string,
): Promise<TokenBalance[]> {
  const allTokens: TokenBalance[] = [];
  let page = 1;
  const limit = 10;

  while (true) {
    try {
      const tokens = await fetchTokenBalancesViaTheGraph(address, apiKey, chainId, limit, page);

      if (tokens.length === 0) {
        break;
      }

      allTokens.push(...tokens);

      if (tokens.length < limit) {
        break;
      }

      page++;
      await new Promise((resolve) => setTimeout(resolve, 200));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage.includes('rate limit')) {
        console.warn('Rate limit hit. Waiting 5 seconds...');
        await new Promise((resolve) => setTimeout(resolve, 5000));
        continue;
      }
      throw error;
    }
  }

  return allTokens;
}

/**
 * Fetches token balances across all supported chains using The Graph API
 * @param address - Wallet address
 * @param apiKey - The Graph API key
 * @returns Promise with array of token balances from all chains
 */
export async function fetchMultiChainBalancesViaTheGraph(
  address: string,
  apiKey: string,
): Promise<{ tokens: TokenBalance[]; nativeBalances: NativeBalance[] }> {
  const allTokens: TokenBalance[] = [];
  const nativeBalances: NativeBalance[] = [];

  for (const chain of SUPPORTED_CHAINS) {
    try {
      await new Promise((resolve) => setTimeout(resolve, 200));

      console.log(`[${chain.name}] Fetching native balance via The Graph...`);
      const nativeBalance = await fetchNativeBalanceViaTheGraph(address, apiKey, chain.chainId);
      if (nativeBalance) {
        nativeBalances.push(nativeBalance);
        const balanceEth = (parseFloat(nativeBalance.balance) / 1e18).toFixed(6);
        console.log(`✓ [${chain.name}] Native balance: ${balanceEth} ${nativeBalance.symbol}`);
      }

      await new Promise((resolve) => setTimeout(resolve, 200));

      console.log(`[${chain.name}] Fetching token balances via The Graph...`);
      const tokens = await fetchAllTokenBalancesViaTheGraph(address, apiKey, chain.chainId);
      if (tokens.length > 0) {
        allTokens.push(...tokens);
        console.log(`✓ [${chain.name}] Found ${tokens.length} token(s)`);
      } else {
        console.log(`ℹ [${chain.name}] No tokens found`);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.warn(`⚠ [${chain.name}] Error: ${errorMessage}`);
    }
  }

  return { tokens: allTokens, nativeBalances };
}

/**
 * Formats token quantity based on divisor
 * @param quantity - Raw token quantity string
 * @param divisor - Token divisor (decimals)
 * @returns Formatted token balance
 */
export function formatTokenBalance(quantity: string, divisor: string): string {
  const divisorNum = parseInt(divisor, 10);
  const quantityNum = BigInt(quantity);
  const divisorBigInt = BigInt(10 ** divisorNum);
  const wholePart = quantityNum / divisorBigInt;
  const fractionalPart = quantityNum % divisorBigInt;

  if (fractionalPart === BigInt(0)) {
    return wholePart.toString();
  }

  const fractionalStr = fractionalPart.toString().padStart(divisorNum, '0');
  const trimmedFractional = fractionalStr.replace(/0+$/, '');
  return `${wholePart}.${trimmedFractional}`;
}

/**
 * Calculates USD value of token balance
 * @param balance - Formatted token balance
 * @param priceUSD - Token price in USD
 * @returns USD value as number
 */
export function calculateUSDValue(balance: string, priceUSD: string): number {
  const balanceNum = parseFloat(balance);
  const priceNum = parseFloat(priceUSD);
  return balanceNum * priceNum;
}

export type { TokenBalance, NativeBalance, ChainInfo };

