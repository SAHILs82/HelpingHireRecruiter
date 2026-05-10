import React from 'react';
import authSeekerImg from '../../assets/auth_seeker.png';
import authHrImg from '../../assets/auth_hr.png';

const AuthLayout = ({ children, type = 'seeker' }) => {
  const bgImage = type === 'hr' ? authHrImg : authSeekerImg;
  const accentColor = type === 'hr' ? 'bg-amber-600' : 'bg-indigo-600';
  const tagline = type === 'hr' 
    ? "Empower your team with AI-driven talent acquisition."
    : "Your next career milestone starts with deep-agent intelligence.";

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-slate-50 font-sans selection:bg-indigo-100 selection:text-indigo-900">
      {/* Visual Side */}
      <div className="hidden md:flex md:w-1/2 relative overflow-hidden bg-slate-900 items-center justify-center">
        <div className="absolute inset-0 z-0">
          <img 
            src={bgImage} 
            alt="Authentication Background" 
            className="w-full h-full object-cover opacity-60 mix-blend-overlay scale-110 animate-pulse-slow"
          />
          <div className="absolute inset-0 bg-gradient-to-tr from-slate-900/90 via-slate-900/40 to-transparent" />
        </div>
        
        <div className="relative z-10 p-12 lg:p-20 text-white max-w-xl">
          <div className="flex items-center gap-3 mb-8 group cursor-default">
            <div className={`w-12 h-12 rounded-2xl ${accentColor} flex items-center justify-center text-2xl font-black shadow-xl shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-500`}>
              HH
            </div>
            <span className="text-3xl font-black tracking-tight">HelpingHire <span className="text-indigo-400">AI</span></span>
          </div>
          
          <h1 className="text-4xl lg:text-5xl font-extrabold mb-6 leading-tight tracking-tight">
            Elevate your <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">hiring journey</span> with deep agents.
          </h1>
          <p className="text-xl text-slate-300 font-medium leading-relaxed">
            {tagline}
          </p>
          
          <div className="mt-12 flex gap-4">
            <div className="px-4 py-2 bg-white/5 backdrop-blur-md rounded-full border border-white/10 text-sm font-semibold">
              ✨ AI Powered
            </div>
            <div className="px-4 py-2 bg-white/5 backdrop-blur-md rounded-full border border-white/10 text-sm font-semibold">
              🚀 Rapid Match
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl" />
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-cyan-600/20 rounded-full blur-3xl" />
      </div>

      {/* Content Side */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12 bg-white">
        <div className="w-full max-w-md space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
          {children}
        </div>
      </div>
      
      <style jsx>{`
        @keyframes pulse-slow {
          0%, 100% { transform: scale(1.1); }
          50% { transform: scale(1.15); }
        }
        .animate-pulse-slow {
          animation: pulse-slow 15s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default AuthLayout;
