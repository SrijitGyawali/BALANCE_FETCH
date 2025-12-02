'use client';

import { useEffect } from 'react';
import { useAccount } from 'wagmi';
import { AppKitButton } from '@reown/appkit/react';

/**
 * Wallet connection component using Reown AppKit
 */
export function WalletConnect(): JSX.Element {
  const { address, isConnected } = useAccount();

  // Suppress non-critical analytics errors
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const originalError = console.error;
    const originalWarn = console.warn;

    console.error = (...args: unknown[]): void => {
      const fullMessage = args.map((arg) => String(arg)).join(' ');
      if (
        fullMessage.includes('Analytics SDK') ||
        fullMessage.includes('ERR_BLOCKED_BY_CLIENT') ||
        fullMessage.includes('cca-lite.coinbase.com') ||
        fullMessage.includes('pulse.walletconnect.org')
      ) {
        return;
      }
      originalError.apply(console, args);
    };

    console.warn = (...args: unknown[]): void => {
      const fullMessage = args.map((arg) => String(arg)).join(' ');
      if (
        fullMessage.includes('Extra attributes from the server') ||
        fullMessage.includes('preload but not used')
      ) {
        return;
      }
      originalWarn.apply(console, args);
    };

    return () => {
      console.error = originalError;
      console.warn = originalWarn;
    };
  }, []);

  // Diagnostic log for MetaMask detection
  useEffect(() => {
    if (typeof window !== 'undefined' && window.ethereum) {
      console.log('MetaMask detected:', window.ethereum.isMetaMask);
    } else {
      console.log('MetaMask not detected. Please install MetaMask extension.');
    }
  }, []);

  return (
    <div className="wallet-connect">
      <AppKitButton />
      {isConnected && address && (
        <div className="wallet-info">
          <p>Connected: {address}</p>
        </div>
      )}
    </div>
  );
}


