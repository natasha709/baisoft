/**
 * Root Layout Component for Product Marketplace
 * ============================================
 * 
 * This is the root layout component that wraps all pages in the Next.js application.
 * It provides the basic HTML structure, global styles, and application-wide providers.
 * 
 * Key Features:
 * - Global HTML structure and metadata
 * - Font loading and optimization (Inter font)
 * - Authentication context provider
 * - Global CSS imports
 * - SEO metadata configuration
 * 
 * Layout Hierarchy:
 * - HTML document structure
 * - Body with font classes
 * - AuthProvider for authentication state
 * - Page content (children)
 * 
 * This component runs on every page load and provides the foundation
 * for the entire application's UI and functionality.
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';

// Configure Inter font with Latin subset for optimal loading
// Inter is a modern, highly readable font designed for user interfaces
const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap', // Improve font loading performance
});

// SEO metadata configuration for the application
// This appears in browser tabs, search results, and social media shares
export const metadata: Metadata = {
  title: 'Product Marketplace - BAISoft',
  description: 'Internal product management system with role-based access control, approval workflows, and AI-powered assistance',
  keywords: ['product management', 'marketplace', 'business tools', 'workflow', 'approval system'],
  authors: [{ name: 'BAISoft Global' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'noindex, nofollow', // Prevent search engine indexing for internal tool
};

/**
 * Root Layout Component
 * 
 * This component provides the basic HTML structure for all pages.
 * It includes global providers and styling that apply to the entire application.
 * 
 * @param children - The page content to render within the layout
 * @returns JSX element with complete HTML document structure
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {/* 
          AuthProvider wraps the entire application to provide authentication state
          This allows any component to access user information and authentication methods
        */}
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
