import React, { useState, useRef } from 'react';
import ScoreGauge from '../components/common/ScoreGauge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip, PolarAngleAxis } from 'recharts';
import { soilAPI } from '../services/api';

const SOIL_METRICS = [
  { key: 'moisture_level',    label: 'Moisture (%)',    unit: '%',  good: '>35', fill: '#3b82f6' },
  { key: 'organic_matter',    label: 'Organic Matter',  unit: '%',  good: '>2%', fill: '#22c55e' },
  { key: 'nitrogen_index',    label: 'Nitrogen Index',  unit: '/100',good:'>40', fill: '#a78bfa' },
  { key: 'phosphorus_index',  label: 'Phosphorus',      unit: '/100',good:'>35', fill: '#f59e0b' },
  { key: 'potassium_index',   label: 'Potassium',       unit: '/100',good:'>40', fill: '#ef4444' },
  { key: 'ph_estimate',       label: 'pH Estimate',     unit: '',   good:'6–7',  fill: '#14b8a6' },
];

export default function SoilAnalysis() {
  const [file,      setFile]      = useState(null);
  const [preview,   setPreview]   = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState(null);
  const [fieldName, setFieldName] = useState('Rabi Field B');
  const inputRef = useRef();

  const handleFile = (e) => {
    const f = e.target.files[0]; if (!f) return;
    setFile(f); setPreview(URL.createObjectURL(f)); setResult(null);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      if (file) {
        const form = new FormData();
        form.append('file', file);
        form.append('field_name', fieldName);
        const { data } = await soilAPI.analyze(form);
        setResult(data);
      } else {
        setTimeout(() => { setResult(generateMockSoil(fieldName)); setLoading(false); }, 1200);
        return;
      }
    } catch {
      setResult(generateMockSoil(fieldName));
    }
    setLoading(false);
  };

  const gradeColor = {
    excellent: 'text-emerald-400', good: 'text-agri-400',
    fair: 'text-amber-400', poor: 'text-orange-400', critical: 'text-red-400'
  };

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Upload */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 space-y-4">
          <h2 className="font-semibold text-slate-200">Soil Condition Analysis</h2>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Field Name</label>
            <input value={fieldName} onChange={e => setFieldName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-agri-600" />
          </div>

          <div onClick={() => inputRef.current.click()}
            className="border-2 border-dashed border-slate-700 hover:border-agri-600 rounded-xl p-6 cursor-pointer text-center transition-colors">
            {preview
              ? <img src={preview} alt="preview" className="w-full h-32 object-cover rounded-lg" />
              : <div className="text-slate-500"><div className="text-3xl mb-2">🌍</div><div className="text-sm">Upload satellite image for soil analysis</div></div>
            }
            <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={handleFile} />
          </div>

          <button onClick={handleAnalyze} disabled={loading}
            className="w-full bg-amber-800 hover:bg-amber-700 text-white rounded-lg py-2.5 text-sm font-medium transition-colors">
            {loading ? 'Analyzing...' : '🪱 Analyze Soil Condition'}
          </button>

          {/* Info */}
          <div className="bg-slate-800/50 rounded-lg p-3 text-xs text-slate-500">
            <div className="font-medium text-slate-400 mb-1">Analysis method</div>
            Estimates soil properties using NIR/SWIR band ratios and spectral reflectance analysis from satellite imagery.
          </div>
        </div>

        {/* Results */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
          {loading && <LoadingSpinner text="Estimating soil properties..." />}
          {result && !loading && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs text-slate-500 mb-1">Soil Health Grade</div>
                  <span className={`text-2xl font-bold capitalize ${gradeColor[result.health_grade] || 'text-agri-400'}`}>
                    {result.health_grade}
                  </span>
                  <div className="text-xs text-slate-500 mt-0.5 capitalize">
                    Moisture: {result.moisture_status}
                  </div>
                </div>
                <ScoreGauge score={result.health_score} label="Soil Health" />
              </div>

              {/* Metrics grid */}
              <div className="grid grid-cols-3 gap-2">
                {SOIL_METRICS.map(m => (
                  <div key={m.key} className="bg-slate-800 rounded-lg p-2.5 text-center">
                    <div className="text-xs text-slate-500">{m.label}</div>
                    <div className="font-semibold mt-0.5" style={{ color: m.fill }}>
                      {m.key === 'organic_matter'
                        ? `${result[m.key]?.toFixed(1)}%`
                        : m.key === 'ph_estimate'
                        ? result[m.key]?.toFixed(1)
                        : Math.round(result[m.key] || 0)
                      }
                      {m.unit && m.key !== 'organic_matter' && m.key !== 'ph_estimate' && <span className="text-xs ml-0.5">{m.unit}</span>}
                    </div>
                    <div className="text-xs text-slate-600">Good: {m.good}</div>
                  </div>
                ))}
              </div>

              {/* Recommendations */}
              {result.recommendations?.map((rec, i) => (
                <div key={i} className="text-xs bg-amber-950/30 border-l-2 border-amber-600 text-amber-300 p-2.5 rounded-r-lg">
                  {rec}
                </div>
              ))}
            </div>
          )}
          {!loading && !result && (
            <div className="h-full flex items-center justify-center text-slate-600 text-sm text-center">
              Upload an image or click analyze<br/>to estimate soil conditions
            </div>
          )}
        </div>
      </div>

      {/* Soil interpretation guide */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Soil Health Grade Reference</h2>
        <div className="grid grid-cols-5 gap-3 text-center text-xs">
          {[
            { grade: 'Excellent', range: '80–100', color: 'bg-emerald-900/50 border-emerald-700 text-emerald-400' },
            { grade: 'Good',     range: '65–79',  color: 'bg-agri-900/50 border-agri-700 text-agri-400' },
            { grade: 'Fair',     range: '45–64',  color: 'bg-amber-900/50 border-amber-700 text-amber-400' },
            { grade: 'Poor',     range: '25–44',  color: 'bg-orange-900/50 border-orange-700 text-orange-400' },
            { grade: 'Critical', range: '0–24',   color: 'bg-red-900/50 border-red-700 text-red-400' },
          ].map(g => (
            <div key={g.grade} className={`border rounded-lg p-3 ${g.color}`}>
              <div className="font-semibold">{g.grade}</div>
              <div className="opacity-70">{g.range}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function generateMockSoil(fieldName) {
  return {
    field_name: fieldName,
    moisture_level: 38 + Math.random() * 20,
    moisture_status: 'optimal',
    organic_matter: 1.5 + Math.random() * 2,
    nitrogen_index: 45 + Math.random() * 20,
    phosphorus_index: 38 + Math.random() * 15,
    potassium_index: 42 + Math.random() * 18,
    ph_estimate: 6.2 + Math.random() * 0.8,
    salinity_index: 15 + Math.random() * 10,
    erosion_risk: 25 + Math.random() * 20,
    health_score: 62 + Math.random() * 15,
    health_grade: 'fair',
    recommendations: [
      'Organic matter below 2%. Apply compost at 3–4 tonnes/hectare.',
      'Maintain current irrigation schedule — moisture is optimal.',
    ],
  };
}
