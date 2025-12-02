/**
 * Environment variable utilities
 * 
 * Handles loading API keys from environment variables with fallback support
 * for both Next.js client-side (NEXT_PUBLIC_*) and server-side formats
 */

/**
 * Get The Graph API key from environment variables
 * 
 * Checks both NEXT_PUBLIC_THEGRAPH_API_KEY (for client-side) and
 * THEGRAPH_API_KEY (for server-side/test compatibility)
 * 
 * @returns The Graph API key or empty string if not found
 */
export function getTheGraphApiKey(): string {
  // In Next.js, client-side code can only access NEXT_PUBLIC_* variables
  // Server-side code can access any variable
  if (typeof window !== 'undefined') {
    // Client-side: only NEXT_PUBLIC_* variables are available
    return process.env.NEXT_PUBLIC_THEGRAPH_API_KEY || '';
  } else {
    // Server-side: can access both formats
    return process.env.NEXT_PUBLIC_THEGRAPH_API_KEY || process.env.THEGRAPH_API_KEY || '';
  }
}

/**
 * Get Wallet Connect Project ID from environment variables
 * 
 * @returns Project ID or empty string if not found
 */
export function getWalletConnectProjectId(): string {
  return process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID || '';
}

/**
 * Validate that required environment variables are set
 * 
 * @returns Object with validation status and missing variables
 */
export function validateEnvVars(): {
  isValid: boolean;
  missing: string[];
  warnings: string[];
} {
  const missing: string[] = [];
  const warnings: string[] = [];

  const apiKey = getTheGraphApiKey();
  if (!apiKey) {
    if (typeof window !== 'undefined') {
      missing.push('NEXT_PUBLIC_THEGRAPH_API_KEY');
      warnings.push(
        'NEXT_PUBLIC_THEGRAPH_API_KEY is required for client-side access. ' +
        'Add it to your .env.local file.'
      );
    } else {
      missing.push('NEXT_PUBLIC_THEGRAPH_API_KEY or THEGRAPH_API_KEY');
      warnings.push(
        'Either NEXT_PUBLIC_THEGRAPH_API_KEY (client-side) or ' +
        'THEGRAPH_API_KEY (server-side) must be set in your .env.local file.'
      );
    }
  }

  const projectId = getWalletConnectProjectId();
  if (!projectId) {
    missing.push('NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID');
    warnings.push(
      'NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID is required for wallet connections. ' +
      'Add it to your .env.local file.'
    );
  }

  return {
    isValid: missing.length === 0,
    missing,
    warnings,
  };
}




