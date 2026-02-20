import { useState, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useActivities, SportType, SPORT_TYPES } from '../db';
import { ActivityCard, Button, Card, Select } from '../components';
import { downloadAllActivities, importActivities, readFileAsText, ImportResult } from '../utils';

export default function ActivityList() {
  const { activities, loading, error, loadActivities } = useActivities();
  const [sportFilter, setSportFilter] = useState<SportType | ''>('');
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFilterChange = (value: string) => {
    setSportFilter(value as SportType | '');
    loadActivities(value ? (value as SportType) : undefined);
  };

  const handleExportAll = useCallback(async () => {
    await downloadAllActivities();
  }, []);

  const handleImportClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImporting(true);
    setImportResult(null);

    try {
      const content = await readFileAsText(file);
      const result = await importActivities(content);
      setImportResult(result);
      
      if (result.imported > 0) {
        loadActivities();
      }
    } catch (err) {
      setImportResult({
        success: false,
        imported: 0,
        skipped: 0,
        errors: [err instanceof Error ? err.message : 'Import failed'],
      });
    } finally {
      setImporting(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, [loadActivities]);

  const dismissImportResult = useCallback(() => {
    setImportResult(null);
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Activities</h1>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Activities</h1>
        <Card className="bg-red-50 border-red-200">
          <p className="text-red-600">Error loading activities: {error}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Activities</h1>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={handleImportClick} disabled={importing}>
            {importing ? 'Importing...' : 'Import'}
          </Button>
          {activities.length > 0 && (
            <Button variant="secondary" onClick={handleExportAll}>
              Export All
            </Button>
          )}
          <Link to="/record">
            <Button>Record New</Button>
          </Link>
        </div>
      </div>

      {/* Hidden file input for import */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Import result message */}
      {importResult && (
        <Card className={importResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
          <div className="flex items-start justify-between">
            <div>
              {importResult.success ? (
                <p className="text-green-800">
                  Imported {importResult.imported} {importResult.imported === 1 ? 'activity' : 'activities'}
                  {importResult.skipped > 0 && `, skipped ${importResult.skipped} (already exist)`}
                </p>
              ) : (
                <p className="text-red-800">
                  Import failed: {importResult.errors.join(', ')}
                </p>
              )}
            </div>
            <button
              onClick={dismissImportResult}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
        </Card>
      )}

      {/* Filter */}
      <Card>
        <Select
          label="Filter by Sport"
          value={sportFilter}
          onChange={(e) => handleFilterChange(e.target.value)}
          options={[
            { value: '', label: 'All Sports' },
            ...SPORT_TYPES.map((s) => ({
              value: s.value,
              label: `${s.icon} ${s.label}`,
            })),
          ]}
        />
      </Card>

      {/* Activity list */}
      {activities.length === 0 ? (
        <Card className="text-center py-12">
          <div className="text-4xl mb-4">🏃</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No activities yet
          </h2>
          <p className="text-gray-500 mb-6">
            Record your first activity to get started!
          </p>
          <Link to="/record">
            <Button>Record Activity</Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-3">
          {activities.map((activity) => (
            <ActivityCard key={activity.id} activity={activity} />
          ))}
        </div>
      )}

      {/* Summary */}
      {activities.length > 0 && (
        <p className="text-sm text-gray-500 text-center">
          Showing {activities.length} {activities.length === 1 ? 'activity' : 'activities'}
        </p>
      )}
    </div>
  );
}
