import React, { useState } from 'react';
import { Mail, X, ArrowLeft } from 'lucide-react';
import { apiClient } from '../../api/client';

interface ForgotPasswordProps {
  onClose: () => void;
  onBackToLogin: () => void;
}

export function ForgotPassword({ onClose, onBackToLogin }: ForgotPasswordProps) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        setSubmitted(true);
        setEmail('');
      } else {
        setError(data.message || 'Failed to request reset link');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      console.error('Forgot password error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: '#FFF7F2' }}>
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden relative border border-gray-100">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 rounded-full hover:bg-white/20 transition-all"
            style={{ color: '#333' }}
          >
            <X size={24} />
          </button>

          {/* Back button */}
          <button
            onClick={onBackToLogin}
            className="absolute top-4 left-4 z-10 p-2 rounded-full hover:bg-white/20 transition-all"
            style={{ color: '#333' }}
          >
            <ArrowLeft size={24} />
          </button>

          {/* Header */}
          <div className="py-8 px-8 flex items-center gap-4" style={{ backgroundColor: '#FFF0F6' }}>
            <div className="rounded-full bg-gradient-to-br from-[#FF671F] to-[#DA1884] w-12 h-12 flex items-center justify-center text-white shadow-md">
              <span className="font-bold">DD</span>
            </div>
            <div>
              <h2 className="text-gray-800 text-lg font-semibold">Reset Your Password</h2>
              <p className="text-sm text-gray-500">Secure password recovery in 2 minutes</p>
            </div>
          </div>

          {/* Form content */}
          <form onSubmit={handleSubmit} className="p-8 space-y-5">
            {!submitted ? (
              <>
                {error && (
                  <div className="p-4 rounded-lg text-white text-sm flex items-start justify-between" style={{ backgroundColor: '#FF6B6B' }}>
                    <span>{error}</span>
                    <button
                      type="button"
                      onClick={() => setError('')}
                      className="ml-2 font-bold hover:opacity-80"
                    >
                      ✕
                    </button>
                  </div>
                )}

                <div>
                  <label htmlFor="email" className="block mb-2" style={{ color: '#8B7355' }}>
                    Enter Your Email
                  </label>
                  <div className="relative">
                    <Mail size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="you@dunkin.com"
                      style={{ borderColor: '#E0D5C7' }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                      required
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    We'll send a secure reset link to verify your identity.
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading || !email.trim()}
                  className="w-full py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ backgroundColor: '#FF671F' }}
                >
                  {loading ? 'Sending...' : 'Send Reset Link'}
                </button>
              </>
            ) : (
              <div className="py-4">
                <div className="mb-4 text-center">
                  <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">✓</span>
                  </div>
                  <h3 className="text-gray-800 font-semibold mb-2">Check Your Email!</h3>
                  <p className="text-gray-600 text-sm mb-4">
                    We've sent a password reset link to <strong>{email}</strong>
                  </p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                    <p className="text-xs text-gray-700">
                      <strong>💡 Tip:</strong> Check your spam folder if you don't see the email. The link expires in 1 hour for security.
                    </p>
                  </div>
                </div>

                <button
                  onClick={onBackToLogin}
                  className="w-full py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg"
                  style={{ backgroundColor: '#FF671F' }}
                >
                  Back to Login
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
