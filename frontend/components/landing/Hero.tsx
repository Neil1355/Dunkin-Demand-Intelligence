import React from 'react';
import { TrendingUp, Coffee } from 'lucide-react';

interface HeroProps {
  onGetStarted: () => void;
}

export function Hero({ onGetStarted }: HeroProps) {
  return (
    <section className="relative overflow-hidden" style={{ backgroundColor: '#FFF8F0' }}>
      {/* Decorative background shapes */}
      <div className="absolute top-20 right-10 w-64 h-64 rounded-full opacity-10" style={{ backgroundColor: '#DA1884' }}></div>
      <div className="absolute bottom-10 left-20 w-48 h-48 rounded-full opacity-10" style={{ backgroundColor: '#FF671F' }}></div>
      
      <div className="max-w-7xl mx-auto px-6 py-24 grid md:grid-cols-2 gap-12 items-center relative z-10">
        <div>
          <h1 style={{ color: '#FF671F' }}>
            Smarter Donut Forecasting for Your Dunkin' Store.
          </h1>
          <p className="mt-6" style={{ color: '#8B7355' }}>
            Track production. Reduce waste. Get AI-powered predictions for tomorrow's donut and munchkin orders.
          </p>
          <button
            onClick={onGetStarted}
            className="mt-8 px-8 py-4 rounded-full text-white transition-all hover:scale-105 shadow-lg"
            style={{ backgroundColor: '#FF671F' }}
          >
            Get Started
          </button>
        </div>
        
        <div className="relative">
          <div className="bg-white rounded-3xl shadow-2xl p-8 transform rotate-2 hover:rotate-0 transition-transform">
            <div className="flex items-center gap-4 mb-6">
              <Coffee size={48} style={{ color: '#DA1884' }} />
              <div>
                <div className="text-sm" style={{ color: '#8B7355' }}>Today's Forecast</div>
                <div className="text-3xl" style={{ color: '#FF671F' }}>85 Dozen</div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-green-600">
              <TrendingUp size={20} />
              <span>12% less waste this week</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
