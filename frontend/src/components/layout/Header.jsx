import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const PAGE_TITLES = {
  '/':         { title: 'Dashboard',     icon: '🌾' },
  '/crop':     { title: 'Crop Health',   icon: '🔬' },
  '/soil':     { title: 'Soil Analysis', icon: '🪱' },
  '/pest':     { title: 'Pest Risk',     icon: '🐛' },
  '/forecast': { title: 'Forecasting',   icon: '📈' },
  '/reports':  { title: 'Reports',       icon: '📄' },
  '/admin':    { title: 'Admin',         icon: '⚙️'  },
};

export default function Header({ alertCount = 0 }) {
  const location = useLocation();
  const info = PAGE_TITLES[location.pathname] || { title: 'AgriVision', icon: '🌿' };
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-xl">{info.icon}</span>
        <h1 className="font-semibold text-slate-100">{info.title}</h1>
        <span className="hidden md:block text-xs text-slate-600 bg-slate-800 px-2 py-0.5 rounded">
          AI-Powered
        </span>
      </div>

      <div className="flex items-center gap-4">
        {/* Live time */}
        <span className="text-xs text-slate-500 hidden md:block">
          {time.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', hour12: false })} IST
        </span>

        {/* Alerts bell */}
        <button className="relative text-slate-400 hover:text-slate-200">
          🔔
          {alertCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-4 h-4 rounded-full flex items-center justify-center font-bold">
              {alertCount > 9 ? '9+' : alertCount}
            </span>
          )}
        </button>

        {/* User avatar */}
        <div className="w-8 h-8 rounded-full bg-agri-800 flex items-center justify-center text-agri-300 text-sm font-medium">
          U
        </div>
      </div>
    </header>
  );
}
