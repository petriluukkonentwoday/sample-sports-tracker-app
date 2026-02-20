import { useState, useCallback, useRef, useEffect } from 'react';

export interface GpsPosition {
  latitude: number;
  longitude: number;
  elevation_meters: number | null;
  accuracy_meters: number | null;
  speed_mps: number | null;
  timestamp: string;
}

export interface UseGeolocationResult {
  currentPosition: GpsPosition | null;
  positions: GpsPosition[];
  isTracking: boolean;
  isPaused: boolean;
  error: string | null;
  start: () => void;
  pause: () => void;
  resume: () => void;
  stop: () => GpsPosition[];
  clearError: () => void;
}

export function useGeolocation(): UseGeolocationResult {
  const [currentPosition, setCurrentPosition] = useState<GpsPosition | null>(null);
  const [positions, setPositions] = useState<GpsPosition[]>([]);
  const [isTracking, setIsTracking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const watchIdRef = useRef<number | null>(null);
  const positionsRef = useRef<GpsPosition[]>([]);

  const clearWatch = useCallback(() => {
    if (watchIdRef.current !== null) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
  }, []);

  const handlePosition = useCallback((position: GeolocationPosition) => {
    const gpsPoint: GpsPosition = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      elevation_meters: position.coords.altitude,
      accuracy_meters: position.coords.accuracy,
      speed_mps: position.coords.speed,
      timestamp: new Date(position.timestamp).toISOString(),
    };

    setCurrentPosition(gpsPoint);
    
    if (!isPaused) {
      positionsRef.current = [...positionsRef.current, gpsPoint];
      setPositions(positionsRef.current);
    }
    
    setError(null);
  }, [isPaused]);

  const handleError = useCallback((positionError: GeolocationPositionError) => {
    let message = 'Unknown geolocation error';
    
    switch (positionError.code) {
      case positionError.PERMISSION_DENIED:
        message = 'Location permission denied. Please enable location access.';
        break;
      case positionError.POSITION_UNAVAILABLE:
        message = 'Location information unavailable.';
        break;
      case positionError.TIMEOUT:
        message = 'Location request timed out.';
        break;
    }
    
    setError(message);
  }, []);

  const start = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser.');
      return;
    }

    setError(null);
    setIsTracking(true);
    setIsPaused(false);
    positionsRef.current = [];
    setPositions([]);

    // First, get current position
    navigator.geolocation.getCurrentPosition(handlePosition, handleError, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    });

    // Then start watching
    watchIdRef.current = navigator.geolocation.watchPosition(
      handlePosition,
      handleError,
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  }, [handlePosition, handleError]);

  const pause = useCallback(() => {
    setIsPaused(true);
  }, []);

  const resume = useCallback(() => {
    setIsPaused(false);
  }, []);

  const stop = useCallback((): GpsPosition[] => {
    clearWatch();
    setIsTracking(false);
    setIsPaused(false);
    const finalPositions = positionsRef.current;
    return finalPositions;
  }, [clearWatch]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearWatch();
    };
  }, [clearWatch]);

  return {
    currentPosition,
    positions,
    isTracking,
    isPaused,
    error,
    start,
    pause,
    resume,
    stop,
    clearError,
  };
}
