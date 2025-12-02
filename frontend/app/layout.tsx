import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { WagmiConfig } from '@/lib/wagmi-config';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Get Balance - Wallet Token Holdings',
  description: 'View all ERC-20 token balances for your connected wallet',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <html lang="en">
      <body className={inter.className}>
        <WagmiConfig>{children}</WagmiConfig>
      </body>
    </html>
  );
}














