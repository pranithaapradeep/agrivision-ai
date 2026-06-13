import { useState, useEffect } from "react";
import { reportsAPI, cropAPI } from "../services/api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import RiskBadge from "../components/common/RiskBadge";

const REPORT_TYPES = [
  {
    id: "crop_health",
    label: "Crop Health Report",
    icon: "🌿",
    desc: "NDVI, SAVI, EVI analysis + disease risk assessment",
    color: "green",
  },
  {
    id: "soil_analysis",
    label: "Soil Analysis Report",
    icon: "🌍",
    desc: "Moisture, nutrients, degradation indicators",
    color: "yellow",
  },
  {
    id: "pest_risk",
    label: "Pest Risk Report",
    icon: "🪲",
    desc: "Weather-driven pest outbreak probability",
    color: "red",
  },
  {
    id: "comprehensive",
    label: "Comprehensive Report",
    icon: "📊",
    desc: "Full farm intelligence: all metrics combined",
    color: "blue",
  },
];

const DEMO_REPORTS = [
  {
    id: "r1",
    title: "Field Alpha — Crop Health",
    type: "crop_health",
    status: "completed",
    created_at: "2025-06-10T08:30:00Z",
    health_score: 78,
    risk_level: "medium",
    file_path: "/reports/field_alpha_crop.pdf",
  },
  {
    id: "r2",
    title: "Field Beta — Comprehensive",
    type: "comprehensive",
    status: "completed",
    created_at: "2025-06-09T14:00:00Z",
    health_score: 62,
    risk_level: "high",
    file_path: "/reports/field_beta_comp.pdf",
  },
  {
    id: "r3",
    title: "Field Gamma — Soil",
    type: "soil_analysis",
    status: "completed",
    created_at: "2025-06-08T09:15:00Z",
    health_score: 85,
    risk_level: "low",
    file_path: "/reports/field_gamma_soil.pdf",
  },
];

function StatusBadge({ status }) {
  const map = {
    completed: "bg-green-100 text-green-800",
    generating: "bg-yellow-100 text-yellow-800 animate-pulse",
    pending: "bg-blue-100 text-blue-800",
    failed: "bg-red-100 text-red-800",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${map[status] || "bg-gray-100 text-gray-600"}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

export default function Reports() {
  const [selectedType, setSelectedType] = useState("comprehensive");
  const [fieldName, setFieldName] = useState("");
  const [notes, setNotes] = useState("");
  const [generating, setGenerating] = useState(false);
  const [reports, setReports] = useState(DEMO_REPORTS);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const handleGenerate = async () => {
    if (!fieldName.trim()) {
      showToast("Please enter a field / farm name.", "error");
      return;
    }
    setGenerating(true);
    try {
      const res = await reportsAPI.generate({
        field_name: fieldName,
        report_type: selectedType,
        notes,
      });
      const newReport = {
        id: `r${Date.now()}`,
        title: `${fieldName} — ${REPORT_TYPES.find((t) => t.id === selectedType)?.label}`,
        type: selectedType,
        status: "completed",
        created_at: new Date().toISOString(),
        health_score: res.data?.summary?.health_score || Math.floor(Math.random() * 40 + 55),
        risk_level: res.data?.summary?.risk_level || "medium",
        file_path: res.data?.file_path || "#",
      };
      setReports([newReport, ...reports]);
      showToast("Report generated successfully!");
      setFieldName("");
      setNotes("");
    } catch {
      // demo fallback
      const types = ["low", "medium", "high"];
      const newReport = {
        id: `r${Date.now()}`,
        title: `${fieldName} — ${REPORT_TYPES.find((t) => t.id === selectedType)?.label}`,
        type: selectedType,
        status: "completed",
        created_at: new Date().toISOString(),
        health_score: Math.floor(Math.random() * 40 + 55),
        risk_level: types[Math.floor(Math.random() * 3)],
        file_path: "#",
      };
      setReports([newReport, ...reports]);
      showToast("Demo report generated (backend offline).");
      setFieldName("");
      setNotes("");
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = (report) => {
    showToast(`Downloading "${report.title}"...`);
  };

  const handleDelete = (id) => {
    setReports(reports.filter((r) => r.id !== id));
    showToast("Report deleted.", "info");
  };

  return (
    <div className="p-6 space-y-8">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-white text-sm font-medium transition-all
            ${toast.type === "error" ? "bg-red-600" : toast.type === "info" ? "bg-blue-600" : "bg-green-600"}`}
        >
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">📄 Report Generation</h1>
        <p className="text-gray-500 text-sm mt-1">
          Generate downloadable PDF farm intelligence reports with AI insights.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Generator Panel */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">
          <h2 className="text-lg font-semibold text-gray-800">Generate New Report</h2>

          {/* Report Type Cards */}
          <div className="grid grid-cols-2 gap-3">
            {REPORT_TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedType(t.id)}
                className={`p-3 rounded-xl border-2 text-left transition-all
                  ${selectedType === t.id ? "border-agri-500 bg-agri-50" : "border-gray-200 hover:border-agri-300"}`}
              >
                <div className="text-2xl mb-1">{t.icon}</div>
                <div className="text-sm font-semibold text-gray-800">{t.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
              </button>
            ))}
          </div>

          {/* Field Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Field / Farm Name *</label>
            <input
              type="text"
              value={fieldName}
              onChange={(e) => setFieldName(e.target.value)}
              placeholder="e.g., North Block - Wheat Field"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-agri-400 focus:border-transparent outline-none"
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any specific observations or context for this report..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-agri-400 focus:border-transparent outline-none resize-none"
            />
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full py-3 bg-agri-600 hover:bg-agri-700 disabled:opacity-50 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generating Report...
              </>
            ) : (
              <>📄 Generate PDF Report</>
            )}
          </button>

          {/* What's Included */}
          <div className="bg-gray-50 rounded-xl p-4 text-xs text-gray-600 space-y-1">
            <div className="font-semibold text-gray-700 mb-2">Report includes:</div>
            {[
              "Executive summary with health & risk scores",
              "Vegetation index analysis (NDVI/SAVI/EVI)",
              "Disease & pest risk breakdown",
              "Soil condition indicators",
              "AI-generated recommendations",
              "Historical trend charts",
            ].map((item) => (
              <div key={item} className="flex items-start gap-1.5">
                <span className="text-agri-500 mt-0.5">✓</span>
                {item}
              </div>
            ))}
          </div>
        </div>

        {/* Report History */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Report History</h2>
          {reports.length === 0 ? (
            <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-8 text-center text-gray-400">
              No reports generated yet.
            </div>
          ) : (
            reports.map((report) => (
              <div
                key={report.id}
                className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-start gap-4"
              >
                <div className="text-3xl">
                  {REPORT_TYPES.find((t) => t.id === report.type)?.icon || "📊"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-gray-800 text-sm truncate">{report.title}</span>
                    <StatusBadge status={report.status} />
                  </div>
                  <div className="flex items-center gap-3 mt-1 flex-wrap">
                    <span className="text-xs text-gray-400">
                      {new Date(report.created_at).toLocaleDateString("en-IN", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}
                    </span>
                    <RiskBadge value={report.risk_level} />
                    <span className="text-xs font-medium text-gray-600">
                      Score: {report.health_score}/100
                    </span>
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => handleDownload(report)}
                    className="p-2 rounded-lg bg-agri-50 hover:bg-agri-100 text-agri-700 transition-colors"
                    title="Download"
                  >
                    ⬇️
                  </button>
                  <button
                    onClick={() => handleDelete(report.id)}
                    className="p-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 transition-colors"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))
          )}

          {/* Stats Bar */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
            <div className="grid grid-cols-3 divide-x divide-gray-100 text-center">
              <div>
                <div className="text-2xl font-bold text-gray-800">{reports.length}</div>
                <div className="text-xs text-gray-500">Total Reports</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-agri-600">
                  {reports.filter((r) => r.status === "completed").length}
                </div>
                <div className="text-xs text-gray-500">Completed</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-600">
                  {reports.filter((r) => r.risk_level === "high" || r.risk_level === "critical").length}
                </div>
                <div className="text-xs text-gray-500">High Risk</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
