import { useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";

const USERS = [
  { id: 1, name: "Ravi Kumar", email: "ravi@farmtech.in", role: "analyst", state: "Punjab", status: "active", analyses: 42 },
  { id: 2, name: "Priya Sharma", email: "priya@agri.gov.in", role: "admin", state: "Maharashtra", status: "active", analyses: 87 },
  { id: 3, name: "Arjun Singh", email: "arjun@krishi.in", role: "viewer", state: "Haryana", status: "inactive", analyses: 15 },
  { id: 4, name: "Meena Patel", email: "meena@farmco.in", role: "analyst", state: "Gujarat", status: "active", analyses: 63 },
  { id: 5, name: "Suresh Reddy", email: "suresh@agrotech.in", role: "viewer", state: "Telangana", status: "active", analyses: 29 },
];

const ACTIVITY_DATA = [
  { day: "Mon", analyses: 12, reports: 3 },
  { day: "Tue", analyses: 18, reports: 5 },
  { day: "Wed", analyses: 9, reports: 2 },
  { day: "Thu", analyses: 24, reports: 7 },
  { day: "Fri", analyses: 31, reports: 9 },
  { day: "Sat", analyses: 14, reports: 4 },
  { day: "Sun", analyses: 8, reports: 2 },
];

const MODEL_PERF = [
  { name: "CNN Crop Health", accuracy: 91.2, latency: "340ms", calls: 1284 },
  { name: "LSTM Forecast", accuracy: 87.6, latency: "620ms", calls: 438 },
  { name: "RF Pest Risk", accuracy: 89.4, latency: "85ms", calls: 2103 },
  { name: "VI Engine", accuracy: 99.1, latency: "120ms", calls: 3410 },
];

const USAGE_PIE = [
  { name: "Crop Health", value: 38, color: "#22c55e" },
  { name: "Pest Risk", value: 28, color: "#f59e0b" },
  { name: "Soil Analysis", value: 20, color: "#8b5cf6" },
  { name: "Forecasting", value: 14, color: "#3b82f6" },
];

const ROLE_COLORS = { admin: "bg-purple-100 text-purple-800", analyst: "bg-blue-100 text-blue-800", viewer: "bg-gray-100 text-gray-700" };

function StatCard({ icon, label, value, sub, color = "agri" }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl bg-${color}-50`}>{icon}</div>
      </div>
    </div>
  );
}

export default function Admin() {
  const [users, setUsers] = useState(USERS);
  const [tab, setTab] = useState("overview");
  const [search, setSearch] = useState("");

  const filtered = users.filter(
    (u) =>
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  );

  const toggleStatus = (id) => {
    setUsers(users.map((u) => u.id === id ? { ...u, status: u.status === "active" ? "inactive" : "active" } : u));
  };

  const TABS = ["overview", "users", "models", "system"];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">⚙️ Admin Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">System health, users, and AI model performance.</p>
        </div>
        <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded-full">Admin Access</span>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium capitalize transition-all
              ${tab === t ? "bg-white shadow text-gray-800" : "text-gray-500 hover:text-gray-700"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* OVERVIEW */}
      {tab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon="👥" label="Total Users" value={users.length} sub={`${users.filter(u=>u.status==="active").length} active`} />
            <StatCard icon="🔬" label="Total Analyses" value="7,234" sub="This month: 1,284" color="blue" />
            <StatCard icon="📄" label="Reports Generated" value="312" sub="PDF downloads: 189" color="yellow" />
            <StatCard icon="⚡" label="API Uptime" value="99.7%" sub="Last 30 days" color="green" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Weekly Activity */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-800 mb-4">Weekly Activity</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={ACTIVITY_DATA}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="analyses" fill="#22c55e" radius={[4,4,0,0]} name="Analyses" />
                  <Bar dataKey="reports" fill="#3b82f6" radius={[4,4,0,0]} name="Reports" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Feature Usage */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-800 mb-4">Feature Usage Distribution</h3>
              <div className="flex items-center gap-4">
                <ResponsiveContainer width={160} height={160}>
                  <PieChart>
                    <Pie data={USAGE_PIE} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value">
                      {USAGE_PIE.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => `${v}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-2 flex-1">
                  {USAGE_PIE.map((item) => (
                    <div key={item.name} className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: item.color }} />
                      <span className="text-gray-600 flex-1">{item.name}</span>
                      <span className="font-semibold text-gray-800">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* USERS */}
      {tab === "users" && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Search users..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-agri-400 outline-none w-64"
            />
            <button className="px-4 py-2 bg-agri-600 hover:bg-agri-700 text-white text-sm font-medium rounded-lg transition-colors">
              + Invite User
            </button>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {["Name", "Role", "State", "Analyses", "Status", "Actions"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-medium text-gray-800">{u.name}</div>
                        <div className="text-xs text-gray-400">{u.email}</div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${ROLE_COLORS[u.role]}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{u.state}</td>
                    <td className="px-4 py-3 font-medium text-gray-800">{u.analyses}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${u.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => toggleStatus(u.id)}
                        className="text-xs text-blue-600 hover:underline mr-3"
                      >
                        {u.status === "active" ? "Deactivate" : "Activate"}
                      </button>
                      <button className="text-xs text-red-500 hover:underline">Remove</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODELS */}
      {tab === "models" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {MODEL_PERF.map((m) => (
              <div key={m.name} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-800">{m.name}</h3>
                    <p className="text-xs text-gray-400 mt-0.5">{m.calls.toLocaleString()} total calls</p>
                  </div>
                  <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                    Live
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 rounded-xl p-3 text-center">
                    <div className="text-xl font-bold text-agri-600">{m.accuracy}%</div>
                    <div className="text-xs text-gray-500">Accuracy</div>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-3 text-center">
                    <div className="text-xl font-bold text-blue-600">{m.latency}</div>
                    <div className="text-xs text-gray-500">Avg Latency</div>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Accuracy</span>
                    <span>{m.accuracy}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-agri-500 rounded-full"
                      style={{ width: `${m.accuracy}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SYSTEM */}
      {tab === "system" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { label: "PostgreSQL", status: "healthy", detail: "5 active connections • v15.4" },
            { label: "Redis Cache", status: "healthy", detail: "Memory: 42MB / 512MB" },
            { label: "Celery Workers", status: "healthy", detail: "2 active workers • 0 queued" },
            { label: "ML Models", status: "healthy", detail: "4/4 loaded • heuristic fallbacks ready" },
            { label: "OpenWeatherMap API", status: "warning", detail: "Demo key — rate limited" },
            { label: "Sentinel-2 Imagery", status: "healthy", detail: "COPERNICUS access • 10m res" },
          ].map((svc) => (
            <div key={svc.label} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-center gap-4">
              <div className={`w-3 h-3 rounded-full flex-shrink-0 ${svc.status === "healthy" ? "bg-green-500" : "bg-yellow-400"}`} />
              <div>
                <div className="font-semibold text-gray-800 text-sm">{svc.label}</div>
                <div className="text-xs text-gray-400">{svc.detail}</div>
              </div>
              <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-semibold ${svc.status === "healthy" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                {svc.status}
              </span>
            </div>
          ))}

          {/* Environment Info */}
          <div className="md:col-span-2 bg-gray-900 text-green-400 rounded-2xl p-5 font-mono text-xs space-y-1">
            <div className="text-gray-500 mb-2"># System Environment</div>
            <div>PYTHON_VERSION=3.11.4</div>
            <div>FASTAPI_VERSION=0.111.0</div>
            <div>TENSORFLOW_VERSION=2.16.1</div>
            <div>PYTORCH_VERSION=2.3.0</div>
            <div>CELERY_VERSION=5.3.6</div>
            <div>POSTGRES_VERSION=15.4</div>
            <div>REDIS_VERSION=7.2</div>
            <div className="text-gray-500 mt-2"># Deployment</div>
            <div>ENVIRONMENT=production</div>
            <div>CONTAINER=docker</div>
            <div>REGION=ap-south-1 (Mumbai)</div>
          </div>
        </div>
      )}
    </div>
  );
}
