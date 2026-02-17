'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

type PublicProduct = {
  id: number;
  name: string;
  description: string;
  price: string;
  business_name?: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export default function Home() {
  const [products, setProducts] = useState<PublicProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');

  useEffect(() => {
    const fetchApproved = async () => {
      try {
        setError('');
        const res = await fetch(`${API_URL}/products/?public=true`, {
          cache: 'no-store',
        });
        if (!res.ok) throw new Error(`Failed to load products (${res.status})`);
        const data = await res.json();
        setProducts(Array.isArray(data) ? data : (data.results || []));
      } catch (e: any) {
        setError(e?.message || 'Failed to load products');
      } finally {
        setLoading(false);
      }
    };
    fetchApproved();
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return products;
    return products.filter((p) => {
      return (
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        (p.business_name || '').toLowerCase().includes(q)
      );
    });
  }, [products, query]);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Product Marketplace</h1>
            <p className="text-sm text-gray-600">Browse approved products available to the public.</p>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className="px-4 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-100"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700"
            >
              Register
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
            <div className="text-sm text-gray-600">
              {loading ? 'Loading…' : `${filtered.length} product(s)`}
            </div>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search products…"
              className="w-full sm:w-80 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <p className="text-gray-600">No approved products yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((p) => (
              <div key={p.id} className="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
                <div className="flex items-start justify-between gap-4">
                  <h3 className="text-lg font-semibold text-gray-900">{p.name}</h3>
                  <div className="text-lg font-bold text-blue-600">${p.price}</div>
                </div>
                {p.business_name && (
                  <div className="text-xs text-gray-500 mt-1">Business: {p.business_name}</div>
                )}
                <p className="text-sm text-gray-700 mt-3 line-clamp-4">{p.description}</p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
