# Sports Tracker Web UI 

A local-first web application for recording and viewing fitness activities. All data is stored in the browser using IndexedDB.

## Features

- **Record Activities** - GPS tracking with live map display
- **View Activities** - List and detail views with GPS route visualization
- **Statistics** - Summary stats and charts
- **Local Storage** - All data persisted in browser (IndexedDB via Dexie.js)
- **Export/Import** - Export activities to JSON, import them back or to another browser

## Quick Start

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

```bash
cd web
npm install
```

### Development

```bash
npm run dev
```

Opens the app at `http://localhost:1234` with hot reload.

### Build for Production

```bash
npm run build
```

Output is in the `dist/` folder.

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | React 18 + TypeScript |
| Build | Parcel |
| Styling | Tailwind CSS |
| Routing | React Router |
| Local Storage | Dexie.js (IndexedDB) |
| Maps | Leaflet + react-leaflet |
| Charts | Recharts |

## Project Structure

```
web/
├── src/
│   ├── index.html       # Entry HTML
│   ├── index.tsx        # React mount
│   ├── App.tsx          # Main app with routing
│   ├── db/              # Database (Dexie) setup
│   ├── components/      # Reusable components
│   ├── pages/           # Route pages
│   ├── hooks/           # Custom hooks (geolocation, timer)
│   ├── utils/           # Utility functions
│   └── styles/          # Tailwind CSS
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── postcss.config.js
```

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Activity List | `/` | Home - list of all activities |
| Record Activity | `/record` | GPS tracking + live map |
| Activity Detail | `/activities/:id` | View single activity with map |
| Stats | `/stats` | Aggregated statistics |

## Data Storage

All data is stored locally in the browser using IndexedDB:

- **activities** - Activity metadata (title, sport type, distance, duration, etc.)
- **gpsPoints** - GPS coordinates with timestamps

Data persists across browser sessions but is specific to each browser/device.

## GPS Tracking

The Record Activity page uses the browser's Geolocation API:

```javascript
navigator.geolocation.watchPosition(onPositionUpdate)
```

**Note**: GPS tracking requires:
- HTTPS (or localhost for development)
- User permission for location access
- Browser tab must stay open during recording

## Export/Import

### Export
- **Single activity**: Click "Export" on any activity detail page
- **All activities**: Click "Export All" on the activity list page

Exports are saved as JSON files containing all activity data and GPS points.

### Import
- Click "Import" on the activity list page
- Select a previously exported `.json` file
- Activities with the same ID are skipped (no duplicates)

### File Format

```json
{
  "version": "1.0",
  "exportedAt": "2024-02-20T10:30:00.000Z",
  "activities": [
    {
      "activity": {
        "id": "uuid",
        "title": "Morning Run",
        "sport_type": "running",
        "started_at": "2024-02-20T08:00:00.000Z",
        "distance_meters": 5000,
        ...
      },
      "gpsPoints": [
        { "latitude": 60.17, "longitude": 24.94, "timestamp": "...", ... }
      ]
    }
  ]
}
```

## Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

Mobile browsers are supported but battery drain may occur during extended GPS tracking.
