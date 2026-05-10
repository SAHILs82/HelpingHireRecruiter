import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Users, 
  Settings, 
  LogOut,
  Briefcase
} from 'lucide-react';
import { Button } from '../components/ui/button';

export default function AppLayout({ user, onLogout }) {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'JD Intake', path: '/jd-intake', icon: <FileText size={20} /> },
    { name: 'Candidates', path: '/candidates', icon: <Users size={20} /> },
    { name: 'Job Listings', path: '/jobs', icon: <Briefcase size={20} /> },
  ];

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-50 font-sans">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 border-r bg-white flex flex-col shadow-xl z-30">
        <div className="h-20 flex items-center px-8 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center text-xl font-black shadow-lg shadow-amber-200">
              HH
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight text-slate-900 leading-none">HelpingHire</span>
              <span className="text-[10px] font-bold text-amber-600 uppercase tracking-[0.2em] mt-1">HR Portal</span>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-8 px-4 space-y-2">
          <div className="px-4 mb-4">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Recruitment Hub</span>
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-300 text-sm font-bold ${
                  isActive 
                    ? "bg-amber-50 text-amber-700 shadow-sm border border-amber-100" 
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900 border border-transparent"
                }`
              }
            >
              <span className={({ isActive }) => isActive ? "text-amber-600" : "text-slate-400"}>
                {item.icon}
              </span>
              {item.name}
            </NavLink>
          ))}
        </nav>

        <div className="p-6 border-t border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-4 mb-6 px-2">
            <div className="w-12 h-12 rounded-2xl bg-white shadow-md border border-slate-200 flex items-center justify-center text-lg font-black text-amber-600">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-black text-slate-900 truncate leading-none mb-1">{user?.email || 'User'}</span>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Administrator</span>
            </div>
          </div>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-xl h-12 font-bold transition-all group" 
            onClick={onLogout}
          >
            <LogOut size={18} className="mr-3 group-hover:-translate-x-1 transition-transform" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-20 flex items-center justify-between px-10 bg-white/80 backdrop-blur-md border-b border-slate-100 sticky top-0 z-20">
          <div>
            <h1 className="text-xl font-black text-slate-900 tracking-tight">
              {navItems.find(item => window.location.pathname === item.path)?.name || 'Recruiter Workspace'}
            </h1>
            <p className="text-xs font-bold text-slate-400 mt-0.5 uppercase tracking-wider">AI-Enhanced Talent Acquisition</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex -space-x-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-slate-200" />
              ))}
              <div className="w-8 h-8 rounded-full border-2 border-white bg-amber-600 text-white text-[10px] font-black flex items-center justify-center">+5</div>
            </div>
          </div>
        </header>
        
        <div className="flex-1 overflow-y-auto p-10 bg-slate-50/30">
          <div className="mx-auto max-w-6xl animate-in fade-in slide-in-from-bottom-4 duration-700">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
