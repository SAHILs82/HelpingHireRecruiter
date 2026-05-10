import React from 'react';
import { Mail, Lock } from 'lucide-react';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

export const EmailField = ({ value, onChange, role = 'seeker', required = true }) => (
  <div className="space-y-2">
    <Label htmlFor="email" className="text-sm font-bold text-slate-700 ml-1">Email Address</Label>
    <div className="relative group">
      <Mail className={`absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 transition-colors ${
        role === 'hr' ? 'group-focus-within:text-amber-500' : 'group-focus-within:text-indigo-500'
      }`} size={18} />
      <Input
        id="email"
        type="email"
        placeholder="name@example.com"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`pl-10 h-12 bg-slate-50 border-slate-200 focus:bg-white transition-all rounded-xl border-2 ${
          role === 'hr' ? 'focus:border-amber-500/50' : 'focus:border-indigo-500/50'
        }`}
        required={required}
      />
    </div>
  </div>
);

export const PasswordField = ({ 
  id = 'password', 
  label = 'Password', 
  value, 
  onChange, 
  role = 'seeker', 
  placeholder = '••••••••',
  showForgot = false,
  required = true 
}) => (
  <div className="space-y-2">
    <div className="flex justify-between items-center ml-1">
      <Label htmlFor={id} className="text-sm font-bold text-slate-700">{label}</Label>
      {showForgot && (
        <a href="#" className={`text-xs font-semibold hover:underline ${
          role === 'hr' ? 'text-amber-600' : 'text-indigo-600'
        }`}>
          Forgot Password?
        </a>
      )}
    </div>
    <div className="relative group">
      <Lock className={`absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 transition-colors ${
        role === 'hr' ? 'group-focus-within:text-amber-500' : 'group-focus-within:text-indigo-500'
      }`} size={18} />
      <Input
        id={id}
        type="password"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`pl-10 h-12 bg-slate-50 border-slate-200 focus:bg-white transition-all rounded-xl border-2 ${
          role === 'hr' ? 'focus:border-amber-500/50' : 'focus:border-indigo-500/50'
        }`}
        required={required}
      />
    </div>
  </div>
);

export const getPasswordStrength = (pass) => {
  let score = 0;
  if (!pass) return { score: 0, text: '', color: 'bg-slate-200', textColor: 'text-slate-500' };
  
  if (pass.length >= 8) score += 1;
  if (/[A-Z]/.test(pass)) score += 1;
  if (/[0-9]/.test(pass)) score += 1;
  if (/[^a-zA-Z0-9]/.test(pass)) score += 1;

  switch (score) {
    case 1: return { score, text: 'Weak', color: 'bg-rose-500', textColor: 'text-rose-500' };
    case 2: return { score, text: 'Fair', color: 'bg-amber-500', textColor: 'text-amber-500' };
    case 3: return { score, text: 'Good', color: 'bg-blue-500', textColor: 'text-blue-500' };
    case 4: return { score, text: 'Strong', color: 'bg-emerald-500', textColor: 'text-emerald-500' };
    default: return { score: 0, text: '', color: 'bg-slate-200', textColor: 'text-slate-500' };
  }
};

export const PasswordStrengthBar = ({ password }) => {
  if (!password || password.length === 0) return null;
  
  const strength = getPasswordStrength(password);

  return (
    <div className="bg-slate-50 p-4 rounded-xl space-y-3">
      <div className="flex justify-between items-center text-xs font-bold">
        <span className="text-slate-500">Password Strength</span>
        <span className={`transition-colors ${strength.textColor}`}>
          {strength.text}
        </span>
      </div>
      <div className="flex gap-1.5 h-1.5 w-full">
        {[1, 2, 3, 4].map((level) => (
          <div 
            key={level} 
            className={`flex-1 rounded-full transition-all duration-500 ${
              level <= strength.score ? strength.color : 'bg-slate-200'
            }`}
          />
        ))}
      </div>
      <div className="text-[10px] font-semibold text-slate-400 mt-2">
        Must contain 8+ characters, uppercase, number, and special character.
      </div>
    </div>
  );
};

