'use client';

import { WalletConnect } from '@/components/wallet-connect';
import { TokenBalances } from '@/components/token-balances';
import { AddressChecker } from '@/components/address-checker';
import { getTheGraphApiKey, validateEnvVars } from '@/lib/env-utils';

export default function Home(): JSX.Element {
  const apiKey = getTheGraphApiKey();

  if (typeof window !== 'undefined') {
    const validation = validateEnvVars();
    
    if (!validation.isValid) {
      console.warn('⚠️ Missing environment variables:');
      validation.warnings.forEach((warning) => {
        console.warn(`  - ${warning}`);
      });
      console.warn('\n💡 Tip: Create a .env.local file in the frontend/ directory with:');
      console.warn('   NEXT_PUBLIC_THEGRAPH_API_KEY=your_jwt_token_here');
      console.warn('   NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your_project_id_here');
    } else {
      console.log('✅ The Graph API key is configured (length:', apiKey.length, ')');
    }
  }

  return (
    <main className="main-container">
      <div className="container">
        <h1>Wallet Token Balances</h1>
        <p className="description">Connect your wallet or check any address to view token holdings</p>
        
        <div className="wallet-section">
          <WalletConnect />
        </div>
        
        <div className="balances-section">
          <TokenBalances apiKey={apiKey} />
        </div>

        <div className="address-checker-section">
          <AddressChecker apiKey={apiKey} />
        </div>
      </div>
    </main>
  );
}














