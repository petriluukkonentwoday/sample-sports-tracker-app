import { useState, useEffect, useCallback } from 'react';
import { db, GpsPoint } from './database';

export function useGpsPoints(activityId: string | undefined) {
  const [points, setPoints] = useState<GpsPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPoints = useCallback(async () => {
    if (!activityId) {
      setPoints([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await db.gpsPoints
        .where('activity_id')
        .equals(activityId)
        .sortBy('timestamp');
      setPoints(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load GPS points');
    } finally {
      setLoading(false);
    }
  }, [activityId]);

  useEffect(() => {
    loadPoints();
  }, [loadPoints]);

  const addPoints = useCallback(async (newPoints: GpsPoint[]): Promise<void> => {
    await db.gpsPoints.bulkAdd(newPoints);
  }, []);

  const addPoint = useCallback(async (point: GpsPoint): Promise<void> => {
    await db.gpsPoints.add(point);
  }, []);

  return {
    points,
    loading,
    error,
    loadPoints,
    addPoints,
    addPoint,
  };
}
