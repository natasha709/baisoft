/**
 * Next.js Configuration for Product Marketplace Frontend
 * =====================================================
 * 
 * This file configures Next.js build and runtime behavior for the Product Marketplace application.
 * It defines how the application should be built, optimized, and served.
 * 
 * Key Features:
 * - Production-ready configuration
 * - API integration settings
 * - Performance optimizations
 * - Security headers
 * - Environment-specific settings
 * 
 * Configuration Categories:
 * 1. Build Configuration - How the app is compiled and optimized
 * 2. Runtime Configuration - How the app behaves when running
 * 3. API Configuration - Backend integration settings
 * 4. Security Configuration - Headers and security policies
 * 5. Performance Configuration - Caching and optimization
 * 
 * @type {import('next').NextConfig}
 */

const nextConfig = {
  // Enable React Strict Mode for better development experience
  // Helps catch common bugs and deprecated patterns
  reactStrictMode: true,
  
  // Enable SWC minification for better performance
  // SWC is faster than Terser and produces smaller bundles
  swcMinify: true,
  
  // Configure image optimization
  images: {
    // Add domains for external images if needed
    domains: [],
    // Enable image optimization
    unoptimized: false,
  },
  
  // Environment variables available to the browser
  // These are embedded at build time and available in client-side code
  env: {
    CUSTOM_KEY: 'my-value',
  },
  
  // Experimental features (use with caution in production)
  experimental: {
    // Enable app directory (Next.js 13+ feature)
    appDir: true,
  },
  
  // Configure redirects for better UX
  async redirects() {
    return [
      // Redirect root to dashboard for authenticated users
      // This would need middleware to check authentication
      // {
      //   source: '/',
      //   destination: '/dashboard',
      //   permanent: false,
      // },
    ]
  },
  
  // Configure rewrites for API proxying if needed
  async rewrites() {
    return [
      // Example: Proxy API calls to backend
      // {
      //   source: '/api/:path*',
      //   destination: 'http://localhost:8000/api/:path*',
      // },
    ]
  },
  
  // Configure security headers
  async headers() {
    return [
      {
        // Apply security headers to all routes
        source: '/(.*)',
        headers: [
          // Prevent clickjacking attacks
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          // Prevent MIME type sniffing
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          // Enable XSS protection
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          // Referrer policy for privacy
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
