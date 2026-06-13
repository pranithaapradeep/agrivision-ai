import React, { useState, useEffect } from 'react';

const DEMO_ALERTS = [
  { id: 1, type: 'pest_risk',        severity: 'danger',  title: 'High Pest Risk Detected',     message: 'Field A — fungal outbreak probability 78%', time: '2m ago' },
  { id: 2, type: 'crop_stress',      severity: 'warning', title: 'Crop Stress Increasing',       message: 'Sector 3 NDVI dropped 12% in 7 days',       time: '15m ago' },
  { id: 3, type: 'disease_outbreak', severity: 'warning', title: 'Possible Disease Outbreak',    message: 'Rice blast pattern detected in Zone B',      time: '1h ago' },
];

const SCOLOR = {
  danger:   'border-l-red-500 bg-red-950/40',
  warning:  'border-l-amber-500 bg-amber-950/30',
  critical: 'border-l-red-500 bg-red-950/60',
  info:     'border-l-blue-500 bg-blue-950/30',
};

export default function AlertPanel() {
  const [visible, setVisible] = useState(true);
  const [alerts, setAlerts] = useState(DEMO_ALERTS);

  const dismiss = (id) => setAlerts(a => a.filter(x => x.id !== id));

  if (!visible || alerts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 w-80 space-y-2 z-50">
      {alerts.map(alert => (
        <div key={alert.id}
             className={`alert-slide border-l-4 rounded-r-lg p-3 text-sm
                         ${SCOLOR[alert.severity] || SCOLOR.info}`}>
          <div className="flex justify-between items-start">
            <span className="font-medium text-slate-100">{alert.title}</span>
            <button onClick={() => dismiss(alert.id)}
                    className="text-slate-500 hover:text-slate-300 ml-2 text-xs">✕</button>
          </div>
          <p className="text-slate-400 text-xs mt-0.5">{alert.message}</p>
          <span className="text-slate-600 text-xs">{alert.time}</span>
        </div>
      ))}
    </div>
  );
}
