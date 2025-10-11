import React from 'react';
import { CheckCircleIcon } from '@heroicons/react/24/outline';

export const AuthHero: React.FC = () => {
  const features = [
    'AI-powered job description parsing',
    'GitHub developer search & ranking',
    'Personalized outreach generation',
    'Track recruitment pipelines',
  ];

  return (
    <div className="hidden lg:flex lg:flex-1 hero-gradient relative overflow-hidden">
      <div className="absolute inset-0 mesh-gradient opacity-30" />

      <div className="relative z-10 flex flex-col justify-center px-12 py-16 text-white">
        <div className="max-w-md">
          <h1 className="text-4xl font-bold mb-4 animate-fade-in">
            Find Your Next Developer
          </h1>
          <p className="text-lg text-primary-100 mb-8 animate-slide-in-up">
            AI-powered recruitment platform that sources, ranks, and helps you reach out to software developers using GitHub.
          </p>

          <div className="space-y-4">
            {features.map((feature, index) => (
              <div
                key={index}
                className="flex items-start gap-3 stagger-item"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CheckCircleIcon className="h-6 w-6 text-secondary-300 flex-shrink-0 mt-0.5" />
                <span className="text-primary-50">{feature}</span>
              </div>
            ))}
          </div>

          <div className="mt-12 pt-8 border-t border-primary-400/30">
            <p className="text-sm text-primary-200">
              Join <span className="font-semibold text-white">500+</span> recruiters finding top talent on GitHub
            </p>
          </div>
        </div>
      </div>

      {/* Decorative elements */}
      <div className="absolute top-20 right-20 w-64 h-64 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow" />
      <div className="absolute bottom-20 left-20 w-64 h-64 bg-secondary-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow" style={{ animationDelay: '1s' }} />
    </div>
  );
};

export default AuthHero;
