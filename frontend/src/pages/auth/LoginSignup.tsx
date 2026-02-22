import React, { useState, useEffect } from 'react';
import { Mail, Lock, X, Building, Phone, User } from 'lucide-react';
import { apiClient } from '../../api/client';
import { apiFetch } from '../../utils/api';

interface LoginSignupProps {
  mode: 'login' | 'signup';
  onLogin: (username: string) => void;
  onToggleMode: () => void;
  onClose: () => void;
  onForgotPassword?: () => void;
}

export function LoginSignup({ mode, onLogin, onToggleMode, onClose, onForgotPassword }: LoginSignupProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    store_id: '',
    phone: '',
    role: 'employee'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Clear form and errors when mode changes
  useEffect(() => {
    setFormData({
      email: '',
      password: '',
      username: '',
      store_id: '',
      phone: '',
      role: 'employee'
    });
    setError('');
    setSuccessMessage('');
  }, [mode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    // Frontend validation
    if (mode === 'signup') {
      if (!formData.username.trim()) {
        setError('Name is required');
        return;
      }
      if (!formData.store_id.trim()) {
        setError('Store number is required');
        return;
      }
    }
    
    if (!formData.email.trim()) {
      setError('Email is required');
      return;
    }
    
    if (!formData.password.trim()) {
      setError('Password is required');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      if (mode === 'login') {
        const response = await apiClient.login(formData.email, formData.password);
        if (response.status === 'success' && response.user) {
          setSuccessMessage('Login successful!');
          setTimeout(() => onLogin(response.user!.name), 500);
        } else {
          setError(response.message || 'Invalid email or password');
        }
      } else {
        const response = await apiClient.signup(
          formData.username || formData.email.split('@')[0],
          formData.email,
          formData.password,
          parseInt(formData.store_id),
          formData.phone || undefined,
          formData.role
        );
        if (response.status === 'success' && response.user) {
          setSuccessMessage('Account created successfully!');
          setTimeout(() => onLogin(response.user!.name), 500);
        } else {
          setError(response.message || 'Signup failed');
        }
      }
    } catch (err: any) {
      // Clean up common error messages for better UX
      let errorMsg = err.message || 'An error occurred. Please try again.';
      
      if (errorMsg.toLowerCase().includes('user not found') || errorMsg.toLowerCase().includes('invalid')) {
        errorMsg = mode === 'login' ? 'Incorrect email or password' : errorMsg;
      }
      
      setError(errorMsg);
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-3 sm:p-6" style={{ backgroundColor: '#FFF7F2' }}>
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl sm:rounded-3xl shadow-2xl overflow-hidden relative border border-gray-100">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-3 left-3 sm:top-4 sm:left-4 z-10 p-1.5 sm:p-2 rounded-full hover:bg-white/20 transition-all"
            style={{ color: '#333' }}
          >
            <X size={20} className="sm:w-6 sm:h-6" />
          </button>

          {/* Header */}
          <div className="py-4 px-4 sm:py-8 sm:px-8 flex items-center gap-3 sm:gap-4" style={{ backgroundColor: '#FFF0F6' }}>
            <div className="rounded-full bg-gradient-to-br from-[#FF671F] to-[#DA1884] w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center text-white shadow-md flex-shrink-0">
              <span className="font-bold text-sm sm:text-base">DD</span>
            </div>
            <div className="min-w-0">
              <h2 className="text-gray-800 text-base sm:text-lg font-semibold truncate">
                {mode === 'login' ? 'Welcome Back' : 'Create Account'}
              </h2>
              <p className="text-xs sm:text-sm text-gray-500 truncate">Dunkin Demand Intelligence</p>
            </div>
          </div>

          {/* Form content */}
          <form onSubmit={handleSubmit} className="p-4 sm:p-8 space-y-4 sm:space-y-5">
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
            {successMessage && (
              <div className="p-4 rounded-lg text-white text-sm flex items-start justify-between" style={{ backgroundColor: '#51CF66' }}>
                <span>{successMessage}</span>
                <button
                  type="button"
                  onClick={() => setSuccessMessage('')}
                  className="ml-2 font-bold hover:opacity-80"
                >
                  ✕
                </button>
              </div>
            )}
            {mode === 'signup' && (
              <>
                <div>
                  <label htmlFor="username" className="block mb-2" style={{ color: '#8B7355' }}>
                    Your Name <span style={{ color: '#FF671F' }}>*</span>
                  </label>
                  <div className="relative">
                    <User size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      id="username"
                      name="username"
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                      className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="John Doe"
                      required
                      style={{ 
                        borderColor: '#E0D5C7',
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="store_id" className="block mb-2" style={{ color: '#8B7355' }}>
                    Store Number <span style={{ color: '#FF671F' }}>*</span>
                  </label>
                  <div className="relative">
                    <Building size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      id="store_id"
                      name="store_id"
                      type="number"
                      value={formData.store_id}
                      onChange={(e) => setFormData({ ...formData, store_id: e.target.value })}
                      className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="12345"
                      required
                      style={{ 
                        borderColor: '#E0D5C7',
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="phone" className="block mb-2" style={{ color: '#8B7355' }}>
                    Phone Number <span style={{ color: '#999', fontSize: '0.85rem' }}>(optional)</span>
                  </label>
                  <div className="relative">
                    <Phone size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                    <input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full pl-12 pr-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm"
                      placeholder="(555) 123-4567"
                      style={{ 
                        borderColor: '#E0D5C7',
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="role" className="block mb-2" style={{ color: '#8B7355' }}>
                    Your Role
                  </label>
                  <div className="relative">
                    <select
                      id="role"
                      name="role"
                      value={formData.role}
                      onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                      className="w-full px-4 py-3 rounded-full border-2 border-gray-200 focus:outline-none transition-all shadow-sm appearance-none"
                      style={{ 
                        borderColor: '#E0D5C7',
                        backgroundColor: 'white'
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#FF671F'}
                      onBlur={(e) => e.target.style.borderColor = '#E0D5C7'}
                    >
                      <option value="employee">Employee</option>
                      <option value="assistant_manager">Assistant Manager</option>
                      <option value="manager">Manager</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            <div>
              <label htmlFor="email" className="block mb-2" style={{ color: '#8B7355' }}>
                Email
              </label>
              <div className="relative">
                <Mail size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                <input
                  id="email"
                  name="email"
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
              <label htmlFor="password" className="block mb-2" style={{ color: '#8B7355' }}>
                Password
              </label>
              <div className="relative">
                <Lock size={20} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: '#8B7355' }} />
                <input
                  id="password"
                  name="password"
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

            {mode === 'login' && (
              <div className="text-right">
                <button
                  type="button"
                  onClick={onForgotPassword}
                  className="text-sm transition-colors hover:underline"
                  style={{ color: '#FF671F' }}
                >
                  Forgot Password?
                </button>
              </div>
            )}

            {mode === 'login' && (
              <div className="p-3 rounded-lg border border-yellow-300 bg-yellow-50">
                <p className="text-xs text-yellow-800 mb-2">
                  <strong>⚠️ Database Unavailable:</strong> Using test login to demonstrate features.
                </p>
                <button
                  type="button"
                  onClick={async () => {
                    setLoading(true);
                    setError('');
                    try {
                      const data = await apiFetch('/test-login');
                      if (data.status === 'success' && data.user) {
                        setSuccessMessage('Test login successful!');
                        setTimeout(() => onLogin(data.user.name), 500);
                      } else {
                        setError('Test login failed. Make sure backend is running.');
                      }
                    } catch (err) {
                      setError('Cannot reach backend. Is it running on localhost:5000?');
                    } finally {
                      setLoading(false);
                    }
                  }}
                  disabled={loading}
                  className="w-full py-2 rounded-lg text-sm text-white transition-all hover:scale-105 disabled:opacity-50 bg-yellow-600"
                >
                  {loading ? 'Loading...' : '🔓 Test Login (No DB)'}
                </button>
              </div>
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