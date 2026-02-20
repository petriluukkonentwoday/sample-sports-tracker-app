import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, useMap } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import { GpsPosition } from '../hooks/useGeolocation';

interface LiveMapProps {
  positions: GpsPosition[];
  currentPosition: GpsPosition | null;
  className?: string;
}

// Component to handle map center updates
function MapCenterUpdater({ position }: { position: LatLngExpression | null }) {
  const map = useMap();
  
  useEffect(() => {
    if (position) {
      map.setView(position, map.getZoom());
    }
  }, [map, position]);

  return null;
}

export function LiveMap({ positions, currentPosition, className = '' }: LiveMapProps) {
  const mapRef = useRef<L.Map | null>(null);

  // Convert positions to Leaflet format
  const polylinePositions: LatLngExpression[] = positions.map((p) => [
    p.latitude,
    p.longitude,
  ]);

  const currentLatLng: LatLngExpression | null = currentPosition
    ? [currentPosition.latitude, currentPosition.longitude]
    : null;

  // Default center (will be overridden by current position)
  const defaultCenter: LatLngExpression = currentLatLng || [60.1699, 24.9384]; // Helsinki

  return (
    <div className={`h-64 md:h-96 rounded-lg overflow-hidden ${className}`}>
      <MapContainer
        center={defaultCenter}
        zoom={16}
        className="w-full h-full"
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Route polyline */}
        {polylinePositions.length > 1 && (
          <Polyline
            positions={polylinePositions}
            color="#2563eb"
            weight={4}
            opacity={0.8}
          />
        )}

        {/* Current position marker */}
        {currentLatLng && (
          <CircleMarker
            center={currentLatLng}
            radius={10}
            fillColor="#3b82f6"
            fillOpacity={1}
            color="#1d4ed8"
            weight={3}
          />
        )}

        {/* Auto-center on current position */}
        <MapCenterUpdater position={currentLatLng} />
      </MapContainer>
    </div>
  );
}
