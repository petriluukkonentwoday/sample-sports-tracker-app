import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { db, Activity, GpsPoint, SPORT_TYPES } from '../db';
import { useGpsPoints } from '../db';
import { RouteMap, Button, Card, Input } from '../components';
import {
  formatDistance,
  formatDuration,
  formatDurationLong,
  formatPace,
  formatSpeed,
  formatElevation,
  formatDateTime,
  estimateCaloriesWithDistance,
  downloadActivity,
} from '../utils';

export default function ActivityDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [activity, setActivity] = useState<Activity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { points, loading: pointsLoading } = useGpsPoints(id);

  // Load activity
  useEffect(() => {
    async function loadActivity() {
      if (!id) return;

      setLoading(true);
      try {
        const result = await db.activities.get(id);
        if (result) {
          setActivity(result);
          setEditTitle(result.title);
          setEditNotes(result.notes || '');
        } else {
          setError('Activity not found');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load activity');
      } finally {
        setLoading(false);
      }
    }

    loadActivity();
  }, [id]);

  const handleSaveEdit = useCallback(async () => {
    if (!id || !activity) return;

    await db.activities.update(id, {
      title: editTitle,
      notes: editNotes || null,
    });

    setActivity({
      ...activity,
      title: editTitle,
      notes: editNotes || null,
    });
    setIsEditing(false);
  }, [id, activity, editTitle, editNotes]);

  const handleDelete = useCallback(async () => {
    if (!id) return;

    await db.transaction('rw', [db.activities, db.gpsPoints], async () => {
      await db.gpsPoints.where('activity_id').equals(id).delete();
      await db.activities.delete(id);
    });

    navigate('/');
  }, [id, navigate]);

  const handleExport = useCallback(async () => {
    if (!id) return;
    await downloadActivity(id);
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (error || !activity) {
    return (
      <div className="space-y-4">
        <Card className="bg-red-50 border-red-200">
          <p className="text-red-600">{error || 'Activity not found'}</p>
        </Card>
        <Link to="/">
          <Button variant="secondary">Back to Activities</Button>
        </Link>
      </div>
    );
  }

  const sportType = SPORT_TYPES.find((s) => s.value === activity.sport_type);
  const avgPace = activity.avg_speed_mps || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link to="/" className="text-primary-600 hover:text-primary-700">
          ← Back
        </Link>
        <div className="flex gap-2">
          {!isEditing && (
            <>
              <Button variant="secondary" onClick={handleExport}>
                Export
              </Button>
              <Button variant="secondary" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
              <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
                Delete
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Title and meta */}
      <Card>
        {isEditing ? (
          <div className="space-y-4">
            <Input
              label="Title"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
            />
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">
                Notes
              </label>
              <textarea
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={3}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSaveEdit}>Save</Button>
              <Button variant="secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-4">
            <div className="text-4xl">{sportType?.icon || '💪'}</div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{activity.title}</h1>
              <p className="text-gray-500">{formatDateTime(activity.started_at)}</p>
              {activity.notes && (
                <p className="mt-2 text-gray-700">{activity.notes}</p>
              )}
            </div>
          </div>
        )}
      </Card>

      {/* Map */}
      {!pointsLoading && <RouteMap points={points} />}

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <p className="stat-value">{formatDistance(activity.distance_meters)}</p>
          <p className="stat-label">Distance</p>
        </Card>
        <Card>
          <p className="stat-value">{formatDuration(activity.duration_seconds)}</p>
          <p className="stat-label">Duration</p>
        </Card>
        <Card>
          <p className="stat-value">{formatPace(avgPace)}</p>
          <p className="stat-label">Avg Pace</p>
        </Card>
        <Card>
          <p className="stat-value">{formatSpeed(avgPace)}</p>
          <p className="stat-label">Avg Speed</p>
        </Card>
      </div>

      {/* Additional stats */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Calories</p>
            <p className="font-medium">
              {activity.calories || estimateCaloriesWithDistance(
                activity.sport_type,
                activity.distance_meters,
                activity.duration_seconds
              )}{' '}
              kcal
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">GPS Points</p>
            <p className="font-medium">{points.length}</p>
          </div>
          {activity.elevation_gain !== null && activity.elevation_gain > 0 && (
            <div>
              <p className="text-sm text-gray-500">Elevation Gain</p>
              <p className="font-medium">{formatElevation(activity.elevation_gain)}</p>
            </div>
          )}
          {activity.elevation_loss !== null && activity.elevation_loss > 0 && (
            <div>
              <p className="text-sm text-gray-500">Elevation Loss</p>
              <p className="font-medium">{formatElevation(activity.elevation_loss)}</p>
            </div>
          )}
          {activity.max_speed_mps !== null && activity.max_speed_mps > 0 && (
            <div>
              <p className="text-sm text-gray-500">Max Speed</p>
              <p className="font-medium">{formatSpeed(activity.max_speed_mps)}</p>
            </div>
          )}
        </div>
      </Card>

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-[1000]">
          <Card className="w-full max-w-sm">
            <h2 className="text-xl font-bold mb-2">Delete Activity?</h2>
            <p className="text-gray-600 mb-6">
              This action cannot be undone. All data including GPS points will be permanently deleted.
            </p>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDelete} className="flex-1">
                Delete
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
