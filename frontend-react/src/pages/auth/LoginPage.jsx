import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { z } from 'zod';
import AuthLayout from '../../components/auth/AuthLayout';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Button } from '../../components/ui/button';
import { Mail, Lock, ArrowRight, User, Briefcase, AlertCircle } from 'lucide-react';
import { authAPI } from '../../api/authAPI';
import { EmailField, PasswordField } from '../../components/auth/AuthFields';
import { useToast } from '../../components/ui/CustomToast';

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address (e.g., name@example.com)"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

const LoginPage = ({ onLogin }) => {
  const toast = useToast();
  const [role, setRole] = useState('job_seeker');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Validation
    const validation = loginSchema.safeParse({ email, password });
    if (!validation.success) {
      const issues = validation.error?.issues || validation.error?.errors || [];
      const errorMessage = issues[0]?.message || "Invalid input provided";
      toast.error(errorMessage);
      return;
    }
    
    setIsLoading(true);
    try {
      const { access_token } = await authAPI.login({ email, password, role });
      localStorage.setItem('project8Token', access_token);
      
      const userData = await authAPI.getCurrentUser(access_token);
      localStorage.setItem('project8User', JSON.stringify(userData));
      
      onLogin(userData);
      toast.success(`Welcome back, ${email.split('@')[0]}!`);
      navigate(userData.role === 'job_seeker' ? '/' : '/jd-intake');
    } catch (err) {
      toast.error(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout type={role === 'recruiter' ? 'hr' : 'seeker'}>
      <div className="text-center md:text-left">
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">Welcome Back</h2>
        <p className="text-slate-500 font-medium">Please enter your details to sign in.</p>
      </div>

      {/* Role Switcher */}
      <div className="flex p-1 bg-slate-100 rounded-xl gap-1">
        <button
          onClick={() => setRole('job_seeker')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 ${
            role === 'job_seeker' 
              ? 'bg-white text-indigo-600 shadow-sm' 
              : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
          }`}
        >
          <User size={16} />
          Job Seeker
        </button>
        <button
          onClick={() => setRole('recruiter')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 ${
            role === 'recruiter' 
              ? 'bg-white text-amber-600 shadow-sm' 
              : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
          }`}
        >
          <Briefcase size={16} />
          HR Portal
        </button>
      </div>

      <form onSubmit={handleLogin} className="space-y-5" noValidate>
        <EmailField 
          value={email} 
          onChange={setEmail} 
          role={role === 'recruiter' ? 'hr' : 'seeker'} 
        />

        <PasswordField 
          value={password} 
          onChange={setPassword} 
          role={role === 'recruiter' ? 'hr' : 'seeker'} 
          showForgot={true}
        />

        <Button 
          type="submit" 
          disabled={isLoading}
          className={`w-full h-12 text-base font-bold rounded-xl transition-all duration-300 shadow-lg ${
            role === 'recruiter' 
              ? 'bg-amber-600 hover:bg-amber-700 shadow-amber-200' 
              : 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Signing in...
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              Sign In <ArrowRight size={18} />
            </div>
          )}
        </Button>
      </form>

      <div className="text-center pt-4">
        <p className="text-sm font-medium text-slate-500">
          Don't have an account? {' '}
          <Link 
            to="/signup" 
            className={`font-bold transition-colors ${role === 'recruiter' ? 'text-amber-600 hover:text-amber-700' : 'text-indigo-600 hover:text-indigo-700'}`}
          >
            Create one now
          </Link>
        </p>
      </div>

      <div className="relative py-4">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-200"></div>
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-4 text-slate-400 font-bold tracking-widest">Or continue with</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Button variant="outline" className="h-11 rounded-xl border-slate-200 font-bold text-slate-600 hover:bg-slate-50">
          <img src="https://www.google.com/favicon.ico" className="w-4 h-4 mr-2 grayscale opacity-70" alt="Google" />
          Google
        </Button>
        <Button variant="outline" className="h-11 rounded-xl border-slate-200 font-bold text-slate-600 hover:bg-slate-50">
          <img src="https://github.githubassets.com/favicon.ico" className="w-4 h-4 mr-2 grayscale opacity-70" alt="GitHub" />
          GitHub
        </Button>
      </div>
    </AuthLayout>
  );
};

export default LoginPage;
