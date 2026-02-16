import React, { useState, useEffect } from 'react';
import { Dashboard } from './pages/dashboard/Dashboard';
import { LoginSignup } from './pages/auth/LoginSignup';
import { ForgotPassword } from './pages/auth/ForgotPassword';
import { ResetPassword } from './pages/auth/ResetPassword';
import { apiClient } from './api/client';
import heroImage from './components/landing/Gemini_Generated_Image_wcpry5wcpry5wcpr.png';
import sprinklesBackground from './components/landing/sprinkles background.png';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [storeId, setStoreId] = useState<number>(12345);
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
    const user = apiClient.getUser();
    if (user && user.store_id) {
      setStoreId(user.store_id);
    }
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
        storeId={storeId}
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
      backgroundImage: `url(${sprinklesBackground})`,
      backgroundRepeat: 'repeat',
      backgroundSize: '600px 600px',
      display: 'flex', 
      flexDirection: 'column', 
      fontFamily: 'sans-serif'
    }}>
      {/* Hero Section with Background Image */}
      <div style={{
        backgroundImage: `url(${heroImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center right',
        padding: '80px 20px',
        color: '#4A2C2A',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center'
      }}>
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(90deg, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0.45) 50%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none'
        }}></div>
        <div style={{
          position: 'relative',
          zIndex: 1,
          maxWidth: '560px',
          marginLeft: '8%',
          textAlign: 'left'
        }}>
          <h1 style={{
            marginBottom: '18px',
            fontSize: '3rem',
            fontWeight: 800,
            color: '#BF5F18',
            fontFamily: '"Montserrat", "Poppins", sans-serif',
            letterSpacing: '0.2px'
          }}>
            Dunkin Demand Intelligence
          </h1>
          <p style={{
            fontSize: '1.35rem',
            marginBottom: '30px',
            color: '#F58220',
            fontFamily: '"Inter", "Roboto", sans-serif',
            lineHeight: 1.5,
            fontWeight: 600
          }}>
            Real-time forecasting powered by AI.
          </p>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" style={{ padding: '60px 20px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
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
      <div style={{ 
        backgroundColor: '#4A2C2A', 
        padding: '40px 60px',
        marginTop: '60px',
        borderTop: '4px solid #F58220'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto', 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '40px',
          color: '#F5F0E8'
        }}>
          {/* Left Column - About */}
          <div>
            <h3 style={{ 
              color: '#F58220', 
              fontSize: '1.1rem', 
              marginBottom: '15px',
              fontFamily: 'Montserrat, sans-serif',
              fontWeight: 700
            }}>About</h3>
            <p style={{ fontSize: '0.9rem', lineHeight: '1.6', margin: 0 }}>
              Dunkin Demand Intelligence leverages data-driven forecasting to optimize inventory, 
              reduce waste, and maximize profitability for Dunkin locations.
            </p>
          </div>

          {/* Center Column - Quick Links */}
          <div>
            <h3 style={{ 
              color: '#F58220', 
              fontSize: '1.1rem', 
              marginBottom: '15px',
              fontFamily: 'Montserrat, sans-serif',
              fontWeight: 700
            }}>Quick Links</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <a 
                href="#features" 
                style={{ 
                  color: '#F5F0E8', 
                  textDecoration: 'none', 
                  fontSize: '0.9rem',
                  transition: 'color 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#F58220'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#F5F0E8'}
              >
                Features
              </a>
              <a 
                href="https://github.com/Neil1355/Dunkin-Demand-Intelligence" 
                target="_blank"
                rel="noopener noreferrer"
                style={{ 
                  color: '#F5F0E8', 
                  textDecoration: 'none', 
                  fontSize: '0.9rem',
                  transition: 'color 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#F58220'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#F5F0E8'}
              >
                GitHub Repository
              </a>
              <a 
                href="https://www.linkedin.com/in/neilbarot5/" 
                target="_blank"
                rel="noopener noreferrer"
                style={{ 
                  color: '#F5F0E8', 
                  textDecoration: 'none', 
                  fontSize: '0.9rem',
                  transition: 'color 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#F58220'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#F5F0E8'}
              >
                LinkedIn
              </a>
            </div>
          </div>

          {/* Right Column - Contact */}
          <div>
            <h3 style={{ 
              color: '#F58220', 
              fontSize: '1.1rem', 
              marginBottom: '15px',
              fontFamily: 'Montserrat, sans-serif',
              fontWeight: 700
            }}>Contact</h3>
            <p style={{ fontSize: '0.9rem', margin: '0 0 10px 0' }}>
              Created by <strong>Neil Barot</strong>
            </p>
            <a 
              href="mailto:neil.barot.jopspace@gmail.com"
              style={{ 
                color: '#F5F0E8', 
                textDecoration: 'none', 
                fontSize: '0.9rem',
                transition: 'color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#F58220'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#F5F0E8'}
            >
              neil.barot.jopspace@gmail.com
            </a>
          </div>
        </div>

        {/* Footer Bottom - Copyright */}
        <div style={{ 
          textAlign: 'center', 
          marginTop: '30px', 
          paddingTop: '25px', 
          borderTop: '1px solid rgba(245, 240, 232, 0.2)',
          color: '#F5F0E8',
          fontSize: '0.85rem'
        }}>
          © 2026 Dunkin Demand Intelligence • Powered by data, perfected by experience 🍩
        </div>
      </div>
    </div>
  );
}