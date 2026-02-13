import React, { useState, useEffect } from 'react';
import { Lock, X, Eye, EyeOff } from 'lucide-react';

interface ResetPasswordProps {
  onClose: () => void;
  onSuccess?: () => void;
  token?: string;
}

export function ResetPassword({ onClose, onSuccess, token: propToken }: ResetPasswordProps) {
  // Get token from props or URL search params
  const urlParams = new URLSearchParams(window.location.search);
  const token = propToken || urlParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  // Validate token on mount
  useEffect(() => {
    if (!token) {
      setError('No reset token provided');
      setValidating(false);
      return;
    }

    const validateToken = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/auth/validate-reset-token`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token })
        });

        const data = await response.json();

        if (response.ok) {
          setTokenValid(true);
          setUserEmail(data.email);
        } else {
          setError(data.message || 'Invalid or expired reset link');
        }
      } catch (err: any) {
        setError(err.message || 'Failed to validate reset token');
        console.error('Token validation error:', err);
      } finally {
        setValidating(false);
      }
    };

    validateToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password })
      });

      const data = await response.json();

      if (response.ok) {
        setSubmitted(true);
        if (onSuccess) {
          setTimeout(onSuccess, 1500);
        }
      } else {
        setError(data.message || 'Failed to reset password');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      console.error('Reset password error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (validating) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: '#FFF7F2' }}>
        <div className="w-full max-w-md">
          <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
            <div className="py-12 px-8 text-center">
              <div className="inline-block animate-spin">
                <div className="w-8 h-8 border-4 border-gray-200 border-t-orange-500 rounded-full" />
              </div>
              <p className="text-gray-600 mt-4">Validating your reset link...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!tokenValid) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: '#FFF7F2' }}>
        <div className="w-full max-w-md">
          <div className="bg-white rounded-3xl shadow-2xl overflow-hidden relative border border-gray-100">
            <button
              onClick={onClose}
              className="absolute top-4 right-4 z-10 p-2 rounded-full hover:bg-white/20 transition-all"
              style={{ color: '#333' }}
            >
              <X size={24} />
            </button>

            <div className="py-12 px-8 text-center">
              <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">✕</span>
              </div>
              <h3 className="text-gray-800 font-semibold mb-2">Link Expired or Invalid</h3>
              <p className="text-gray-600 text-sm mb-4">{error}</p>
              <button
                onClick={onClose}
                className="w-full py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg"
                style={{ backgroundColor: '#FF671F' }}
              >
                Request New Link
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

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

          {/* Header */}
          <div className="py-8 px-8 flex items-center gap-4" style={{ backgroundColor: '#FFF0F6' }}>
            <div className="rounded-full bg-gradient-to-br from-[#FF671F] to-[#DA1884] w-12 h-12 flex items-center justify-center text-white shadow-md">
              <Lock size={24} />
            </div>
            <div>
              <h2 className="text-gray-800 text-lg font-semibold">Create New Password</h2>
              <p className="text-sm text-gray-500">Make it strong and unique</p>
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
                  <label htmlFor="password" className="block mb-2" style={{ color: '#8B7355' }}>
                    New Password
                  </label>
                  <div className="relative">
                    <Lock size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-12 pr-12 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="••••••••"
                      style={{ borderColor: '#E0D5C7' }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                      required
                      minLength={8}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2"
                      style={{ color: '#8B7355' }}
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
                </div>

                <div>
                  <label htmlFor="confirm" className="block mb-2" style={{ color: '#8B7355' }}>
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      id="confirm"
                      type={showConfirm ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full pl-12 pr-12 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="••••••••"
                      style={{ borderColor: '#E0D5C7' }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirm(!showConfirm)}
                      className="absolute right-4 top-1/2 -translate-y-1/2"
                      style={{ color: '#8B7355' }}
                    >
                      {showConfirm ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading || !password || !confirmPassword}
                  className="w-full py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ backgroundColor: '#FF671F' }}
                >
                  {loading ? 'Updating Password...' : 'Reset Password'}
                </button>
              </>
            ) : (
              <div className="py-4">
                <div className="mb-4 text-center">
                  <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">✓</span>
                  </div>
                  <h3 className="text-gray-800 font-semibold mb-2">Password Reset Successful!</h3>
                  <p className="text-gray-600 text-sm">
                    Your password has been securely updated. You can now log in with your new password.
                  </p>
                </div>

                <button
                  onClick={onClose}
                  className="w-full py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg"
                  style={{ backgroundColor: '#FF671F' }}
                >
                  Return to Login
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
