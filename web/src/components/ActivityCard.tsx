import { Link } from 'react-router-dom';
import { Activity, SPORT_TYPES } from '../db';
import { formatDistance, formatDuration, formatRelativeTime } from '../utils';
import { Card } from './ui';

interface ActivityCardProps {
  activity: Activity;
}

export function ActivityCard({ activity }: ActivityCardProps) {
  const sportType = SPORT_TYPES.find((s) => s.value === activity.sport_type);

  return (
    <Link to={`/activities/${activity.id}`}>
      <Card className="activity-card hover:border-primary-200 cursor-pointer">
        <div className="flex items-center gap-4">
          {/* Sport icon */}
          <div className="text-3xl">{sportType?.icon || '💪'}</div>

          {/* Activity info */}
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">
              {activity.title || `${sportType?.label || 'Activity'}`}
            </h3>
            <p className="text-sm text-gray-500">
              {formatRelativeTime(activity.started_at)}
            </p>
          </div>

          {/* Stats */}
          <div className="text-right">
            <p className="font-semibold text-gray-900">
              {formatDistance(activity.distance_meters)}
            </p>
            <p className="text-sm text-gray-500">
              {formatDuration(activity.duration_seconds)}
            </p>
          </div>
        </div>
      </Card>
    </Link>
  );
}
