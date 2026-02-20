/**
 * Calculate distance between two GPS points using Haversine formula.
 * @returns Distance in meters
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371000; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

/**
 * Calculate total distance from an array of GPS points.
 * @returns Total distance in meters
 */
export function calculateTotalDistance(
  points: { latitude: number; longitude: number }[]
): number {
  if (points.length < 2) return 0;

  let total = 0;
  for (let i = 1; i < points.length; i++) {
    total += calculateDistance(
      points[i - 1].latitude,
      points[i - 1].longitude,
      points[i].latitude,
      points[i].longitude
    );
  }
  return total;
}

/**
 * Calculate elevation gain and loss from GPS points.
 */
export function calculateElevation(
  points: { elevation_meters: number | null }[]
): { gain: number; loss: number } {
  let gain = 0;
  let loss = 0;

  const elevations = points
    .map((p) => p.elevation_meters)
    .filter((e): e is number => e !== null);

  if (elevations.length < 2) return { gain: 0, loss: 0 };

  for (let i = 1; i < elevations.length; i++) {
    const diff = elevations[i] - elevations[i - 1];
    if (diff > 0) {
      gain += diff;
    } else {
      loss += Math.abs(diff);
    }
  }

  return { gain, loss };
}

/**
 * Calculate center point of GPS coordinates.
 */
export function calculateCenter(
  points: { latitude: number; longitude: number }[]
): [number, number] {
  if (points.length === 0) return [0, 0];

  const sumLat = points.reduce((sum, p) => sum + p.latitude, 0);
  const sumLng = points.reduce((sum, p) => sum + p.longitude, 0);

  return [sumLat / points.length, sumLng / points.length];
}

/**
 * Calculate bounding box for GPS points.
 */
export function calculateBounds(
  points: { latitude: number; longitude: number }[]
): [[number, number], [number, number]] | null {
  if (points.length === 0) return null;

  const lats = points.map((p) => p.latitude);
  const lngs = points.map((p) => p.longitude);

  return [
    [Math.min(...lats), Math.min(...lngs)],
    [Math.max(...lats), Math.max(...lngs)],
  ];
}
