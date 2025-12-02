import React, { useState } from 'react';
import { Header } from './components/landing/Header';
import { Hero } from './components/landing/Hero';
import { Features } from './components/landing/Features';
import { Footer } from './components/landing/Footer';
import { LoginSignup } from './pages/auth/LoginSignup';
import { Dashboard } from './pages/dashboard/Dashboard';

export default function App() {
  const [currentPage, setCurrentPage] = useState<'landing' | 'login' | 'signup' | 'dashboard'>('landing');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');

  // Initialize with default donut and munchkin types
  const [donutTypes, setDonutTypes] = useState([
    'Glazed', 'Chocolate Frosted', 'Boston Kreme', 'Strawberry Frosted',
    'Jelly Filled', 'Vanilla Frosted', 'Old Fashioned', 'Blueberry Cake',
    'French Cruller', 'Powdered Sugar', 'Cinnamon Sugar', 'Maple Frosted'
  ]);

  const [munchkinTypes, setMunchkinTypes] = useState([
    'Glazed Munchkins', 'Chocolate Munchkins', 'Jelly Munchkins', 'Powdered Munchkins'
  ]);

  const handleGetStarted = () => {
    setCurrentPage('signup');
  };

  const handleLogin = (name: string) => {
    setUsername(name);
    setIsLoggedIn(true);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentPage('landing');
  };

  const handleNavigate = (page: string) => {
    if (page === 'landing') {
      setCurrentPage('landing');
    } else if (page === 'login') {
      setCurrentPage('login');
    } else if (page === 'signup') {
      setCurrentPage('signup');
    }
  };

  const toggleLoginSignup = () => {
    setCurrentPage(currentPage === 'login' ? 'signup' : 'login');
  };

  const handleCloseAuth = () => {
    setCurrentPage('landing');
  };

  if (currentPage === 'dashboard' && isLoggedIn) {
    return (
      <Dashboard
        onLogout={handleLogout}
        username={username}
        donutTypes={donutTypes}
        munchkinTypes={munchkinTypes}
        onUpdateDonutTypes={setDonutTypes}
        onUpdateMunchkinTypes={setMunchkinTypes}
      />
    );
  }

  if (currentPage === 'login' || currentPage === 'signup') {
    return (
      <LoginSignup
        mode={currentPage}
        onLogin={handleLogin}
        onToggleMode={toggleLoginSignup}
        onClose={handleCloseAuth}
      />
    );
  }

  return (
    <div className="min-h-screen">
      <Header onNavigate={handleNavigate} />
      <Hero onGetStarted={handleGetStarted} />
      <Features />
      <Footer />
    </div>
  );
}