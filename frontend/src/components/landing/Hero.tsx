import React from 'react';
import { TrendingUp, Coffee } from 'lucide-react';
import heroImage from './Gemini_Generated_Image_wcpry5wcpry5wcpr.png';

interface HeroProps {
  onGetStarted: () => void;
}

export function Hero({ onGetStarted }: HeroProps) {
  return (
    <section 
      className="relative overflow-hidden min-h-screen flex items-center"
      style={{
        backgroundImage: `url(${heroImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
        backgroundRepeat: 'no-repeat'
      }}
    >
      
      <div className="max-w-7xl mx-auto px-6 py-32 flex items-center justify-between w-full">
        <div className="flex-1">
          <h1 className="text-5xl md:text-6xl font-bold text-white drop-shadow-2xl mb-6">
            Dunkin Demand Intelligence
          </h1>
          <p className="text-2xl text-white/95 drop-shadow-lg mb-8 max-w-lg">
            Optimizing production through data-driven insights.
          </p>
          <button
            onClick={onGetStarted}
            className="px-10 py-4 rounded-full text-white transition-all hover:scale-105 shadow-lg font-semibold text-lg"
            style={{ backgroundColor: '#FF671F' }}
          >
            Get Started
          </button>
        </div>
        
        <div className="flex-1 hidden md:flex justify-end">
          <div className="bg-white/95 rounded-3xl shadow-2xl p-8 w-full max-w-sm">
            <div className="flex items-center gap-4 mb-6">
              <Coffee size={48} style={{ color: '#DA1884' }} />
              <div>
                <div className="text-sm" style={{ color: '#8B7355' }}>Today's Forecast</div>
                <div className="text-3xl font-bold" style={{ color: '#FF671F' }}>85 Dozen</div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-green-600 font-semibold">
              <TrendingUp size={20} />
              <span>12% less waste this week</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
