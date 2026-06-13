import React from 'react';

export default function ScoreGauge({ score, label, size = 120 }) {
  const clamp = Math.min(100, Math.max(0, score || 0));
  const angle = (clamp / 100) * 180 - 90; // -90 to +90
  const rad   = (angle * Math.PI) / 180;
  const r = 44;
  const cx = 60, cy = 60;
  const nx = cx + r * Math.cos(rad);
  const ny = cy + r * Math.sin(rad);

  const color = clamp >= 70 ? '#22c55e' : clamp >= 45 ? '#eab308' : clamp >= 25 ? '#f97316' : '#ef4444';

  // Arc path from -90° to current angle
  const arcStart = { x: cx + r * Math.cos(-Math.PI / 2), y: cy + r * Math.sin(-Math.PI / 2) };
  const largeArc = clamp > 50 ? 1 : 0;

  return (
    <div className="flex flex-col items-center" style={{ width: size }}>
      <svg viewBox="0 0 120 80" width={size} height={size * 0.67}>
        {/* Background track */}
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="#1e293b" strokeWidth="8" strokeLinecap="round"
        />
        {/* Value arc */}
        {clamp > 0 && (
          <path
            d={`M ${arcStart.x} ${arcStart.y} A ${r} ${r} 0 ${largeArc} 1 ${nx} ${ny}`}
            fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
          />
        )}
        {/* Needle */}
        <line
          x1={cx} y1={cy}
          x2={cx + (r - 8) * Math.cos(rad)}
          y2={cy + (r - 8) * Math.sin(rad)}
          stroke={color} strokeWidth="2.5" strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r="4" fill={color} />
        {/* Score text */}
        <text x={cx} y={cy + 18} textAnchor="middle" fill={color}
              fontSize="16" fontWeight="700" fontFamily="Inter">{Math.round(clamp)}</text>
        <text x={cx} y={cy + 28} textAnchor="middle" fill="#64748b"
              fontSize="7" fontFamily="Inter">/ 100</text>
      </svg>
      <span className="text-xs text-slate-400 mt-1">{label}</span>
    </div>
  );
}
