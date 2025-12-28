import React from 'react';
import { Pencil, TrendingDown, Brain } from 'lucide-react';

export function Features() {
  const features = [
    {
      icon: Pencil,
      title: 'Daily Product Input',
      description: 'Enter quantities for each donut & munchkin variety with an intuitive, fast interface.',
      color: '#FF671F'
    },
    {
      icon: TrendingDown,
      title: 'Waste Tracking & Analytics',
      description: 'Automatically detect excess and shortages with visual reports and trend analysis.',
      color: '#DA1884'
    },
    {
      icon: Brain,
      title: 'AI Forecasting',
      description: 'Predicts optimal next-day order quantities based on historical patterns and trends.',
      color: '#FF671F'
    }
  ];

  return (
    <section className="py-20" style={{ backgroundColor: '#F5F0E8' }}>
      <div className="max-w-7xl mx-auto px-6">
        <h2 className="text-center mb-16" style={{ color: '#FF671F' }}>
          Everything You Need to Optimize Your Store
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1"
            >
              <div 
                className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6"
                style={{ backgroundColor: `${feature.color}15` }}
              >
                <feature.icon size={32} style={{ color: feature.color }} strokeWidth={2.5} />
              </div>
              <h3 className="mb-4" style={{ color: '#FF671F' }}>
                {feature.title}
              </h3>
              <p style={{ color: '#8B7355' }}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
