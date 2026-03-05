// src/pages/MapPage.tsx
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, useMap, GeoJSON, LayersControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import './MapPage.css';
import API_BASE from '../config';

// 🗑️ Trash-bin emoji marker
const TrashIcon = L.divIcon({
  className: '',
  html: `<div style="font-size:28px;line-height:1;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.35));transform:translateY(-4px)">🗑️</div>`,
  iconSize:   [32, 32],
  iconAnchor: [16, 28],
  popupAnchor:[0, -30],
});

interface Report {
  id: string;
  image_path: string;
  lat: number | null;
  lng: number | null;
  address: string;
  count: number;
  created_at: string;
  description?: string;
}

// Component to handle smooth map movements
function MapController({ center, enabled }: { center: [number, number]; enabled: boolean }) {
  const map = useMap();
  
  useEffect(() => {
    if (enabled && center) {
      map.flyTo(center, 14, {
        duration: 1.5,
        easeLinearity: 0.25
      });
    }
  }, [center, enabled, map]);

  return null;
}

// Component to add heatmap layer
function HeatmapLayer({ reports }: { reports: Report[] }) {
  const map = useMap();
  const heatLayerRef = React.useRef<any>(null);

  useEffect(() => {
    // Always clear the previous layer first
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }
    if (reports.length === 0) return;

    // Create new heat layer
    const points = reports
      .filter(r => r.lat !== null && r.lng !== null)
      .map(r => [r.lat!, r.lng!, 0.8] as [number, number, number]);
    heatLayerRef.current = (L as any).heatLayer(points, {
      radius: 30,
      blur: 20,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.0: '#00ff00',
        0.5: '#ffff00',
        0.7: '#ff9900',
        1.0: '#ff0000'
      }
    }).addTo(map);

    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
      }
    };
  }, [reports, map]);

  return null;
}

// Component: emoji trash markers with automatic zoom-based clustering
function ClusteredReportMarkers({ reports }: { reports: Report[] }) {
  const map = useMap();
  const clusterRef = React.useRef<any>(null);

  useEffect(() => {
    const L_mc = L as any;
    if (typeof L_mc.markerClusterGroup !== 'function') return;

    // Tear down previous cluster group on re-render
    if (clusterRef.current) {
      map.removeLayer(clusterRef.current);
    }

    const mcg = L_mc.markerClusterGroup({
      showCoverageOnHover: false,
      maxClusterRadius: 60,
      // Cluster icon: emoji + red count badge
      iconCreateFunction: (cluster: any) => {
        const n = cluster.getChildCount();
        return L.divIcon({
          className: '',
          html: `<div style="position:relative;width:44px;height:44px;display:flex;align-items:center;justify-content:center">
            <span style="font-size:32px;line-height:1;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.35))">🗑️</span>
            <span style="position:absolute;top:0;right:0;background:#e53935;color:#fff;border-radius:50%;min-width:18px;height:18px;padding:0 3px;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;font-family:sans-serif;border:1.5px solid #fff;box-sizing:border-box">${n}</span>
          </div>`,
          iconSize:    L.point(44, 44),
          iconAnchor:  L.point(22, 44),
          popupAnchor: L.point(0, -44),
        });
      },
    });

    reports
      .filter((r) => r.lat != null && r.lng != null)
      .forEach((r) => {
        // Handle both full Supabase URLs and legacy local filenames
        const imgUrl = r.image_path
          ? r.image_path.startsWith('http')
            ? r.image_path
            : `${API_BASE}/uploads/${r.image_path}`
          : null;

        const imgHtml = imgUrl
          ? `<img src="${imgUrl}" alt="reported waste" style="width:100%;height:110px;object-fit:cover;border-radius:6px;margin-bottom:8px;display:block" />`
          : '';
        const descHtml = r.description
          ? `<p style="margin:4px 0 0;font-size:12px;color:#444;font-style:italic">${esc(r.description)}</p>`
          : '';
        const addrHtml = r.address
          ? `<p style="margin:4px 0 0;font-size:11px;color:#666">📍 ${esc(r.address)}</p>`
          : '';
        const dateHtml = `<p style="margin:4px 0 0;font-size:10px;color:#999">${new Date(r.created_at).toLocaleDateString()}</p>`;

        const marker = L.marker([r.lat!, r.lng!], { icon: TrashIcon });
        marker.bindPopup(
          `<div style="min-width:180px;max-width:250px">
            ${imgHtml}
            <p style="margin:0;font-weight:700;font-size:13px">🗑️ ${r.count} item${r.count !== 1 ? 's' : ''} reported</p>
            ${descHtml}${addrHtml}${dateHtml}
          </div>`,
          { maxWidth: 270 }
        );
        mcg.addLayer(marker);
      });

    map.addLayer(mcg);
    clusterRef.current = mcg;

    return () => {
      if (clusterRef.current) {
        map.removeLayer(clusterRef.current);
      }
    };
  }, [reports, map]);

  return null;
}

// ── GBA Ward / Zone Layer (369 wards, 10 zones) ──────────────────────────────
// Escape user-supplied strings before interpolating into popup innerHTML
const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const ZONE_COLORS: Record<string, string> = {
  "Bommanahalli":        "#e74c3c",
  "Byatarayanapura":     "#3498db",
  "C.V. Raman Nagar":    "#2ecc71",
  "Gandhinagara":        "#f39c12",
  "Jayanagar":           "#9b59b6",
  "K.R. Pura":           "#1abc9c",
  "Mahadevapura":        "#e67e22",
  "Malleshwaram":        "#e91e8c",
  "Rajarajeshwarinagar": "#27ae60",
  "Yelahanka":           "#00bcd4",
};

function BangaloreZonesLayer() {
  const [geoData, setGeoData] = useState<any>(null);

  useEffect(() => {
    fetch("/wards.geojson")
      .then((r) => r.json())
      .then((data) => setGeoData(data))
      .catch(() => console.warn("Could not load GBA ward boundaries"));
  }, []);

  if (!geoData) return null;

  const getColor = (feature: any): string =>
    ZONE_COLORS[feature?.properties?.zone_name as string] ?? "#607d8b";

  return (
    <GeoJSON
      key="gba-wards"
      data={geoData}
      style={(feature: any) => ({
        fillColor: getColor(feature),
        weight: 1,
        opacity: 0.85,
        color: "#ffffff",
        fillOpacity: 0.38,
      })}
      onEachFeature={(feature: any, layer: any) => {
        const p        = feature?.properties ?? {};
        const ward     = p.ward_name  || p.Ward_Name || "Ward";
        const zone     = p.zone_name  || "";
        const assembly = p.Assembly   || "";
        layer.bindPopup(
          `<b style="font-size:13px">${ward}</b>` +
          (zone     ? `<br/><span style="color:#555;font-size:11px">📍 ${zone} Zone</span>` : "") +
          (assembly ? `<br/><span style="color:#888;font-size:10px">🗳️ ${assembly}</span>` : "")
        );
        layer.on("mouseover", (e: any) => {
          e.target.setStyle({ fillOpacity: 0.7, weight: 2 });
          e.target.bringToFront();
        });
        layer.on("mouseout", (e: any) =>
          e.target.setStyle({ fillOpacity: 0.38, weight: 1 })
        );
      }}
    />
  );
}

const MapPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [center, setCenter] = useState<[number, number]>([12.9716, 77.5946]);
  const hasCenteredRef = React.useRef(false);

  const fetchReports = async () => {
    try {
      const response = await fetch(`${API_BASE}/reports`);
      if (!response.ok) throw new Error('Failed to fetch reports');
      const data: Report[] = await response.json();
      setReports(data);

      // Only fly to the newest report the first time — don't disrupt the user on every poll
      if (!hasCenteredRef.current) {
        const first = data.find((r) => r.lat !== null && r.lng !== null);
        if (first) {
          setCenter([first.lat as number, first.lng as number]);
          hasCenteredRef.current = true;
        }
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  useEffect(() => {
    fetchReports();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchReports, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="section map-page">
      <div className="container">
        <div className="map-header">
          <h2 className="map-title">Interactive Map</h2>
        </div>

        <div className="map-info">
          <span className="map-badge">
            {reports.length} reports
          </span>
          <span className="map-description">
            Heat intensity shows garbage concentration
          </span>
        </div>

        <div className="map-wrapper">
          <MapContainer 
            center={[12.9716, 77.5946]} 
            zoom={11} 
            style={{ height: '100%', width: '100%', borderRadius: '12px' }}
            zoomControl={true}
            scrollWheelZoom={true}
          >
            <LayersControl position="topright">
              {/* Base tile layers */}
              <LayersControl.BaseLayer checked name="OpenStreetMap Standard">
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
                />
              </LayersControl.BaseLayer>
              <LayersControl.BaseLayer name="CartoDB Light">
                <TileLayer
                  attribution='&copy; <a href="https://carto.com">CARTO</a>'
                  url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
                />
              </LayersControl.BaseLayer>
              <LayersControl.BaseLayer name="CartoDB Dark">
                <TileLayer
                  attribution='&copy; <a href="https://carto.com">CARTO</a>'
                  url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
                />
              </LayersControl.BaseLayer>

              {/* Overlay layers */}
              <LayersControl.Overlay checked name="Wards">
                <BangaloreZonesLayer />
              </LayersControl.Overlay>
              <LayersControl.Overlay checked name="Trash Reports">
                <ClusteredReportMarkers reports={reports} />
              </LayersControl.Overlay>
              <LayersControl.Overlay checked name="Heatmap">
                <HeatmapLayer reports={reports} />
              </LayersControl.Overlay>
            </LayersControl>

            <MapController center={center} enabled={hasCenteredRef.current} />
          </MapContainer>
        </div>

        {/* Zone legend */}
        <div style={{ marginTop: 16, display: 'flex', flexWrap: 'wrap', gap: '8px 16px' }}>
          {Object.entries({
            "Bommanahalli":        "#e74c3c",
            "Byatarayanapura":     "#3498db",
            "C.V. Raman Nagar":    "#2ecc71",
            "Gandhinagara":        "#f39c12",
            "Jayanagar":           "#9b59b6",
            "K.R. Pura":           "#1abc9c",
            "Mahadevapura":        "#e67e22",
            "Malleshwaram":        "#e91e8c",
            "Rajarajeshwarinagar": "#27ae60",
            "Yelahanka":           "#00bcd4",
          }).map(([zone, color]) => (
            <span key={zone} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
              <span style={{ width: 14, height: 14, borderRadius: 3, background: color, display: 'inline-block', opacity: 0.85 }} />
              {zone}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
};

export default MapPage;
