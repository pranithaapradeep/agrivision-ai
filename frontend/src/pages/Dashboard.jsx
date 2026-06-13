import React, { useState, useEffect } from 'react';
import ScoreGauge from '../components/common/ScoreGauge';
import RiskBadge from '../components/common/RiskBadge';
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const NDVI_TREND = [
  { day: 'Jun 1', ndvi: 0.52, evi: 0.43, savi: 0.47 },
  { day: 'Jun 4', ndvi: 0.49, evi: 0.40, savi: 0.44 },
  { day: 'Jun 7', ndvi: 0.51, evi: 0.42, savi: 0.46 },
  { day: 'Jun 10', ndvi: 0.44, evi: 0.36, savi: 0.40 },
  { day: 'Jun 13', ndvi: 0.42, evi: 0.34, savi: 0.38 },
  { day: 'Jun 16', ndvi: 0.45, evi: 0.37, savi: 0.41 },
  { day: 'Today', ndvi: 0.47, evi: 0.39, savi: 0.43 },
];

const STAT_CARDS = [
  { label: 'Active Fields',    value: '12',    sub: '↑ 2 this week', color: 'text-agri-400' },
  { label: 'Analyses Run',     value: '48',    sub: 'last 30 days',  color: 'text-blue-400' },
  { label: 'Alerts Triggered', value: '7',     sub: '3 unresolved',  color: 'text-amber-400' },
  { label: 'Avg Health Score', value: '73%',   sub: '↑ 5% vs last month', color: 'text-emerald-400' },
];

const FIELD_STATUS = [
  { name: 'Rabi Field A',  crop: 'Wheat',     health: 78, pest: 'low',    soil: 72 },
  { name: 'Kharif Zone 1', crop: 'Rice',      health: 52, pest: 'high',   soil: 58 },
  { name: 'Field B-North', crop: 'Soybean',   health: 65, pest: 'medium', soil: 67 },
  { name: 'Cotton Sector', crop: 'Cotton',    health: 41, pest: 'critical',soil: 44 },
  { name: 'Maize Plot 3',  crop: 'Maize',     health: 81, pest: 'low',    soil: 79 },
];

export default function Dashboard() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {STAT_CARDS.map(card => (
          <div key={card.label} className="bg-slate-900 rounded-xl border border-slate-800 p-4">
            <div className={`text-3xl font-bold ${card.color}`}>{card.value}</div>
            <div className="text-sm font-medium text-slate-300 mt-1">{card.label}</div>
            <div className="text-xs text-slate-500 mt-0.5">{card.sub}</div>
          </div>
        ))}
      </div>

      {/* Gauges row */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">System Health Overview</h2>
        <div className="flex flex-wrap justify-around gap-6">
          <ScoreGauge score={74} label="Crop Health"  />
          <ScoreGauge score={62} label="Soil Health"  />
          <ScoreGauge score={38} label="Pest Risk"    />
          <ScoreGauge score={71} label="Overall Score"/>
        </div>
      </div>

      {/* NDVI trend chart */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-sm font-semibold text-slate-300">Vegetation Index Trend (7 days)</h2>
          <span className="text-xs text-slate-500">Aggregated across all fields</span>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={NDVI_TREND}>
            <defs>
              <linearGradient id="ndviGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0}   />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} />
            <YAxis domain={[0, 1]} tick={{ fill: '#64748b', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: '#64748b' }} />
            <Area type="monotone" dataKey="ndvi" stroke="#22c55e" fill="url(#ndviGrad)" strokeWidth={2} name="NDVI" />
            <Line type="monotone" dataKey="evi"  stroke="#3b82f6" strokeWidth={1.5} dot={false} name="EVI"  />
            <Line type="monotone" dataKey="savi" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="SAVI" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Field status table */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800">
          <h2 className="text-sm font-semibold text-slate-300">Field Status Summary</h2>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-slate-500 bg-slate-950">
              <th className="px-6 py-3 text-left">Field</th>
              <th className="px-4 py-3 text-left">Crop</th>
              <th className="px-4 py-3 text-center">Health</th>
              <th className="px-4 py-3 text-center">Pest Risk</th>
              <th className="px-4 py-3 text-center">Soil</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {FIELD_STATUS.map(field => (
              <tr key={field.name} className="hover:bg-slate-800/50 transition-colors">
                <td className="px-6 py-3 font-medium text-slate-200">{field.name}</td>
                <td className="px-4 py-3 text-slate-400">{field.crop}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`font-semibold ${
                    field.health >= 70 ? 'text-emerald-400' :
                    field.health >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                    {field.health}%
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <RiskBadge level={field.pest} />
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`font-semibold ${
                    field.soil >= 65 ? 'text-emerald-400' :
                    field.soil >= 45 ? 'text-amber-400' : 'text-red-400'}`}>
                    {field.soil}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
