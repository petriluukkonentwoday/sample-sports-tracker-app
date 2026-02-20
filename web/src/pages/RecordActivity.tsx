import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGeolocation, useTimer } from '../hooks';
import { db, Activity, GpsPoint, SportType, SPORT_TYPES } from '../db';
import { LiveMap, Button, Card, Select, Input } from '../components';
import {
  formatDuration,
  formatDistance,
  formatPace,
  calculateTotalDistance,
  calculateElevation,
  estimateCaloriesWithDistance,
} from '../utils';

type RecordingState = 'idle' | 'recording' | 'paused' | 'saving';

export default function RecordActivity() {
  const navigate = useNavigate();
  const [sportType, setSportType] = useState<SportType>('running');
  const [recordingState, setRecordingState] = useState<RecordingState>('idle');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');

  const geolocation = useGeolocation();
  const timer = useTimer();

  // Calculate live stats
  const distance = calculateTotalDistance(geolocation.positions);
  const pace = timer.seconds > 0 ? distance / timer.seconds : 0; // m/s

  const handleStart = useCallback(() => {
    geolocation.start();
    timer.start();
    setRecordingState('recording');
  }, [geolocation, timer]);

  const handlePause = useCallback(() => {
    geolocation.pause();
    timer.pause();
    setRecordingState('paused');
  }, [geolocation, timer]);

  const handleResume = useCallback(() => {
    geolocation.resume();
    timer.resume();
    setRecordingState('recording');
  }, [geolocation, timer]);

  const handleStop = useCallback(() => {
    geolocation.stop();
    timer.stop();
    setShowSaveModal(true);
    setRecordingState('saving');
  }, [geolocation, timer]);

  const handleSave = useCallback(async () => {
    const positions = geolocation.positions;
    const duration = timer.seconds;
    const totalDistance = calculateTotalDistance(positions);
    const elevation = calculateElevation(positions);
    const calories = estimateCaloriesWithDistance(sportType, totalDistance, duration);

    const now = new Date().toISOString();
    const startedAt = positions.length > 0 ? positions[0].timestamp : now;
    const endedAt = positions.length > 0 ? positions[positions.length - 1].timestamp : now;

    const activityId = crypto.randomUUID();

    // Create activity
    const activity: Activity = {
      id: activityId,
      title: title || `${SPORT_TYPES.find((s) => s.value === sportType)?.label || 'Activity'}`,
      sport_type: sportType,
      started_at: startedAt,
      ended_at: endedAt,
      distance_meters: totalDistance,
      duration_seconds: duration,
      calories,
      notes: notes || null,
      elevation_gain: elevation.gain,
      elevation_loss: elevation.loss,
      avg_speed_mps: duration > 0 ? totalDistance / duration : null,
      max_speed_mps: positions.length > 0
        ? Math.max(...positions.map((p) => p.speed_mps || 0))
        : null,
    };

    // Create GPS points
    const gpsPoints: GpsPoint[] = positions.map((p) => ({
      activity_id: activityId,
      latitude: p.latitude,
      longitude: p.longitude,
      elevation_meters: p.elevation_meters,
      timestamp: p.timestamp,
      speed_mps: p.speed_mps,
      accuracy_meters: p.accuracy_meters,
    }));

    // Save to database
    await db.transaction('rw', [db.activities, db.gpsPoints], async () => {
      await db.activities.add(activity);
      if (gpsPoints.length > 0) {
        await db.gpsPoints.bulkAdd(gpsPoints);
      }
    });

    // Navigate to activity detail
    navigate(`/activities/${activityId}`);
  }, [geolocation.positions, timer.seconds, sportType, title, notes, navigate]);

  const handleDiscard = useCallback(() => {
    setShowSaveModal(false);
    setRecordingState('idle');
    timer.reset();
    setTitle('');
    setNotes('');
  }, [timer]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Record Activity</h1>

      {/* Sport type selector (only shown when idle) */}
      {recordingState === 'idle' && (
        <Card>
          <Select
            label="Sport Type"
            value={sportType}
            onChange={(e) => setSportType(e.target.value as SportType)}
            options={SPORT_TYPES.map((s) => ({
              value: s.value,
              label: `${s.icon} ${s.label}`,
            }))}
          />
        </Card>
      )}

      {/* Error display */}
      {geolocation.error && (
        <Card className="bg-red-50 border-red-200">
          <div className="flex items-center gap-3">
            <span className="text-red-500">⚠️</span>
            <div>
              <p className="font-medium text-red-800">Location Error</p>
              <p className="text-sm text-red-600">{geolocation.error}</p>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={geolocation.clearError}
              className="ml-auto"
            >
              Dismiss
            </Button>
          </div>
        </Card>
      )}

      {/* Map */}
      {recordingState !== 'idle' && (
        <LiveMap
          positions={geolocation.positions}
          currentPosition={geolocation.currentPosition}
        />
      )}

      {/* Stats display */}
      {recordingState !== 'idle' && (
        <Card>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="stat-value">{formatDuration(timer.seconds)}</p>
              <p className="stat-label">Duration</p>
            </div>
            <div>
              <p className="stat-value">{formatDistance(distance)}</p>
              <p className="stat-label">Distance</p>
            </div>
            <div>
              <p className="stat-value">{formatPace(pace)}</p>
              <p className="stat-label">Pace</p>
            </div>
          </div>
        </Card>
      )}

      {/* Controls */}
      <Card>
        <div className="flex justify-center gap-4">
          {recordingState === 'idle' && (
            <Button onClick={handleStart} size="lg" className="w-full max-w-xs">
              Start Recording
            </Button>
          )}

          {recordingState === 'recording' && (
            <>
              <Button onClick={handlePause} variant="secondary" size="lg">
                Pause
              </Button>
              <Button onClick={handleStop} variant="danger" size="lg">
                Stop
              </Button>
            </>
          )}

          {recordingState === 'paused' && (
            <>
              <Button onClick={handleResume} variant="success" size="lg">
                Resume
              </Button>
              <Button onClick={handleStop} variant="danger" size="lg">
                Stop
              </Button>
            </>
          )}
        </div>
      </Card>

      {/* Recording indicator */}
      {recordingState === 'recording' && (
        <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
          <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          Recording in progress...
        </div>
      )}

      {recordingState === 'paused' && (
        <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
          <span className="w-2 h-2 bg-yellow-500 rounded-full" />
          Recording paused
        </div>
      )}

      {/* Save modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-[1000]">
          <Card className="w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Save Activity</h2>
            
            <div className="space-y-4">
              {/* Summary */}
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-500">Distance:</span>{' '}
                    <span className="font-medium">{formatDistance(distance)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Duration:</span>{' '}
                    <span className="font-medium">{formatDuration(timer.seconds)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">GPS Points:</span>{' '}
                    <span className="font-medium">{geolocation.positions.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Sport:</span>{' '}
                    <span className="font-medium">
                      {SPORT_TYPES.find((s) => s.value === sportType)?.label}
                    </span>
                  </div>
                </div>
              </div>

              <Input
                label="Title (optional)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={`${SPORT_TYPES.find((s) => s.value === sportType)?.label || 'Activity'}`}
              />

              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">
                  Notes (optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows={3}
                  placeholder="How did it feel?"
                />
              </div>

              <div className="flex gap-3">
                <Button onClick={handleDiscard} variant="secondary" className="flex-1">
                  Discard
                </Button>
                <Button onClick={handleSave} className="flex-1">
                  Save Activity
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
