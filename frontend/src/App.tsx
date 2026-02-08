import React, { useState, useEffect } from 'react';
import { Dashboard } from './pages/dashboard/Dashboard';
import { LoginSignup } from './pages/auth/LoginSignup';
import { apiClient } from './api/client';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

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
      alignItems: 'center', 
      justifyContent: 'center',
      fontFamily: 'sans-serif'
    }}>
      <div style={{ textAlign: 'center', padding: '40px', backgroundColor: 'white', borderRadius: '24px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)' }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>🍩</div>
        <h1 style={{ color: '#FF671F', marginBottom: '10px', fontSize: '2.5rem', fontWeight: '800' }}>
          Dunkin Demand Intelligence
        </h1>
        
        {!showAuth ? (
          <div style={{ marginTop: '30px' }}>
            <p style={{ color: '#8B7355', marginBottom: '30px', fontSize: '1.1rem' }}>
              Optimizing production through data-driven insights.
            </p>
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <button
                onClick={() => handleOpenAuth('login')}
                style={{
                  padding: '12px 32px',
                  backgroundColor: '#FF671F',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}
              >
                Login
              </button>
              <button
                onClick={() => handleOpenAuth('signup')}
                style={{
                  padding: '12px 32px',
                  backgroundColor: '#DA1884',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}
              >
                Sign Up
              </button>
            </div>
          </div>
        ) : (
          <div style={{ marginTop: '20px' }}>
            <LoginSignup
              mode={authMode}
              onLogin={handleLogin}
              onToggleMode={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
              onClose={() => setShowAuth(false)}
            />
          </div>
        )}
      </div>
    </div>
  );
}