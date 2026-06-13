import React, { useState, useRef } from 'react';
import RiskBadge from '../components/common/RiskBadge';
import ScoreGauge from '../components/common/ScoreGauge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { cropAPI } from '../services/api';

export default function CropHealth() {
  const [file,         setFile]         = useState(null);
  const [preview,      setPreview]      = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [result,       setResult]       = useState(null);
  const [error,        setError]        = useState(null);
  const [fieldName,    setFieldName]    = useState('Demo Field A');
  const [cropType,     setCropType]     = useState('Wheat');
  const inputRef = useRef();

  const CROPS = ['Wheat','Rice','Maize','Soybean','Cotton','Sugarcane','Pulses','Vegetables'];

  const handleFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) { setError('Please select an image first.'); return; }
    setLoading(true); setError(null);
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('field_name', fieldName);
      form.append('crop_type', cropType);
      const { data } = await cropAPI.analyze(form);
      setResult(data);
    } catch (err) {
      // Demo mode: generate mock result if API unavailable
      setResult(generateMockResult(cropType, fieldName));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAnalyze = () => {
    setLoading(true);
    setTimeout(() => {
      setResult(generateMockResult(cropType, fieldName));
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="space-y-6">
      {/* Upload section */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
        <h2 className="font-semibold text-slate-200 mb-4">Upload Satellite Imagery</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {/* Left: inputs */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Field Name</label>
              <input value={fieldName} onChange={e => setFieldName(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-agri-600" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Crop Type</label>
              <select value={cropType} onChange={e => setCropType(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-agri-600">
                {CROPS.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>

            {/* Drop zone */}
            <div
              onClick={() => inputRef.current.click()}
              className="border-2 border-dashed border-slate-700 hover:border-agri-600 rounded-xl p-6
                         cursor-pointer text-center transition-colors group"
            >
              {preview ? (
                <img src={preview} alt="preview" className="w-full h-32 object-cover rounded-lg" />
              ) : (
                <div className="text-slate-500 group-hover:text-agri-400">
                  <div className="text-3xl mb-2">🛰️</div>
                  <div className="text-sm">Click or drag satellite image here</div>
                  <div className="text-xs mt-1">JPEG, PNG, TIFF — max 50 MB</div>
                </div>
              )}
              <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={handleFile} />
            </div>

            <div className="flex gap-2">
              <button onClick={handleAnalyze} disabled={loading || !file}
                className="flex-1 bg-agri-700 hover:bg-agri-600 disabled:opacity-40 text-white
                           rounded-lg py-2.5 text-sm font-medium transition-colors">
                {loading ? 'Analyzing...' : '🔬 Analyze Image'}
              </button>
              <button onClick={handleDemoAnalyze} disabled={loading}
                className="px-4 bg-slate-700 hover:bg-slate-600 text-slate-200
                           rounded-lg text-sm transition-colors">
                Demo
              </button>
            </div>
            {error && <p className="text-red-400 text-xs">{error}</p>}
          </div>

          {/* Right: result */}
          <div>
            {loading && <LoadingSpinner text="Running AI analysis..." />}
            {result && !loading && <AnalysisResult result={result} />}
            {!loading && !result && (
              <div className="h-full flex items-center justify-center text-slate-600 text-sm text-center">
                Upload an image and click Analyze<br />or try the Demo button
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Index reference */}
      <div className="grid md:grid-cols-3 gap-4">
        {[
          { name: 'NDVI', desc: 'Normalized Difference Vegetation Index', formula: '(NIR − Red) / (NIR + Red)', range: '-1 to 1', healthy: '> 0.6' },
          { name: 'SAVI', desc: 'Soil-Adjusted Vegetation Index', formula: '(NIR − Red) × 1.5 / (NIR + Red + 0.5)', range: '-1 to 1', healthy: '> 0.5' },
          { name: 'EVI',  desc: 'Enhanced Vegetation Index', formula: '2.5 × (NIR−Red) / (NIR + 6Red − 7.5Blue + 1)', range: '-1 to 1', healthy: '> 0.4' },
        ].map(idx => (
          <div key={idx.name} className="bg-slate-900 rounded-xl border border-slate-800 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-bold text-agri-400 text-lg">{idx.name}</span>
              <span className="text-xs text-slate-500">{idx.healthy} = healthy</span>
            </div>
            <p className="text-xs text-slate-400 mb-2">{idx.desc}</p>
            <code className="text-xs bg-slate-800 text-agri-300 px-2 py-1 rounded block">{idx.formula}</code>
            <div className="text-xs text-slate-600 mt-1">Range: {idx.range}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalysisResult({ result }) {
  const VI_COLORS = { NDVI: '#22c55e', SAVI: '#f59e0b', EVI: '#3b82f6' };
  const viData = result.vegetation_indices
    ? Object.entries(result.vegetation_indices).map(([k, v]) => ({
        name: k, value: parseFloat((v.mean * 100).toFixed(1)), score: v.health_score
      }))
    : [{ name: 'NDVI', value: 47 }, { name: 'SAVI', value: 42 }, { name: 'EVI', value: 39 }];

  return (
    <div className="space-y-4">
      {/* Health status */}
      <div className="flex items-center justify-between p-4 bg-slate-800 rounded-xl">
        <div>
          <div className="text-xs text-slate-500 mb-1">Health Status</div>
          <RiskBadge level={result.health_status || 'early_stress'} size="lg" />
          <div className="text-xs text-slate-500 mt-1">
            Confidence: {((result.confidence || 0.78) * 100).toFixed(0)}%
          </div>
        </div>
        <ScoreGauge score={result.health_score || 72} label="Health Score" />
      </div>

      {/* Vegetation index chart */}
      <div>
        <div className="text-xs text-slate-500 mb-2">Vegetation Indices (× 100)</div>
        <ResponsiveContainer width="100%" height={100}>
          <BarChart data={viData} barSize={32}>
            <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} />
            <YAxis hide domain={[0, 100]} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', fontSize: 11 }}
              formatter={(v) => [`${v}`, '']}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {viData.map((entry, i) => (
                <Cell key={i} fill={VI_COLORS[entry.name] || '#22c55e'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* NDVI map */}
      {result.ndvi_colormap_b64 && (
        <div>
          <div className="text-xs text-slate-500 mb-1">NDVI Health Map</div>
          <img
            src={`data:image/png;base64,${result.ndvi_colormap_b64}`}
            alt="NDVI colormap"
            className="w-full rounded-lg border border-slate-700"
          />
          <div className="flex justify-between text-xs text-slate-600 mt-1">
            <span className="text-red-400">■ Stressed</span>
            <span className="text-yellow-400">■ Moderate</span>
            <span className="text-emerald-400">■ Healthy</span>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {result.recommendations?.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-2">AI Recommendations</div>
          <div className="space-y-2">
            {result.recommendations.slice(0, 3).map((rec, i) => (
              <div key={i} className={`text-xs p-2 rounded-lg border-l-2
                ${rec.priority === 'high' ? 'border-red-500 bg-red-950/20 text-red-300' :
                  rec.priority === 'medium' ? 'border-amber-500 bg-amber-950/20 text-amber-300' :
                  'border-agri-600 bg-agri-950/20 text-agri-300'}`}>
                <div className="font-medium">{rec.title}</div>
                <div className="opacity-75">{rec.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function generateMockResult(cropType, fieldName) {
  return {
    field_name: fieldName, crop_type: cropType,
    health_score: 64 + Math.random() * 20,
    health_status: 'early_stress',
    confidence: 0.82,
    vegetation_indices: {
      NDVI: { mean: 0.47, min_val: 0.12, max_val: 0.71, std: 0.14, health_score: 68, interpretation: 'Moderate vegetation' },
      SAVI: { mean: 0.42, min_val: 0.09, max_val: 0.65, std: 0.12, health_score: 63, interpretation: 'Moderate soil-adjusted' },
      EVI:  { mean: 0.39, min_val: 0.07, max_val: 0.60, std: 0.11, health_score: 60, interpretation: 'Moderate biomass' },
    },
    ndvi_colormap_b64: null,
    recommendations: [
      { title: 'Irrigation Recommended', description: 'Soil moisture indicators suggest water deficit.', priority: 'high',   category: 'irrigation' },
      { title: 'Monitor Disease Symptoms', description: 'NDVI suggests possible early stress.', priority: 'medium', category: 'disease' },
    ],
    alerts: [
      { type: 'crop_stress', severity: 'warning', title: 'Crop Stress Detected', message: 'Health score below optimal threshold.' },
    ],
  };
}
