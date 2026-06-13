import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/common/LoadingSpinner';
import {
  ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { forecastAPI } from '../services/api';

const TARGETS = [
  { key: 'stress_score', label: 'Crop Stress',   color: '#f97316', icon: '🌡️' },
  { key: 'disease_prob', label: 'Disease Risk',   color: '#ef4444', icon: '🦠' },
  { key: 'pest_prob',    label: 'Pest Outbreak',  color: '#eab308', icon: '🐛' },
];

export default function Forecasting() {
  const [forecasts, setForecasts] = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [active,    setActive]    = useState('stress_score');

  const loadDemo = async () => {
    setLoading(true);
    try {
      const { data } = await forecastAPI.demo();
      setForecasts(data);
    } catch {
      setForecasts(generateMockForecasts());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDemo(); }, []);

  const buildChartData = (target) => {
    if (!forecasts?.[target]) return [];
    const f = forecasts[target];
    return f.forecast_dates.map((date, i) => ({
      date: date.slice(5),  // MM-DD
      forecast: f.forecast_values[i],
      upper: f.ci_upper ? f.ci_upper[i] : f.forecast_values[i] + 8,
      lower: f.ci_lower ? f.ci_lower[i] : f.forecast_values[i] - 8,
    }));
  };

  const activeForecast = forecasts?.[active];
  const chartData      = buildChartData(active);
  const activeConfig   = TARGETS.find(t => t.key === active);

  const trendColor = {
    improving:    'text-emerald-400',
    stable:       'text-blue-400',
    deteriorating:'text-red-400',
  };

  return (
    <div className="space-y-6">
      {/* Header cards */}
      <div className="grid md:grid-cols-3 gap-4">
        {TARGETS.map(target => {
          const f = forecasts?.[target.key];
          return (
            <button
              key={target.key}
              onClick={() => setActive(target.key)}
              className={`bg-slate-900 rounded-xl border p-4 text-left transition-all
                ${active === target.key
                  ? 'border-agri-600 bg-agri-950/20'
                  : 'border-slate-800 hover:border-slate-700'}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span>{target.icon}</span>
                <span className="text-sm font-medium text-slate-300">{target.label}</span>
              </div>
              {f ? (
                <div>
                  <div className="text-2xl font-bold" style={{ color: target.color }}>
                    {f.current_value?.toFixed(0)}%
                  </div>
                  <div className={`text-xs mt-1 capitalize ${trendColor[f.trend] || 'text-slate-400'}`}>
                    {f.trend === 'deteriorating' ? '↑ Worsening' : f.trend === 'improving' ? '↓ Improving' : '→ Stable'}
                  </div>
                  {f.forecast_values?.length && (
                    <div className="text-xs text-slate-500 mt-0.5">
                      14d: {f.forecast_values[f.forecast_values.length - 1]?.toFixed(0)}%
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-slate-600 text-sm">Loading...</div>
              )}
            </button>
          );
        })}
      </div>

      {/* Main forecast chart */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-semibold text-slate-200">
            {activeConfig?.icon} {activeConfig?.label} — 14-Day LSTM Forecast
          </h2>
          <div className={`text-sm font-medium capitalize ${trendColor[activeForecast?.trend] || 'text-slate-400'}`}>
            Trend: {activeForecast?.trend || '—'}
          </div>
        </div>

        {loading && <LoadingSpinner text="Running LSTM model..." />}

        {!loading && chartData.length > 0 && (
          <ResponsiveContainer width="100%" height={280}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} unit="%" />
              <Tooltip
                contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, fontSize: 11 }}
                formatter={(v, name) => [`${typeof v === 'number' ? v.toFixed(1) : v}%`, name]}
              />
              <Legend wrapperStyle={{ fontSize: 11, color: '#64748b' }} />

              {/* Confidence interval band */}
              <Area
                dataKey="upper" stroke="none"
                fill={activeConfig?.color} fillOpacity={0.08} name="CI Upper"
              />
              <Area
                dataKey="lower" stroke="none"
                fill={activeConfig?.color} fillOpacity={0.08} name="CI Lower"
              />

              {/* Alert threshold */}
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 4"
                label={{ value: 'Alert threshold', fill: '#ef4444', fontSize: 10 }} />

              {/* Forecast line */}
              <Line
                type="monotone" dataKey="forecast"
                stroke={activeConfig?.color} strokeWidth={2.5}
                dot={{ fill: activeConfig?.color, r: 3 }}
                name="Forecast"
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}

        {activeForecast?.alert_triggered && (
          <div className="mt-4 p-3 bg-red-950/40 border border-red-700 rounded-lg text-sm text-red-300">
            ⚠️ {activeForecast.alert_message}
          </div>
        )}
      </div>

      {/* Model info */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">LSTM Model Architecture</h2>
        <div className="grid md:grid-cols-4 gap-4 text-xs">
          {[
            { label: 'Input Features', value: '8 time-series features', sub: 'NDVI, weather, soil' },
            { label: 'Lookback Window', value: '30 days', sub: 'Minimum history needed' },
            { label: 'Architecture', value: 'Bi-LSTM + Attention', sub: '128 → 64 hidden units' },
            { label: 'Forecast Horizon', value: '14 days', sub: '3 targets simultaneously' },
          ].map(item => (
            <div key={item.label} className="bg-slate-800 rounded-lg p-3">
              <div className="text-slate-500">{item.label}</div>
              <div className="font-semibold text-agri-400 mt-1">{item.value}</div>
              <div className="text-slate-600 mt-0.5">{item.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function generateMockForecasts() {
  const gen = (base, slope) => {
    const vals = [], dates = [];
    for (let i = 1; i <= 14; i++) {
      const today = new Date();
      today.setDate(today.getDate() + i);
      dates.push(today.toISOString().slice(0, 10));
      vals.push(Math.round(Math.min(100, Math.max(0, base + slope * i + (Math.random() - 0.5) * 6))));
    }
    return { current_value: base, forecast_values: vals, forecast_dates: dates,
             ci_upper: vals.map(v => Math.min(100, v + 8)),
             ci_lower: vals.map(v => Math.max(0, v - 8)),
             trend: slope > 1.5 ? 'deteriorating' : slope < -1 ? 'improving' : 'stable',
             alert_triggered: vals[vals.length - 1] > 70, alert_message: 'High risk in 14 days' };
  };
  return {
    stress_score: gen(42, 1.8),
    disease_prob: gen(35, 1.2),
    pest_prob:    gen(55, 0.5),
  };
}
