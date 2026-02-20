import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Activity, SPORT_TYPES } from '../db';

interface DailyData {
  date: string;
  distance: number;
  duration: number;
  count: number;
}

interface StatsChartProps {
  activities: Activity[];
  days?: number;
}

export function DistanceChart({ activities, days = 7 }: StatsChartProps) {
  // Group activities by day
  const now = new Date();
  const data: DailyData[] = [];

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    const dayLabel = date.toLocaleDateString('en-US', { weekday: 'short' });

    const dayActivities = activities.filter((a) =>
      a.started_at.startsWith(dateStr)
    );

    data.push({
      date: dayLabel,
      distance: Math.round(
        dayActivities.reduce((sum, a) => sum + a.distance_meters, 0) / 1000 * 10
      ) / 10, // km with 1 decimal
      duration: Math.round(
        dayActivities.reduce((sum, a) => sum + a.duration_seconds, 0) / 60
      ), // minutes
      count: dayActivities.length,
    });
  }

  if (activities.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-gray-500">
        No activity data to display
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value: number) => [`${value} km`, 'Distance']}
          labelStyle={{ color: '#374151' }}
        />
        <Bar dataKey="distance" fill="#3b82f6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

interface SportDistributionProps {
  activities: Activity[];
}

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280'];

export function SportDistribution({ activities }: SportDistributionProps) {
  // Group by sport type
  const sportData = SPORT_TYPES.map((sport, index) => {
    const sportActivities = activities.filter(
      (a) => a.sport_type === sport.value
    );
    const totalDistance = sportActivities.reduce(
      (sum, a) => sum + a.distance_meters,
      0
    );

    return {
      name: sport.label,
      value: Math.round(totalDistance / 1000 * 10) / 10,
      color: COLORS[index % COLORS.length],
    };
  }).filter((d) => d.value > 0);

  if (sportData.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-gray-500">
        No activity data to display
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={sportData}
          cx="50%"
          cy="50%"
          innerRadius={40}
          outerRadius={80}
          paddingAngle={2}
          dataKey="value"
          label={({ name, value }) => `${name}: ${value}km`}
          labelLine={false}
        >
          {sportData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => [`${value} km`, 'Distance']} />
      </PieChart>
    </ResponsiveContainer>
  );
}
