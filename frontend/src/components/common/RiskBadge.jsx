import React from 'react';

const RISK_CONFIG = {
  low:      { label: 'Low Risk',    bg: 'bg-emerald-900/50', text: 'text-emerald-400', border: 'border-emerald-700' },
  medium:   { label: 'Medium Risk', bg: 'bg-amber-900/50',   text: 'text-amber-400',   border: 'border-amber-700' },
  high:     { label: 'High Risk',   bg: 'bg-orange-900/50',  text: 'text-orange-400',  border: 'border-orange-700' },
  critical: { label: 'Critical',    bg: 'bg-red-900/50',     text: 'text-red-400',     border: 'border-red-700', pulse: true },
  healthy:  { label: 'Healthy',     bg: 'bg-emerald-900/50', text: 'text-emerald-400', border: 'border-emerald-700' },
  early_stress:  { label: 'Early Stress', bg: 'bg-yellow-900/50', text: 'text-yellow-400', border: 'border-yellow-700' },
  disease_risk:  { label: 'Disease Risk', bg: 'bg-orange-900/50', text: 'text-orange-400', border: 'border-orange-700' },
  severe_stress: { label: 'Severe Stress', bg: 'bg-red-900/50', text: 'text-red-400', border: 'border-red-700', pulse: true },
};

export default function RiskBadge({ level, size = 'sm' }) {
  const config = RISK_CONFIG[level] || RISK_CONFIG.low;
  const sizeClass = size === 'lg' ? 'text-sm px-3 py-1.5' : 'text-xs px-2 py-0.5';

  return (
    <span className={`
      inline-flex items-center gap-1 rounded-full border font-medium
      ${config.bg} ${config.text} ${config.border} ${sizeClass}
      ${config.pulse ? 'risk-critical' : ''}
    `}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.text.replace('text-', 'bg-')}`} />
      {config.label}
    </span>
  );
}
