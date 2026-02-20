import { useState, useEffect, useCallback } from 'react';
import { db, Activity, SportType } from './database';

export function useActivities() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadActivities = useCallback(async (sportType?: SportType) => {
    setLoading(true);
    setError(null);
    try {
      let query = db.activities.orderBy('started_at').reverse();
      if (sportType) {
        const all = await query.toArray();
        setActivities(all.filter(a => a.sport_type === sportType));
      } else {
        setActivities(await query.toArray());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load activities');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  const getActivity = useCallback(async (id: string): Promise<Activity | undefined> => {
    return db.activities.get(id);
  }, []);

  const createActivity = useCallback(async (activity: Activity): Promise<void> => {
    await db.activities.add(activity);
    await loadActivities();
  }, [loadActivities]);

  const updateActivity = useCallback(async (id: string, updates: Partial<Activity>): Promise<void> => {
    await db.activities.update(id, updates);
    await loadActivities();
  }, [loadActivities]);

  const deleteActivity = useCallback(async (id: string): Promise<void> => {
    await db.transaction('rw', [db.activities, db.gpsPoints], async () => {
      await db.gpsPoints.where('activity_id').equals(id).delete();
      await db.activities.delete(id);
    });
    await loadActivities();
  }, [loadActivities]);

  return {
    activities,
    loading,
    error,
    loadActivities,
    getActivity,
    createActivity,
    updateActivity,
    deleteActivity,
  };
}
