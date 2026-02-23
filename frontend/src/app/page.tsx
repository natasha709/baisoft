'use client';

import Link from 'next/link';
import { ShoppingCart, Lock } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-900 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-[#001529]" />
              </div>
              <span className="ml-3 text-xl font-bold text-white">BAISoft</span>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="px-4 py-2 text-gray-300 hover:text-white font-medium transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="px-5 py-2.5 rounded-lg bg-white text-gray-900 font-medium hover:bg-gray-100 transition-all"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50"></div>
        <div className="absolute top-20 right-0 w-96 h-96 bg-[#001529]/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 leading-tight mb-6">
              Welcome to
              <span className="text-[#001529]"> BAISoft</span>
            </h1>
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              Internal Product Management System
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/login"
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-[#001529] text-white font-semibold text-lg hover:bg-[#002140] transition-all shadow-xl shadow-[#001529]/20 flex items-center justify-center"
              >
                <Lock className="w-5 h-5 mr-2" />
                Login to Access
              </Link>
              <Link
                href="/register"
                className="w-full sm:w-auto px-8 py-4 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold text-lg hover:border-[#001529] hover:text-[#001529] transition-all flex items-center justify-center"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center mb-4 md:mb-0">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-5 h-5 text-[#001529]" />
              </div>
              <span className="ml-3 text-lg font-bold">BAISoft</span>
            </div>
            <p className="text-gray-400 text-sm">
              © 2024 BAISoft. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
