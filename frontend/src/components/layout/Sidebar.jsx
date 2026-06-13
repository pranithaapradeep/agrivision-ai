import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { path: '/',           icon: '🌾', label: 'Dashboard'      },
  { path: '/crop',       icon: '🔬', label: 'Crop Health'    },
  { path: '/soil',       icon: '🪱', label: 'Soil Analysis'  },
  { path: '/pest',       icon: '🐛', label: 'Pest Risk'      },
  { path: '/forecast',   icon: '📈', label: 'Forecasting'    },
  { path: '/reports',    icon: '📄', label: 'Reports'        },
  { path: '/admin',      icon: '⚙️',  label: 'Admin'          },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`bg-slate-900 border-r border-slate-800 flex flex-col transition-all duration-300
                       ${collapsed ? 'w-16' : 'w-56'} min-h-screen`}>
      {/* Logo */}
      <div className="p-4 border-b border-slate-800 flex items-center gap-3">
        <span className="text-2xl flex-shrink-0">🌿</span>
        {!collapsed && (
          <div>
            <div className="font-bold text-agri-400 text-sm leading-tight">AgriVision</div>
            <div className="text-xs text-slate-500">AI Platform</div>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="ml-auto text-slate-500 hover:text-slate-300 text-xs"
        >{collapsed ? '→' : '←'}</button>
      </div>

      {/* Nav items */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors
               ${isActive
                 ? 'bg-agri-900 text-agri-400 font-medium'
                 : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'}`
            }
          >
            <span className="flex-shrink-0">{item.icon}</span>
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* SIH badge */}
      {!collapsed && (
        <div className="p-4 border-t border-slate-800">
          <div className="text-xs text-slate-600 text-center">
            <div className="font-medium text-agri-700">SIH 2024</div>
            <div>Problem #25099</div>
          </div>
        </div>
      )}
    </aside>
  );
}
