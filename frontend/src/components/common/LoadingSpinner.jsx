import React from 'react';
export default function LoadingSpinner({ size = 'md', text = 'Analyzing...' }) {
  const s = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size];
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <div className={`${s} border-2 border-agri-600 border-t-transparent rounded-full animate-spin`} />
      {text && <span className="text-sm text-slate-400">{text}</span>}
    </div>
  );
}
