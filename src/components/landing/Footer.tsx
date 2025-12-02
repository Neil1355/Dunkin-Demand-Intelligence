import React from 'react';

export function Footer() {
  return (
    <footer className="py-8" style={{ backgroundColor: '#FFF8F0' }}>
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-center gap-8">
          <button className="hover:opacity-70 transition-opacity" style={{ color: '#8B7355' }}>
            About
          </button>
          <button className="hover:opacity-70 transition-opacity" style={{ color: '#8B7355' }}>
            Contact
          </button>
          <button className="hover:opacity-70 transition-opacity" style={{ color: '#8B7355' }}>
            Privacy
          </button>
        </div>
        <div className="mt-4 text-center text-sm" style={{ color: '#8B7355' }}>
          © 2025 Dunkin' Demand Intelligence. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
