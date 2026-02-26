/**
 * Tailwind CSS Configuration for Product Marketplace
 * =================================================
 * 
 * This file configures Tailwind CSS for the Product Marketplace frontend.
 * It defines the design system, utility classes, and styling approach.
 * 
 * Key Features:
 * - Utility-first CSS framework
 * - Responsive design system
 * - Custom color palette and typography
 * - Component-friendly class generation
 * - Production optimization (unused CSS removal)
 * 
 * Design System:
 * - Colors: Professional blue/gray palette for business applications
 * - Typography: Clean, readable fonts for data-heavy interfaces
 * - Spacing: Consistent spacing scale for layouts
 * - Breakpoints: Mobile-first responsive design
 * - Components: Reusable UI patterns
 * 
 * @type {import('tailwindcss').Config}
 */

module.exports = {
  // Content sources for Tailwind to scan for class usage
  // This enables tree-shaking to remove unused CSS in production
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',     // Pages directory (if using)
    './src/components/**/*.{js,ts,jsx,tsx,mdx}', // Reusable components
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',       // App directory (Next.js 13+)
  ],
  
  // Theme customization and extensions
  theme: {
    extend: {
      // Custom color palette for the marketplace
      colors: {
        // Primary brand colors
        primary: {
          50: '#eff6ff',
          100: '#dbeafe', 
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Main primary color
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        
        // Secondary colors for accents
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',  // Main secondary color
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        
        // Success, warning, and error colors
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
      },
      
      // Custom typography scale
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
      
      // Custom spacing scale
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      
      // Custom border radius
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      
      // Custom box shadows for depth
      boxShadow: {
        'soft': '0 2px 15px 0 rgba(0, 0, 0, 0.08)',
        'medium': '0 4px 25px 0 rgba(0, 0, 0, 0.1)',
        'hard': '0 10px 40px 0 rgba(0, 0, 0, 0.15)',
      },
      
      // Custom animations for interactions
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },
      
      // Keyframes for custom animations
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(-5%)' },
          '50%': { transform: 'translateY(0)' },
        },
      },
    },
  },
  
  // Tailwind plugins for additional functionality
  plugins: [
    // Add plugins here as needed:
    // require('@tailwindcss/forms'),        // Better form styling
    // require('@tailwindcss/typography'),   // Prose styling
    // require('@tailwindcss/aspect-ratio'), // Aspect ratio utilities
  ],
  
  // Dark mode configuration (if needed)
  darkMode: 'class', // Enable class-based dark mode
}
