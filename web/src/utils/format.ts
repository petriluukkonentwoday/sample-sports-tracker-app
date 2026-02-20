/**
 * Format duration in seconds to human readable string.
 * @example formatDuration(3661) => "1:01:01"
 */
export function formatDuration(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format duration with labels.
 * @example formatDurationLong(3661) => "1h 1m 1s"
 */
export function formatDurationLong(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const parts: string[] = [];
  if (hrs > 0) parts.push(`${hrs}h`);
  if (mins > 0) parts.push(`${mins}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

  return parts.join(' ');
}

/**
 * Format distance in meters to km or m.
 * @example formatDistance(1500) => "1.50 km"
 */
export function formatDistance(meters: number): string {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(2)} km`;
  }
  return `${Math.round(meters)} m`;
}

/**
 * Format distance with short unit.
 */
export function formatDistanceShort(meters: number): string {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(1)}km`;
  }
  return `${Math.round(meters)}m`;
}

/**
 * Format pace (min/km) from speed in m/s.
 * @example formatPace(3.0) => "5:33 /km"
 */
export function formatPace(speedMps: number): string {
  if (speedMps <= 0) return '--:-- /km';
  
  const paceSecondsPerKm = 1000 / speedMps;
  const mins = Math.floor(paceSecondsPerKm / 60);
  const secs = Math.floor(paceSecondsPerKm % 60);
  
  return `${mins}:${secs.toString().padStart(2, '0')} /km`;
}

/**
 * Format speed in km/h from m/s.
 * @example formatSpeed(3.0) => "10.8 km/h"
 */
export function formatSpeed(speedMps: number): string {
  const kmh = speedMps * 3.6;
  return `${kmh.toFixed(1)} km/h`;
}

/**
 * Format elevation in meters.
 */
export function formatElevation(meters: number): string {
  return `${Math.round(meters)} m`;
}

/**
 * Format date for display.
 * @example formatDate("2024-02-20T10:30:00") => "Feb 20, 2024"
 */
export function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Format time for display.
 * @example formatTime("2024-02-20T10:30:00") => "10:30 AM"
 */
export function formatTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

/**
 * Format date and time.
 */
export function formatDateTime(isoString: string): string {
  return `${formatDate(isoString)} at ${formatTime(isoString)}`;
}

/**
 * Format relative time (e.g., "2 days ago").
 */
export function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return formatDate(isoString);
}
