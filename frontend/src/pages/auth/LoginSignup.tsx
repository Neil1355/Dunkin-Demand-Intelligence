import React, { useState } from 'react';
import { Mail, Lock, MapPin, Hash, X } from 'lucide-react';
import { apiClient } from '../../api/client';

interface LoginSignupProps {
  mode: 'login' | 'signup';
  onLogin: (username: string) => void;
  onToggleMode: () => void;
  onClose: () => void;
}

export function LoginSignup({ mode, onLogin, onToggleMode, onClose }: LoginSignupProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    storeAddress: '',
    storeNumber: '',
    username: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'login') {
        const response = await apiClient.login(formData.email, formData.password);
        if (response.status === 'success' && response.user) {
          onLogin(response.user.name);
        } else {
          setError(response.message || 'Login failed');
        }
      } else {
        const response = await apiClient.signup(
          formData.username || formData.email.split('@')[0],
          formData.email,
          formData.password,
          formData.storeAddress,
          formData.storeNumber
        );
        if (response.status === 'success' && response.user) {
          onLogin(response.user.name);
        } else {
          setError(response.message || 'Signup failed');
        }
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred. Please try again.');
      console.error('Auth error:', err);
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
            className="absolute top-4 left-4 z-10 p-2 rounded-full hover:bg-white/20 transition-all"
            style={{ color: '#333' }}
          >
            <X size={24} />
          </button>

          {/* Header */}
          <div className="py-8 px-8 flex items-center gap-4" style={{ backgroundColor: '#FFF0F6' }}>
            <div className="rounded-full bg-gradient-to-br from-[#FF671F] to-[#DA1884] w-12 h-12 flex items-center justify-center text-white shadow-md">
              <span className="font-bold">DD</span>
            </div>
            <div>
              <h2 className="text-gray-800 text-lg font-semibold">
                {mode === 'login' ? 'Welcome Back' : 'Create Your Account'}
              </h2>
              <p className="text-sm text-gray-500">Dunkin Demand Intelligence — insights for your store</p>
            </div>
          </div>

          {/* Form content */}
          <form onSubmit={handleSubmit} className="p-8 space-y-5">
            {error && (
              <div className="p-3 rounded-md text-white text-sm" style={{ backgroundColor: '#FF6B6B' }}>
                {error}
              </div>
            )}
            {mode === 'signup' && (
              <div>
                <label className="block mb-2" style={{ color: '#8B7355' }}>
                  Your Name
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="w-full px-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                    placeholder="John Doe"
                    style={{ 
                      borderColor: '#E0D5C7',
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                    onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block mb-2" style={{ color: '#8B7355' }}>
                Email
              </label>
              <div className="relative">
                <Mail size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                  placeholder="you@dunkin.com"
                  style={{ 
                    borderColor: '#E0D5C7',
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                  onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                />
              </div>
            </div>

            <div>
              <label className="block mb-2" style={{ color: '#8B7355' }}>
                Password
              </label>
              <div className="relative">
                <Lock size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                  placeholder="••••••••"
                  style={{ 
                    borderColor: '#E0D5C7',
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                  onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                />
              </div>
            </div>

            {mode === 'signup' && (
              <>
                <div>
                  <label className="block mb-2" style={{ color: '#8B7355' }}>
                    Store Address
                  </label>
                  <div className="relative">
                    <MapPin size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      type="text"
                      value={formData.storeAddress}
                      onChange={(e) => setFormData({ ...formData, storeAddress: e.target.value })}
                      className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="123 Main St, Boston, MA"
                      style={{ 
                        borderColor: '#E0D5C7',
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                    />
                  </div>
                </div>

                <div>
                  <label className="block mb-2" style={{ color: '#8B7355' }}>
                    Store Number
                  </label>
                  <div className="relative">
                    <Hash size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      type="text"
                      value={formData.storeNumber}
                      onChange={(e) => setFormData({ ...formData, storeNumber: e.target.value })}
                      className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="12345"
                      style={{ 
                        borderColor: '#E0D5C7',
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                    />
                  </div>
                </div>
              </>
            )}

            <div className="flex gap-3 pt-4">
              {mode === 'login' ? (
                <>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg disabled:opacity-50"
                    style={{ backgroundColor: '#FF671F' }}
                  >
                    {loading ? 'Logging in...' : 'Login'}
                  </button>
                  <button
                    type="button"
                    onClick={onToggleMode}
                    disabled={loading}
                    className="flex-1 py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg disabled:opacity-50"
                    style={{ backgroundColor: '#DA1884' }}
                  >
                    Create Account
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={onToggleMode}
                    disabled={loading}
                    className="flex-1 py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg disabled:opacity-50"
                    style={{ backgroundColor: '#FF671F' }}
                  >
                    Back to Login
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg disabled:opacity-50"
                    style={{ backgroundColor: '#DA1884' }}
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                  </button>
                </>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}