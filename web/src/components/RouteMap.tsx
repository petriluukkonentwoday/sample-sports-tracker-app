import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, useMap } from 'react-leaflet';
import { LatLngExpression, LatLngBounds } from 'leaflet';
import { GpsPoint } from '../db';
import { calculateBounds } from '../utils';

interface RouteMapProps {
  points: GpsPoint[];
  className?: string;
}

// Component to fit map to route bounds
function MapBoundsFitter({ bounds }: { bounds: LatLngBounds | null }) {
  const map = useMap();
  
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  }, [map, bounds]);

  return null;
}

export function RouteMap({ points, className = '' }: RouteMapProps) {
  const mapRef = useRef<L.Map | null>(null);

  if (points.length === 0) {
    return (
      <div className={`h-64 md:h-96 rounded-lg bg-gray-100 flex items-center justify-center ${className}`}>
        <p className="text-gray-500">No GPS data available</p>
      </div>
    );
  }

  // Convert points to Leaflet format
  const polylinePositions: LatLngExpression[] = points.map((p) => [
    p.latitude,
    p.longitude,
  ]);

  // Calculate bounds
  const boundsData = calculateBounds(points);
  const bounds = boundsData
    ? new LatLngBounds(boundsData[0], boundsData[1])
    : null;

  // Start and end markers
  const startPosition: LatLngExpression = [points[0].latitude, points[0].longitude];
  const endPosition: LatLngExpression = [
    points[points.length - 1].latitude,
    points[points.length - 1].longitude,
  ];

  // Center point
  const center: LatLngExpression = startPosition;

  return (
    <div className={`h-64 md:h-96 rounded-lg overflow-hidden ${className}`}>
      <MapContainer
        center={center}
        zoom={14}
        className="w-full h-full"
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Route polyline */}
        <Polyline
          positions={polylinePositions}
          color="#2563eb"
          weight={4}
          opacity={0.8}
        />

        {/* Start marker (green) */}
        <CircleMarker
          center={startPosition}
          radius={8}
          fillColor="#22c55e"
          fillOpacity={1}
          color="#16a34a"
          weight={2}
        />

        {/* End marker (red) */}
        {points.length > 1 && (
          <CircleMarker
            center={endPosition}
            radius={8}
            fillColor="#ef4444"
            fillOpacity={1}
            color="#dc2626"
            weight={2}
          />
        )}

        {/* Fit to bounds */}
        <MapBoundsFitter bounds={bounds} />
      </MapContainer>
    </div>
  );
}
