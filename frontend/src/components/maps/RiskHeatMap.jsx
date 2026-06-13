import { useEffect, useRef } from "react";

const RISK_COLORS = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#ef4444",
  critical: "#7c3aed",
};

/**
 * RiskHeatMap — Leaflet map showing risk point overlays.
 * Props:
 *   points: Array<{ lat, lng, risk_level, risk_score, label? }>
 *   center: [lat, lng]  default: [20.5937, 78.9629] (India)
 *   zoom: number        default: 5
 *   height: string      default: "400px"
 *   title: string
 */
export default function RiskHeatMap({
  points = [],
  center = [20.5937, 78.9629],
  zoom = 5,
  height = "400px",
  title = "Risk Heatmap",
}) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    // Dynamically import Leaflet to avoid SSR issues
    let L;
    let map;

    const init = async () => {
      try {
        L = await import("leaflet");
        await import("leaflet/dist/leaflet.css");

        if (mapInstanceRef.current) return; // already initialized

        map = L.map(mapRef.current, {
          center,
          zoom,
          zoomControl: true,
          scrollWheelZoom: false,
        });

        mapInstanceRef.current = map;

        // OpenStreetMap tiles
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
          maxZoom: 18,
        }).addTo(map);

        renderPoints(L, map);
      } catch (err) {
        console.warn("Leaflet init error:", err);
      }
    };

    const renderPoints = (L, map) => {
      // Clear existing markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      points.forEach((pt) => {
        const color = RISK_COLORS[pt.risk_level] || "#6b7280";
        const size = pt.risk_level === "critical" ? 14 : pt.risk_level === "high" ? 12 : 10;

        const icon = L.divIcon({
          className: "",
          html: `<div style="
            width:${size}px;height:${size}px;
            background:${color};
            border:2px solid white;
            border-radius:50%;
            box-shadow:0 0 ${size}px ${color}80;
            ${pt.risk_level === "critical" ? "animation:pulse 1.5s infinite;" : ""}
          "></div>`,
          iconSize: [size, size],
          iconAnchor: [size / 2, size / 2],
        });

        const marker = L.marker([pt.lat, pt.lng], { icon })
          .bindPopup(`
            <div style="font-family:sans-serif;font-size:13px;min-width:140px">
              <strong>${pt.label || "Field"}</strong><br/>
              Risk: <span style="color:${color};font-weight:600">${pt.risk_level?.toUpperCase()}</span><br/>
              Score: ${pt.risk_score?.toFixed(2) || "—"}
            </div>
          `)
          .addTo(map);

        markersRef.current.push(marker);
      });
    };

    init();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Re-render points when data changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    import("leaflet").then((L) => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      points.forEach((pt) => {
        const color = RISK_COLORS[pt.risk_level] || "#6b7280";
        const size = pt.risk_level === "critical" ? 14 : pt.risk_level === "high" ? 12 : 10;

        const icon = L.divIcon({
          className: "",
          html: `<div style="width:${size}px;height:${size}px;background:${color};border:2px solid white;border-radius:50%;box-shadow:0 0 ${size}px ${color}80;"></div>`,
          iconSize: [size, size],
          iconAnchor: [size / 2, size / 2],
        });

        const marker = L.marker([pt.lat, pt.lng], { icon })
          .bindPopup(`<div style="font-family:sans-serif;font-size:13px;min-width:140px"><strong>${pt.label || "Field"}</strong><br/>Risk: <span style="color:${color};font-weight:600">${pt.risk_level?.toUpperCase()}</span><br/>Score: ${pt.risk_score?.toFixed(2) || "—"}</div>`)
          .addTo(map);

        markersRef.current.push(marker);
      });
    });
  }, [points]);

  // Legend
  const legend = Object.entries(RISK_COLORS).map(([level, color]) => ({
    level,
    color,
    count: points.filter((p) => p.risk_level === level).length,
  }));

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <h3 className="font-semibold text-gray-800 text-sm">{title}</h3>
        <span className="text-xs text-gray-400">{points.length} locations</span>
      </div>

      {/* Map */}
      <div ref={mapRef} style={{ height, width: "100%" }} />

      {/* Legend */}
      <div className="px-4 py-3 border-t border-gray-100 flex items-center gap-4 flex-wrap">
        <span className="text-xs font-medium text-gray-500">Legend:</span>
        {legend.map(({ level, color, count }) => (
          <div key={level} className="flex items-center gap-1.5 text-xs text-gray-600">
            <div className="w-3 h-3 rounded-full border border-white shadow-sm" style={{ background: color }} />
            <span className="capitalize">{level}</span>
            <span className="text-gray-400">({count})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
