'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';

interface Message {
  id?: number;
  user_message?: string;
  ai_response?: string;
  message?: string;
  response?: string;
  isUser: boolean;
  text: string;
}

export default function Chatbot() {
  const { user } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Protect this route so only authenticated users can access chatbot features.
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    fetchHistory();
  }, [user, router]);

  const fetchHistory = async () => {
    try {
      const response = await api.get('/chatbot/history/');
      // API returns user/AI pairs. We transform each pair into two bubble messages
      // and flatten them so the UI can render a single chronological list.
      const history = (response.data.results || response.data).map((msg: any) => [
        { isUser: true, text: msg.user_message },
        { isUser: false, text: msg.ai_response },
      ]).flat();
      // Reverse so older records appear first and latest appears at the bottom.
      setMessages(history.reverse());
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    // Optimistic update: show user message immediately before API response returns.
    setMessages([...messages, { isUser: true, text: userMessage }]);
    setLoading(true);

    try {
      const response = await api.post('/chatbot/query/', { message: userMessage });
      setMessages(prev => [...prev, { isUser: false, text: response.data.response }]);
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Sorry, I encountered an error. Please try again.';
      // Keep failures visible in the thread so users understand what happened.
      setMessages(prev => [...prev, {
        isUser: false,
        text: errorMessage
      }]);
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">AI Product Assistant</h1>
            <Link href="/dashboard" className="text-blue-600 hover:text-blue-800">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md h-[600px] flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
<p className="text-lg mb-2">Hi! I&apos;m your AI product assistant.</p>
                <p>Ask me about available products, prices, or anything else!</p>
                <div className="mt-6 text-sm text-left max-w-md mx-auto space-y-2">
                  <p className="font-semibold">Try asking:</p>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>&quot;Show me all available products&quot;</li>
                    <li>&quot;What products do you have?&quot;</li>
                    <li>&quot;Which products are under $50?&quot;</li>
                    <li>&quot;Tell me about [product name]&quot;</li>
                  </ul>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-2 ${msg.isUser
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-900'
                      }`}
                    style={{ whiteSpace: 'pre-wrap' }}
                  >
                    {msg.text}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 rounded-lg px-4 py-2">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSend} className="border-t p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about products..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
