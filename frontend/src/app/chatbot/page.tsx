/**
 * AI Chatbot Page Component - Product Assistant Interface
 * =======================================================
 * 
 * This component provides an AI-powered chatbot interface for users to query
 * product information using natural language. It integrates with OpenAI GPT
 * to provide intelligent responses about marketplace products.
 * 
 * Key Features:
 * - Natural language product queries
 * - Real-time chat interface with message history
 * - AI-powered responses using OpenAI GPT
 * - Business-scoped product context (users only query their business products)
 * - Professional chat UI with modern design
 * - Message persistence and history retrieval
 * - Responsive design for all devices
 * - Error handling with graceful fallbacks
 * 
 * AI Capabilities:
 * - Product search and discovery
 * - Price comparisons and recommendations
 * - Business insights and analytics
 * - Natural language understanding
 * - Context-aware responses
 * 
 * Business Logic:
 * - Users can only query products from their associated business
 * - Superusers can query all approved products
 * - Only approved products are included in AI responses
 * - Chat history is stored per user for reference
 * 
 * User Experience:
 * - Conversational interface similar to modern chat apps
 * - Suggested queries for new users
 * - Real-time typing indicators
 * - Message history for reference
 * - Professional appearance suitable for business use
 * 
 * Security & Privacy:
 * - Authentication required for access
 * - Business isolation (users can't query other businesses' data)
 * - Chat history is private to each user
 * - No sensitive business data exposed to AI
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';

import { Building2, MessageSquare, LayoutDashboard, Share2, Users, TrendingUp } from 'lucide-react';

/**
 * Message Interface Definition
 * 
 * Represents a chat message in the conversation. Handles both user messages
 * and AI responses with flexible field support for different API response formats.
 */
interface Message {
  id?: number;                          // Optional message ID from database
  user_message?: string;                // User's message (from chat history API)
  ai_response?: string;                 // AI's response (from chat history API)
  message?: string;                     // Alternative field name for user message
  response?: string;                    // Alternative field name for AI response
  isUser: boolean;                      // Whether this message is from the user
  text: string;                         // The actual message text to display
}

/**
 * AI Chatbot Component
 * 
 * Provides an intelligent chat interface for product queries and business insights.
 */
export default function Chatbot() {
  // Authentication and navigation hooks
  const { user, logout } = useAuth();                        // Get current user and logout function
  const router = useRouter();                                // Next.js router for navigation
  const pathname = usePathname();                            // Current path for navigation highlighting
  
  // Chat state management
  const [messages, setMessages] = useState<Message[]>([]);   // Chat conversation history
  const [input, setInput] = useState('');                    // Current user input
  const [loading, setLoading] = useState(false);             // Loading state for AI responses

  /**
   * Authentication Guard and Data Loading Effect
   * 
   * Ensures only authenticated users can access the chatbot and loads
   * their chat history when the component mounts.
   */
  useEffect(() => {
    // Redirect unauthenticated users to login
    if (!user) {
      router.push('/login');
      return;
    }
    
    // Load user's chat history
    fetchHistory();
  }, [user, router]);

  /**
   * Fetch Chat History from API
   * 
   * Retrieves the user's previous chat conversations with the AI assistant.
   * Messages are formatted and ordered for display in the chat interface.
   * 
   * Process:
   * 1. Fetch chat history from backend API
   * 2. Transform API response into Message format
   * 3. Create alternating user/AI message pairs
   * 4. Reverse order to show newest messages at bottom
   * 5. Update messages state for display
   */
  const fetchHistory = async () => {
    try {
      const response = await api.get('/chatbot/history/');
      
      // Transform API response into chat message format
      const history = (response.data.results || response.data).map((msg: any) => [
        { isUser: true, text: msg.user_message },      // User's question
        { isUser: false, text: msg.ai_response },      // AI's response
      ]).flat();
      
      // Reverse to show chronological order (oldest to newest)
      setMessages(history.reverse());
    } catch (error) {
      console.error('Error fetching chat history:', error);
      // TODO: Show user-friendly error message
    }
  };

  /**
   * Handle Chat Message Submission
   * 
   * Processes user input and sends it to the AI chatbot API for intelligent responses.
   * Manages the complete conversation flow with error handling and UI updates.
   * 
   * Process Flow:
   * 1. Validate user input (not empty)
   * 2. Add user message to chat immediately (optimistic UI)
   * 3. Clear input field and show loading state
   * 4. Send query to AI chatbot API
   * 5. Add AI response to chat
   * 6. Handle errors gracefully with user-friendly messages
   * 7. Clear loading state
   * 
   * Error Handling:
   * - Network errors: Generic error message
   * - API errors: Specific error from backend
   * - AI service errors: Fallback error message
   * 
   * @param e - Form submission event
   */
  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    
    // Add user message to chat immediately (optimistic UI update)
    setMessages([...messages, { isUser: true, text: userMessage }]);
    setLoading(true);

    try {
      // Send query to AI chatbot API
      const response = await api.post('/chatbot/query/', { message: userMessage });
      
      // Add AI response to chat
      setMessages(prev => [...prev, { isUser: false, text: response.data.response }]);
    } catch (error: any) {
      // Handle errors gracefully with user-friendly messages
      const errorMessage = error.response?.data?.error || 'Sorry, I encountered an error. Please try again.';
      setMessages(prev => [...prev, {
        isUser: false,
        text: errorMessage
      }]);
    } finally {
      // Always clear loading state
      setLoading(false);
    }
  };

  /**
   * Handle User Logout
   * 
   * Logs out the current user and redirects to the landing page.
   */
  const handleLogout = () => {
    logout();
    router.push('/');
  };

  // Early return if user is not authenticated (prevents flash of content)
  if (!user) return null;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-[#001529] text-white shadow-lg flex flex-col transition-colors duration-200">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-white">Product Marketplace</h1>
        </div>

        <nav className="mt-6 flex-1 space-y-1">
          {user.role === 'admin' && (
            <Link
              href="/admin/dashboard"
              className={`flex items-center px-6 py-3 transition-colors ${pathname === '/admin/dashboard'
                ? 'text-white bg-blue-600 border-r-4 border-blue-400'
                : 'text-gray-300 hover:bg-[#002140] hover:text-white'
                }`}
            >
              <TrendingUp className="w-5 h-5 mr-3" />
              Admin Dashboard
            </Link>
          )}

          {user.role === 'admin' && (
            <Link
              href="/users"
              className={`flex items-center px-6 py-3 transition-colors ${pathname === '/users'
                ? 'text-white bg-blue-600 border-r-4 border-blue-400'
                : 'text-gray-300 hover:bg-[#002140] hover:text-white'
                }`}
            >
              <Users className="w-5 h-5 mr-3" />
              Manage Users
            </Link>
          )}

          <Link
            href="/dashboard"
            className={`flex items-center px-6 py-3 transition-colors ${pathname === '/dashboard'
              ? 'text-white bg-blue-600 border-r-4 border-blue-400'
              : 'text-gray-300 hover:bg-[#002140] hover:text-white'
              }`}
          >
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Products
          </Link>

          <Link
            href="/business"
            className={`flex items-center px-6 py-3 transition-colors ${pathname === '/business'
              ? 'text-white bg-blue-600 border-r-4 border-blue-400'
              : 'text-gray-300 hover:bg-[#002140] hover:text-white'
              }`}
          >
            <Building2 className="w-5 h-5 mr-3" />
            Business
          </Link>

          <Link
            href="/chatbot"
            className={`flex items-center px-6 py-3 transition-colors ${pathname === '/chatbot'
              ? 'text-white bg-blue-600 border-r-4 border-blue-400'
              : 'text-gray-300 hover:bg-[#002140] hover:text-white'
              }`}
          >
            <MessageSquare className="w-5 h-5 mr-3" />
            AI Chatbot
          </Link>
        </nav>

        <div className="border-t border-gray-700">
          <div className="p-4 bg-[#001529]">
            <p className="text-sm font-medium text-white">{user.business_name}</p>
            <p className="text-xs text-gray-400 mt-1">{user.email}</p>
            <p className="text-xs text-gray-500">{user.role}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-6 py-3 text-white hover:bg-red-900/20 transition-colors"
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm z-10">
          <div className="px-8 py-4 flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-900">AI Product Assistant</h2>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                Online
              </span>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-hidden p-8 flex flex-col">
          <div className="bg-white rounded-xl shadow-lg flex-1 flex flex-col border border-gray-100 overflow-hidden max-w-5xl mx-auto w-full">
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50/50">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 mt-20">
                  <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <MessageSquare className="w-10 h-10 text-blue-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">How can I help you today?</h3>
                  <p className="max-w-md mx-auto">Ask me about available products, compare prices, or get business insights from our catalog.</p>

                  <div className="mt-8 grid grid-cols-2 gap-3 text-left max-w-2xl mx-auto">
                    {[
                      "Show me all available products",
                      "What products are under $100?",
                      "Tell me more about Maze",
                      "How many businesses are listed?"
                    ].map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => setInput(suggestion)}
                        className="p-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors shadow-sm"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm ${msg.isUser
                        ? 'bg-blue-600 text-white rounded-tr-none'
                        : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
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
                  <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-none px-5 py-3 shadow-sm">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-100">
              <div className="flex gap-3 max-w-4xl mx-auto items-center">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me anything about products..."
                  className="flex-1 px-5 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-inner"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-blue-600/20 active:scale-95 transition-all"
                >
                  <Share2 className="w-6 h-6 rotate-90" />
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
