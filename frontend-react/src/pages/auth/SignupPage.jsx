import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { z } from 'zod';
import AuthLayout from '../../components/auth/AuthLayout';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Button } from '../../components/ui/button';
import { Mail, Lock, ArrowRight, User, Briefcase, CheckCircle2, AlertCircle } from 'lucide-react';
import { authAPI } from '../../api/authAPI';
import { EmailField, PasswordField, PasswordStrengthBar } from '../../components/auth/AuthFields';
import { useToast } from '../../components/ui/CustomToast';

const signupSchema = z.object({
  email: z.string().email("Invalid email format (e.g. name@example.com)"),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[0-9]/, "Password must contain at least one number")
    .regex(/[^a-zA-Z0-9]/, "Password must contain at least one special character"),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

const SignupPage = ({ onLogin }) => {
  const toast = useToast();
  const [role, setRole] = useState(null); // null, 'job_seeker', or 'recruiter'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  
  const handleSignup = async (e) => {
    e.preventDefault();
    console.log("Form submitted!");
    console.log("Email:", email, "Password length:", password.length, "Confirm length:", confirmPassword.length);
    if (!role) return;

    // Validation
    const validation = signupSchema.safeParse({ email, password, confirmPassword });
    if (!validation.success) {
      const issues = validation.error?.issues || validation.error?.errors || [];
      const errorMessage = issues[0]?.message || "Invalid input provided";
      console.log("Validation failed:", issues);
      toast.error(errorMessage);
      return;
    }
    
    console.log("Validation passed, making API call");
    setIsLoading(true);
    try {
      await authAPI.signup({ email, password, role });
      
      // Auto login after signup
      const { access_token } = await authAPI.login({ email, password, role });
      localStorage.setItem('project8Token', access_token);
      
      const userData = await authAPI.getCurrentUser(access_token);
      localStorage.setItem('project8User', JSON.stringify(userData));
      
      onLogin(userData);
      toast.success("Account created successfully!");
      navigate(userData.role === 'job_seeker' ? '/' : '/jd-intake');
    } catch (err) {
      toast.error(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!role) {
    return (
      <AuthLayout>
        <div className="text-center md:text-left mb-8">
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">Join HelpingHire</h2>
          <p className="text-slate-500 font-medium text-lg">Choose how you want to use the platform.</p>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => setRole('job_seeker')}
            className="w-full flex items-center p-6 bg-slate-50 border-2 border-slate-200 rounded-2xl transition-all hover:border-indigo-500 hover:bg-indigo-50/30 group text-left"
          >
            <div className="w-14 h-14 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mr-5 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
              <User size={28} />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-slate-900 text-lg">I'm a Job Seeker</h3>
              <p className="text-sm text-slate-500 font-medium">I want to apply for jobs and get AI-matched.</p>
            </div>
            <ArrowRight className="text-slate-300 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" size={24} />
          </button>

          <button
            onClick={() => setRole('recruiter')}
            className="w-full flex items-center p-6 bg-slate-50 border-2 border-slate-200 rounded-2xl transition-all hover:border-amber-500 hover:bg-amber-50/30 group text-left"
          >
            <div className="w-14 h-14 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center mr-5 transition-colors group-hover:bg-amber-600 group-hover:text-white">
              <Briefcase size={28} />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-slate-900 text-lg">I'm a Recruiter</h3>
              <p className="text-sm text-slate-500 font-medium">I want to post jobs and find top talent fast.</p>
            </div>
            <ArrowRight className="text-slate-300 group-hover:text-amber-600 group-hover:translate-x-1 transition-all" size={24} />
          </button>
        </div>

        <div className="text-center pt-8">
          <p className="text-sm font-medium text-slate-500">
            Already have an account? {' '}
            <Link to="/login" className="text-indigo-600 font-bold hover:text-indigo-700">Sign in</Link>
          </p>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout type={role === 'recruiter' ? 'hr' : 'seeker'}>
      <button 
        onClick={() => setRole(null)}
        className="text-sm font-bold text-slate-400 hover:text-slate-600 flex items-center gap-1 mb-4 transition-colors"
      >
        ← Back to selection
      </button>

      <div className="text-center md:text-left">
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">Create Account</h2>
        <p className="text-slate-500 font-medium italic">
          Signing up as <span className={`font-bold not-italic ${role === 'recruiter' ? 'text-amber-600' : 'text-indigo-600'}`}>
            {role === 'recruiter' ? 'HR Recruiter' : 'Job Seeker'}
          </span>
        </p>
      </div>

      <form onSubmit={handleSignup} className="space-y-5" noValidate>
        <EmailField 
          value={email} 
          onChange={setEmail} 
          role={role === 'recruiter' ? 'hr' : 'seeker'} 
        />

        <PasswordField 
          label="Password"
          value={password} 
          onChange={setPassword} 
          role={role === 'recruiter' ? 'hr' : 'seeker'} 
          placeholder="Create a strong password"
        />

        <PasswordField 
          id="confirmPassword"
          label="Confirm Password"
          value={confirmPassword} 
          onChange={setConfirmPassword} 
          role={role === 'recruiter' ? 'hr' : 'seeker'} 
          placeholder="Repeat your password"
        />

        <PasswordStrengthBar password={password} />

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
              Creating account...
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              Get Started <ArrowRight size={18} />
            </div>
          )}
        </Button>
      </form>

      <div className="text-center pt-4">
        <p className="text-sm font-medium text-slate-500">
          By joining, you agree to our <a href="#" className="underline">Terms of Service</a>.
        </p>
      </div>
    </AuthLayout>
  );
};

export default SignupPage;
