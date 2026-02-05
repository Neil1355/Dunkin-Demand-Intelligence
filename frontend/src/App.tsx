import React, { useState, useEffect } from 'react';
import DailyEntryForm from "./components/DailyEntryForm";
import { LoginSignup } from './pages/auth/LoginSignup';
import { apiClient } from './api/client';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  useEffect(() => {
    // Check if user is already logged in
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

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1>Dunkin Demand Intelligence</h1>
        {isLoggedIn && (
          <div>
            <span style={{ marginRight: 20 }}>Welcome, {username}</span>
            <button
              onClick={handleLogout}
              style={{
                padding: '10px 20px',
                backgroundColor: '#FF671F',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>

      {isLoggedIn ? (
        <DailyEntryForm />
      ) : (
        <div>
          {!showAuth && (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <p style={{ marginBottom: 20 }}>Please log in to continue</p>
              <button
                onClick={() => handleOpenAuth('login')}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#FF671F',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  marginRight: 10
                }}
              >
                Login
              </button>
              <button
                onClick={() => handleOpenAuth('signup')}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#DA1884',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer'
                }}
              >
                Sign Up
              </button>
            </div>
          )}
          {showAuth && (
            <LoginSignup
              mode={authMode}
              onLogin={handleLogin}
              onToggleMode={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
              onClose={() => setShowAuth(false)}
            />
          )}
        </div>
      )}
    </div>
  );
}