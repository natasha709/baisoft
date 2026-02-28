import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Product Marketplace - BAISoft',
  description: 'Internal product management system with role-based access control, approval workflows, and AI-powered assistance',
  keywords: ['product management', 'marketplace', 'business tools', 'workflow', 'approval system'],
  authors: [{ name: 'BAISoft Global' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'noindex, nofollow',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {}
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
