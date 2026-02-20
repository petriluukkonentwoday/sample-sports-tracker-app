import Dexie, { Table } from 'dexie';

export interface Activity {
  id: string;
  title: string;
  sport_type: SportType;
  started_at: string;
  ended_at: string;
  distance_meters: number;
  duration_seconds: number;
  calories: number | null;
  notes: string | null;
  elevation_gain: number | null;
  elevation_loss: number | null;
  avg_speed_mps: number | null;
  max_speed_mps: number | null;
}

export interface GpsPoint {
  id?: number;
  activity_id: string;
  latitude: number;
  longitude: number;
  elevation_meters: number | null;
  timestamp: string;
  speed_mps: number | null;
  accuracy_meters: number | null;
}

export type SportType = 'running' | 'cycling' | 'walking' | 'hiking' | 'swimming' | 'other';

export const SPORT_TYPES: { value: SportType; label: string; icon: string }[] = [
  { value: 'running', label: 'Running', icon: '🏃' },
  { value: 'cycling', label: 'Cycling', icon: '🚴' },
  { value: 'walking', label: 'Walking', icon: '🚶' },
  { value: 'hiking', label: 'Hiking', icon: '🥾' },
  { value: 'swimming', label: 'Swimming', icon: '🏊' },
  { value: 'other', label: 'Other', icon: '💪' },
];

class SportsTrackerDB extends Dexie {
  activities!: Table<Activity>;
  gpsPoints!: Table<GpsPoint>;

  constructor() {
    super('SportsTrackerDB');
    this.version(1).stores({
      activities: 'id, sport_type, started_at',
      gpsPoints: '++id, activity_id, timestamp',
    });
  }
}

export const db = new SportsTrackerDB();
