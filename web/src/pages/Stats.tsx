import { useState, useMemo } from 'react';
import { useActivities } from '../db';
import { Card, CardTitle, Select, DistanceChart, SportDistribution } from '../components';
import { formatDistance, formatDurationLong } from '../utils';

type TimePeriod = 'week' | 'month' | 'year' | 'all';

export default function Stats() {
  const { activities, loading } = useActivities();
  const [period, setPeriod] = useState<TimePeriod>('week');

  // Filter activities by period
  const filteredActivities = useMemo(() => {
    if (period === 'all') return activities;

    const now = new Date();
    let cutoff: Date;

    switch (period) {
      case 'week':
        cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        cutoff = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case 'year':
        cutoff = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
      default:
        return activities;
    }

    return activities.filter((a) => new Date(a.started_at) >= cutoff);
  }, [activities, period]);

  // Calculate summary stats
  const stats = useMemo(() => {
    const totalDistance = filteredActivities.reduce(
      (sum, a) => sum + a.distance_meters,
      0
    );
    const totalDuration = filteredActivities.reduce(
      (sum, a) => sum + a.duration_seconds,
      0
    );
    const totalCalories = filteredActivities.reduce(
      (sum, a) => sum + (a.calories || 0),
      0
    );
    const activityCount = filteredActivities.length;
    const avgPace =
      totalDuration > 0 ? totalDistance / totalDuration : 0; // m/s

    return {
      totalDistance,
      totalDuration,
      totalCalories,
      activityCount,
      avgPace,
      avgDistance: activityCount > 0 ? totalDistance / activityCount : 0,
    };
  }, [filteredActivities]);

  const chartDays = period === 'week' ? 7 : period === 'month' ? 30 : 14;

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Statistics</h1>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Statistics</h1>

      {/* Period selector */}
      <Card>
        <Select
          label="Time Period"
          value={period}
          onChange={(e) => setPeriod(e.target.value as TimePeriod)}
          options={[
            { value: 'week', label: 'Last 7 days' },
            { value: 'month', label: 'Last 30 days' },
            { value: 'year', label: 'Last year' },
            { value: 'all', label: 'All time' },
          ]}
        />
      </Card>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <p className="stat-value">{filteredActivities.length}</p>
          <p className="stat-label">Activities</p>
        </Card>
        <Card>
          <p className="stat-value">{formatDistance(stats.totalDistance)}</p>
          <p className="stat-label">Total Distance</p>
        </Card>
        <Card>
          <p className="stat-value">{formatDurationLong(stats.totalDuration)}</p>
          <p className="stat-label">Total Time</p>
        </Card>
        <Card>
          <p className="stat-value">{stats.totalCalories.toLocaleString()}</p>
          <p className="stat-label">Calories</p>
        </Card>
      </div>

      {/* Distance chart */}
      <Card>
        <CardTitle className="mb-4">Distance by Day</CardTitle>
        <DistanceChart activities={activities} days={chartDays} />
      </Card>

      {/* Sport distribution */}
      <Card>
        <CardTitle className="mb-4">Distance by Sport</CardTitle>
        <SportDistribution activities={filteredActivities} />
      </Card>

      {/* Averages */}
      {stats.activityCount > 0 && (
        <Card>
          <CardTitle className="mb-4">Averages</CardTitle>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Avg Distance per Activity</p>
              <p className="font-medium">{formatDistance(stats.avgDistance)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg Duration per Activity</p>
              <p className="font-medium">
                {formatDurationLong(
                  stats.activityCount > 0
                    ? stats.totalDuration / stats.activityCount
                    : 0
                )}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Empty state */}
      {filteredActivities.length === 0 && (
        <Card className="text-center py-8">
          <div className="text-4xl mb-4">📊</div>
          <p className="text-gray-500">
            No activities found for the selected period.
          </p>
        </Card>
      )}
    </div>
  );
}
