import React from 'react';

interface HeaderProps {
  onNavigate: (page: string) => void;
}

export function Header({ onNavigate }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <button 
          onClick={() => onNavigate('landing')}
          className="flex items-center gap-2 hover:opacity-80 transition-opacity"
        >
          <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#FF671F' }}>
            <span className="text-white text-2xl">🍩</span>
          </div>
          <span className="text-2xl" style={{ color: '#FF671F' }}>
            Dunkin' Demand Intelligence
          </span>
        </button>
        
        <div className="flex gap-3">
          <button
            onClick={() => onNavigate('login')}
            className="px-6 py-2.5 rounded-full border-2 transition-all hover:scale-105"
            style={{ 
              borderColor: '#FF671F',
              color: '#FF671F'
            }}
          >
            Login
          </button>
          <button
            onClick={() => onNavigate('signup')}
            className="px-6 py-2.5 rounded-full transition-all hover:scale-105 text-white"
            style={{ backgroundColor: '#DA1884' }}
          >
            Sign Up
          </button>
        </div>
      </div>
    </header>
  );
}
