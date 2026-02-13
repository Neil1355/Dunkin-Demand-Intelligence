import React from 'react';
import { TrendingUp, Coffee } from 'lucide-react';

interface HeroProps {
  onGetStarted: () => void;
}

export function Hero({ onGetStarted }: HeroProps) {
  return (
    <section 
      className="relative overflow-hidden"
      style={{
        backgroundImage: 'url(/Gemini_Generated_Image_wcpry5wcpry5wcpr.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundColor: '#FFF8F0'
      }}
    >
      {/* Dark overlay for text readability */}
      <div className="absolute inset-0 bg-black/40"></div>
      
      <div className="max-w-7xl mx-auto px-6 py-24 grid md:grid-cols-2 gap-12 items-center relative z-10">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-white drop-shadow-lg">
            Dunkin Demand Intelligence
          </h1>
          <p className="mt-6 text-xl text-white/95 drop-shadow-md">
            Optimizing production through data-driven insights.
          </p>
          <button
            onClick={onGetStarted}
            className="mt-8 px-8 py-4 rounded-full text-white transition-all hover:scale-105 shadow-lg font-semibold"
            style={{ backgroundColor: '#FF671F' }}
          >
            Get Started
          </button>
        </div>
        
        <div className="relative">
          <div className="bg-white/95 rounded-3xl shadow-2xl p-8 transform rotate-2 hover:rotate-0 transition-transform">
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
