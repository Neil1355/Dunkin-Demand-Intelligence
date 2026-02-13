import React, { useState, useEffect } from 'react';
import { Dashboard } from './pages/dashboard/Dashboard';
import { LoginSignup } from './pages/auth/LoginSignup';
import { ForgotPassword } from './pages/auth/ForgotPassword';
import { ResetPassword } from './pages/auth/ResetPassword';
import { apiClient } from './api/client';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [resetToken, setResetToken] = useState('');

  // Default item types for the Dashboard to display
  const [donutTypes, setDonutTypes] = useState<string[]>([
    'Glazed', 
    'Chocolate Frosted', 
    'Boston Kreme', 
    'Strawberry Frosted'
  ]);
  const [munchkinTypes, setMunchkinTypes] = useState<string[]>([
    'Glazed Munchkin', 
    'Chocolate Munchkin', 
    'Jelly Munchkin'
  ]);

  useEffect(() => {
    // Check if user is already logged in on page load
    if (apiClient.isLoggedIn()) {
      const user = apiClient.getUser();
      if (user) {
        setUsername(user.name);
        setIsLoggedIn(true);
      }
    }

    // Check URL for reset token (e.g., ?token=abc123)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      setResetToken(token);
      setShowResetPassword(true);
      setShowAuth(true);
    }
  }, []);

  const handleLogin = (name: string) => {
    setUsername(name);
    setIsLoggedIn(true);
    setShowAuth(false);
  };

  const handleLogout = () => {
    apiClient.logout();
    setIsLoggedIn(false);
    setUsername('');
    setShowAuth(true);
    setAuthMode('login');
  };

  const handleOpenAuth = (mode: 'login' | 'signup') => {
    setAuthMode(mode);
    setShowAuth(true);
  };

  const handleForgotPassword = () => {
    setShowForgotPassword(true);
  };

  const handleBackToLogin = () => {
    setShowForgotPassword(false);
    setShowResetPassword(false);
  };

  const handlePasswordResetSuccess = () => {
    setShowResetPassword(false);
    setShowForgotPassword(false);
    setAuthMode('login');
  };

  // If logged in, show the styled Dashboard instead of the plain DailyEntryForm
  if (isLoggedIn) {
    return (
      <Dashboard 
        username={username}
        onLogout={handleLogout}
        donutTypes={donutTypes}
        munchkinTypes={munchkinTypes}
        onUpdateDonutTypes={setDonutTypes}
        onUpdateMunchkinTypes={setMunchkinTypes}
      />
    );
  }

  // Landing page for users who are not logged in
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#F5F0E8', 
      display: 'flex', 
      flexDirection: 'column', 
      fontFamily: 'sans-serif'
    }}>
      {/* Hero Section with Background Image */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(255,103,31,0.95) 0%, rgba(218,24,132,0.95) 100%)',
        padding: '60px 20px',
        textAlign: 'center',
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Decorative donuts */}
        <div style={{ position: 'absolute', top: '20px', left: '10%', fontSize: '60px', opacity: '0.2', transform: 'rotate(-15deg)' }}>🍩</div>
        <div style={{ position: 'absolute', bottom: '30px', right: '15%', fontSize: '80px', opacity: '0.15', transform: 'rotate(25deg)' }}>🍩</div>
        <div style={{ position: 'absolute', top: '40%', right: '5%', fontSize: '50px', opacity: '0.2', transform: 'rotate(-30deg)' }}>☕</div>
        
        <div style={{ position: 'relative', zIndex: 1, maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ fontSize: '72px', marginBottom: '20px' }}>🍩</div>
          <h1 style={{ marginBottom: '20px', fontSize: '3rem', fontWeight: '900', textShadow: '2px 2px 4px rgba(0,0,0,0.2)' }}>
            Dunkin Demand Intelligence
          </h1>
          <p style={{ fontSize: '1.3rem', marginBottom: '30px', opacity: '0.95' }}>
            Optimizing production through data-driven insights.
          </p>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ padding: '60px 20px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '30px', marginBottom: '60px' }}>
          <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 5px 15px rgba(0,0,0,0.08)', textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>📊</div>
            <h3 style={{ color: '#FF671F', marginBottom: '10px', fontSize: '1.4rem' }}>Real-Time Analytics</h3>
            <p style={{ color: '#8B7355', lineHeight: '1.6' }}>Track production, waste, and sales with live dashboards and intelligent forecasting.</p>
          </div>
          <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 5px 15px rgba(0,0,0,0.08)', textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>🎯</div>
            <h3 style={{ color: '#DA1884', marginBottom: '10px', fontSize: '1.4rem' }}>Accurate Forecasts</h3>
            <p style={{ color: '#8B7355', lineHeight: '1.6' }}>AI-powered predictions help optimize production and reduce waste by up to 30%.</p>
          </div>
          <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 5px 15px rgba(0,0,0,0.08)', textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>⚡</div>
            <h3 style={{ color: '#FF671F', marginBottom: '10px', fontSize: '1.4rem' }}>Quick Entry</h3>
            <p style={{ color: '#8B7355', lineHeight: '1.6' }}>QR code scanning and mobile-friendly forms make data entry effortless.</p>
          </div>
        </div>

        {/* CTA Section */}
        <div style={{ textAlign: 'center', padding: '40px', backgroundColor: 'white', borderRadius: '24px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)' }}>
          <h2 style={{ color: '#FF671F', marginBottom: '15px', fontSize: '2rem', fontWeight: '700' }}>
            Ready to Optimize Your Store?
          </h2>
          <p style={{ color: '#8B7355', marginBottom: '30px', fontSize: '1.1rem' }}>
            Join managers already saving time and reducing waste.
          </p>
          {!showAuth ? (
            <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
              <button
                onClick={() => handleOpenAuth('login')}
                style={{
                  padding: '16px 48px',
                  backgroundColor: '#FF671F',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50px',
                  fontWeight: '700',
                  fontSize: '1.1rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  boxShadow: '0 4px 15px rgba(255,103,31,0.3)'
                }}
                onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                Login
              </button>
              <button
                onClick={() => handleOpenAuth('signup')}
                style={{
                  padding: '16px 48px',
                  backgroundColor: '#DA1884',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50px',
                  fontWeight: '700',
                  fontSize: '1.1rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  boxShadow: '0 4px 15px rgba(218,24,132,0.3)'
                }}
                onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                Sign Up
              </button>
            </div>
          ) : (
            <>
              {showResetPassword ? (
                <ResetPassword 
                  token={resetToken}
                  onClose={() => setShowAuth(false)}
                  onSuccess={handlePasswordResetSuccess}
                />
              ) : showForgotPassword ? (
                <ForgotPassword
                  onClose={() => setShowAuth(false)}
                  onBackToLogin={handleBackToLogin}
                />
              ) : (
                <LoginSignup
                  mode={authMode}
                  onLogin={handleLogin}
                  onToggleMode={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
                  onClose={() => setShowAuth(false)}
                  onForgotPassword={handleForgotPassword}
                />
              )}
            </>
          )}
        </div>
      </div>
      
      {/* Footer */}
      <div style={{ padding: '30px', textAlign: 'center', color: '#8B7355', fontSize: '0.9rem' }}>
        <p>© 2026 Dunkin Demand Intelligence • Powered by data, perfected by experience 🍩</p>
      </div>
    </div>
  );
}