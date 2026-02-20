import { db, Activity, GpsPoint } from '../db';

/**
 * Export data format
 */
export interface ExportedActivity {
  activity: Activity;
  gpsPoints: Omit<GpsPoint, 'id'>[];
}

export interface ExportedData {
  version: string;
  exportedAt: string;
  activities: ExportedActivity[];
}

/**
 * Export a single activity with its GPS points.
 */
export async function exportActivity(activityId: string): Promise<ExportedActivity | null> {
  const activity = await db.activities.get(activityId);
  if (!activity) return null;

  const gpsPoints = await db.gpsPoints
    .where('activity_id')
    .equals(activityId)
    .toArray();

  // Remove the auto-generated id from GPS points
  const cleanedPoints = gpsPoints.map(({ id, ...point }) => point);

  return {
    activity,
    gpsPoints: cleanedPoints,
  };
}

/**
 * Export all activities with their GPS points.
 */
export async function exportAllActivities(): Promise<ExportedData> {
  const activities = await db.activities.toArray();
  const exportedActivities: ExportedActivity[] = [];

  for (const activity of activities) {
    const gpsPoints = await db.gpsPoints
      .where('activity_id')
      .equals(activity.id)
      .toArray();

    const cleanedPoints = gpsPoints.map(({ id, ...point }) => point);

    exportedActivities.push({
      activity,
      gpsPoints: cleanedPoints,
    });
  }

  return {
    version: '1.0',
    exportedAt: new Date().toISOString(),
    activities: exportedActivities,
  };
}

/**
 * Download data as a JSON file.
 */
export function downloadAsJson(data: unknown, filename: string): void {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Export a single activity and download as JSON.
 */
export async function downloadActivity(activityId: string): Promise<boolean> {
  const exported = await exportActivity(activityId);
  if (!exported) return false;

  const filename = `activity-${exported.activity.sport_type}-${exported.activity.started_at.split('T')[0]}.json`;
  
  const data: ExportedData = {
    version: '1.0',
    exportedAt: new Date().toISOString(),
    activities: [exported],
  };

  downloadAsJson(data, filename);
  return true;
}

/**
 * Export all activities and download as JSON.
 */
export async function downloadAllActivities(): Promise<void> {
  const data = await exportAllActivities();
  const date = new Date().toISOString().split('T')[0];
  const filename = `sports-tracker-export-${date}.json`;
  downloadAsJson(data, filename);
}

/**
 * Validate imported data structure.
 */
function validateImportedData(data: unknown): data is ExportedData {
  if (!data || typeof data !== 'object') return false;
  
  const obj = data as Record<string, unknown>;
  
  if (!obj.version || typeof obj.version !== 'string') return false;
  if (!Array.isArray(obj.activities)) return false;

  for (const item of obj.activities) {
    if (!item || typeof item !== 'object') return false;
    
    const activityItem = item as Record<string, unknown>;
    
    // Validate activity
    const activity = activityItem.activity as Record<string, unknown>;
    if (!activity || typeof activity !== 'object') return false;
    if (!activity.id || typeof activity.id !== 'string') return false;
    if (!activity.sport_type || typeof activity.sport_type !== 'string') return false;
    if (!activity.started_at || typeof activity.started_at !== 'string') return false;
    
    // Validate gpsPoints array
    if (!Array.isArray(activityItem.gpsPoints)) return false;
  }

  return true;
}

/**
 * Import result
 */
export interface ImportResult {
  success: boolean;
  imported: number;
  skipped: number;
  errors: string[];
}

/**
 * Import activities from JSON data.
 * Skips activities that already exist (by ID).
 */
export async function importActivities(jsonData: string): Promise<ImportResult> {
  const result: ImportResult = {
    success: false,
    imported: 0,
    skipped: 0,
    errors: [],
  };

  let data: unknown;
  try {
    data = JSON.parse(jsonData);
  } catch (e) {
    result.errors.push('Invalid JSON format');
    return result;
  }

  if (!validateImportedData(data)) {
    result.errors.push('Invalid data structure. Expected Sports Tracker export format.');
    return result;
  }

  for (const item of data.activities) {
    try {
      // Check if activity already exists
      const existing = await db.activities.get(item.activity.id);
      if (existing) {
        result.skipped++;
        continue;
      }

      // Import activity and GPS points in a transaction
      await db.transaction('rw', [db.activities, db.gpsPoints], async () => {
        await db.activities.add(item.activity);
        
        if (item.gpsPoints.length > 0) {
          const pointsWithActivityId = item.gpsPoints.map((point) => ({
            ...point,
            activity_id: item.activity.id,
          }));
          await db.gpsPoints.bulkAdd(pointsWithActivityId);
        }
      });

      result.imported++;
    } catch (e) {
      result.errors.push(`Failed to import activity "${item.activity.title}": ${e}`);
    }
  }

  result.success = result.errors.length === 0 || result.imported > 0;
  return result;
}

/**
 * Read a file as text.
 */
export function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}
