import React, { useState } from 'react';
import RiskBadge from '../components/common/RiskBadge';
import ScoreGauge from '../components/common/ScoreGauge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { pestAPI } from '../services/api';

export default function PestPrediction() {
  const [form, setForm] = useState({
    crop_type: 'Rice', field_name: 'Field A',
    temperature: 28, humidity: 72, rainfall_7d: 18,
    consecutive_wet_days: 3, ndvi: 0.45,
  });
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);

  const handleChange = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleAssess = async () => {
    setLoading(true);
    try {
      const { data } = await pestAPI.assess(form);
      setResult(data);
    } catch {
      setResult(generateMockPestResult(form));
    } finally {
      setLoading(false);
    }
  };

  const radarData = result ? [
    { subject: 'Fungal',    value: result.fungal_risk    || 65 },
    { subject: 'Insect',    value: result.insect_risk    || 52 },
    { subject: 'Bacterial', value: result.bacterial_risk || 38 },
    { subject: 'Viral',     value: result.viral_risk     || 28 },
    { subject: 'Overall',   value: result.overall_risk_score || 55 },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Input panel */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 space-y-4">
          <h2 className="font-semibold text-slate-200">Pest Risk Assessment Parameters</h2>

          <div className="grid grid-cols-2 gap-3">
            {[
              { key: 'temperature',         label: '🌡️ Temperature (°C)', min: 10, max: 50 },
              { key: 'humidity',            label: '💧 Humidity (%)',      min: 0,  max: 100 },
              { key: 'rainfall_7d',         label: '🌧️ Rainfall 7d (mm)', min: 0,  max: 200 },
              { key: 'consecutive_wet_days',label: '☔ Wet Days',         min: 0,  max: 14 },
              { key: 'ndvi',                label: '🌿 NDVI Value',       min: 0,  max: 1, step: 0.01 },
            ].map(field => (
              <div key={field.key}>
                <label className="block text-xs text-slate-400 mb-1">{field.label}</label>
                <input
                  type="number" min={field.min} max={field.max} step={field.step || 1}
                  value={form[field.key]}
                  onChange={e => handleChange(field.key, parseFloat(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm text-slate-100 focus:outline-none focus:border-agri-600"
                />
              </div>
            ))}
            <div>
              <label className="block text-xs text-slate-400 mb-1">🌾 Crop Type</label>
              <select value={form.crop_type} onChange={e => handleChange('crop_type', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm text-slate-100">
                {['Rice','Wheat','Cotton','Maize','Soybean'].map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
          </div>

          {/* Weather sliders */}
          <div>
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>Temperature</span>
              <span className="text-agri-400">{form.temperature}°C</span>
            </div>
            <input type="range" min={10} max={50} value={form.temperature}
              onChange={e => handleChange('temperature', parseInt(e.target.value))}
              className="w-full accent-agri-500" />
          </div>
          <div>
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>Humidity</span>
              <span className="text-blue-400">{form.humidity}%</span>
            </div>
            <input type="range" min={0} max={100} value={form.humidity}
              onChange={e => handleChange('humidity', parseInt(e.target.value))}
              className="w-full accent-blue-500" />
          </div>

          <button onClick={handleAssess} disabled={loading}
            className="w-full bg-amber-700 hover:bg-amber-600 disabled:opacity-40
                       text-white rounded-lg py-2.5 text-sm font-medium transition-colors">
            {loading ? 'Assessing...' : '🐛 Assess Pest Risk'}
          </button>
        </div>

        {/* Result panel */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
          {loading && <LoadingSpinner text="Running pest risk model..." />}
          {result && !loading && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs text-slate-500 mb-1">Overall Risk</div>
                  <RiskBadge level={result.risk_level} size="lg" />
                </div>
                <ScoreGauge score={result.overall_risk_score} label="Risk Score" />
              </div>

              {/* Radar chart */}
              <ResponsiveContainer width="100%" height={180}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#1e293b" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar name="Risk" dataKey="value" stroke="#f97316" fill="#f97316" fillOpacity={0.25} />
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', fontSize: 11 }} />
                </RadarChart>
              </ResponsiveContainer>

              {/* Top threats */}
              {result.top_threats?.length > 0 && (
                <div>
                  <div className="text-xs text-slate-500 mb-2">Top Threats Identified</div>
                  {result.top_threats.map((threat, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-slate-800 text-sm">
                      <div>
                        <div className="text-slate-200">{threat.pest}</div>
                        <div className="text-xs text-slate-500 capitalize">{threat.category}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-orange-400 font-medium">{threat.risk_score?.toFixed(0)}%</div>
                        <RiskBadge level={threat.risk_level} />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Recommendations */}
              {result.recommendations?.map((rec, i) => (
                <div key={i} className="text-xs bg-slate-800 rounded-lg p-2.5 text-amber-300 border-l-2 border-amber-600">
                  {rec}
                </div>
              ))}
            </div>
          )}
          {!loading && !result && (
            <div className="h-full flex items-center justify-center text-slate-600 text-sm text-center">
              Configure parameters and click<br/>Assess Pest Risk
            </div>
          )}
        </div>
      </div>

      {/* Pest risk info cards */}
      <div className="grid md:grid-cols-4 gap-4">
        {[
          { pest: 'Fungal', icon: '🍄', driver: 'High humidity + warm temps', threshold: 'Risk > 60%' },
          { pest: 'Insect', icon: '🦟', driver: 'Temperature + crop vigor', threshold: 'Risk > 55%' },
          { pest: 'Bacterial', icon: '🦠', driver: 'Wet conditions + warmth', threshold: 'Risk > 50%' },
          { pest: 'Viral', icon: '🧬', driver: 'Insect vectors + heat', threshold: 'Risk > 45%' },
        ].map(info => (
          <div key={info.pest} className="bg-slate-900 rounded-xl border border-slate-800 p-4">
            <div className="text-2xl mb-1">{info.icon}</div>
            <div className="font-medium text-slate-200 text-sm">{info.pest}</div>
            <div className="text-xs text-slate-500 mt-1">{info.driver}</div>
            <div className="text-xs text-amber-600 mt-1">{info.threshold}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function generateMockPestResult(form) {
  const f = form.fungal_risk  || Math.min(100, form.humidity * 0.5 + form.temperature * 0.8 + form.rainfall_7d * 0.3);
  const i = form.insect_risk  || Math.min(100, form.temperature * 1.5 + (1 - form.ndvi) * 40);
  const overall = Math.min(100, f * 0.4 + i * 0.4 + 15);
  return {
    overall_risk_score: Math.round(overall),
    risk_level: overall > 70 ? 'high' : overall > 40 ? 'medium' : 'low',
    fungal_risk: Math.round(f),
    insect_risk: Math.round(i),
    bacterial_risk: Math.round(form.humidity * 0.4),
    viral_risk: Math.round(form.temperature * 0.5),
    top_threats: [
      { pest: 'Brown rust', category: 'fungal', risk_score: Math.round(f), risk_level: f > 60 ? 'high' : 'medium' },
      { pest: 'Aphids', category: 'insect', risk_score: Math.round(i), risk_level: i > 60 ? 'high' : 'medium' },
    ],
    recommendations: [
      overall > 60 ? 'Apply preventive fungicide within 48 hours.' : 'Continue regular monitoring.',
      'Check field edges for insect colonies every 2–3 days.',
    ],
  };
}
