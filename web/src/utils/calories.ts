import { SportType } from '../db';

/**
 * MET values for different activities.
 * MET = Metabolic Equivalent of Task
 */
const MET_VALUES: Record<SportType, number> = {
  running: 9.8,    // Running 6 mph (10 min/mile)
  cycling: 7.5,    // Cycling 12-14 mph
  walking: 3.5,    // Walking 3.5 mph
  hiking: 6.0,     // Hiking
  swimming: 6.0,   // Swimming, moderate effort
  other: 5.0,      // General exercise
};

/**
 * Estimate calories burned during activity.
 * Formula: Calories = MET × weight(kg) × duration(hours)
 * 
 * @param sportType - Type of sport
 * @param durationSeconds - Duration in seconds
 * @param weightKg - User weight in kg (default: 70kg)
 * @returns Estimated calories burned
 */
export function estimateCalories(
  sportType: SportType,
  durationSeconds: number,
  weightKg: number = 70
): number {
  const met = MET_VALUES[sportType] || MET_VALUES.other;
  const durationHours = durationSeconds / 3600;
  return Math.round(met * weightKg * durationHours);
}

/**
 * Estimate calories with distance factor.
 * More accurate for running/walking.
 * 
 * @param sportType - Type of sport
 * @param distanceMeters - Distance in meters
 * @param durationSeconds - Duration in seconds
 * @param weightKg - User weight in kg
 */
export function estimateCaloriesWithDistance(
  sportType: SportType,
  distanceMeters: number,
  durationSeconds: number,
  weightKg: number = 70
): number {
  // For running/walking, use distance-based calculation
  if (sportType === 'running' || sportType === 'walking') {
    // Rough estimate: ~1 kcal per kg per km
    const distanceKm = distanceMeters / 1000;
    const factor = sportType === 'running' ? 1.0 : 0.5;
    return Math.round(weightKg * distanceKm * factor);
  }

  // For other activities, use MET-based calculation
  return estimateCalories(sportType, durationSeconds, weightKg);
}
