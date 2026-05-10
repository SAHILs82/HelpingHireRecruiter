import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { X, CheckCircle2, AlertCircle, Info, Bell } from 'lucide-react';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
      removeToast(id);
    }, 4000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-3 w-full max-w-md px-4 pointer-events-none">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} {...toast} onRemove={() => removeToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within a ToastProvider');
  
  return {
    success: (msg) => context.addToast(msg, 'success'),
    error: (msg) => context.addToast(msg, 'error'),
    info: (msg) => context.addToast(msg, 'info'),
  };
};

const ToastItem = ({ message, type, onRemove }) => {
  const configs = {
    success: {
      icon: <CheckCircle2 size={20} />,
      bg: 'bg-emerald-500',
      border: 'border-emerald-600',
      shadow: 'shadow-emerald-200/50'
    },
    error: {
      icon: <AlertCircle size={20} />,
      bg: 'bg-rose-500',
      border: 'border-rose-600',
      shadow: 'shadow-rose-200/50'
    },
    info: {
      icon: <Info size={20} />,
      bg: 'bg-indigo-500',
      border: 'border-indigo-600',
      shadow: 'shadow-indigo-200/50'
    }
  };

  const config = configs[type] || configs.info;

  return (
    <div className={`
      pointer-events-auto
      flex items-center gap-3 p-4 rounded-2xl border-2 text-white font-bold shadow-xl
      animate-in slide-in-from-top-4 fade-in duration-300
      ${config.bg} ${config.border} ${config.shadow}
    `}>
      <div className="shrink-0 bg-white/20 p-1 rounded-lg">
        {config.icon}
      </div>
      <p className="flex-1 text-sm leading-tight">{message}</p>
      <button 
        onClick={onRemove}
        className="shrink-0 hover:bg-white/20 p-1 rounded-lg transition-colors"
      >
        <X size={18} />
      </button>
    </div>
  );
};
