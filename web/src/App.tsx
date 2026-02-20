import { Routes, Route, Link, useLocation } from 'react-router-dom';
import ActivityList from './pages/ActivityList';
import ActivityDetail from './pages/ActivityDetail';
import RecordActivity from './pages/RecordActivity';
import Stats from './pages/Stats';

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link
      to={to}
      className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        isActive
          ? 'bg-primary-600 text-white'
          : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      {children}
    </Link>
  );
}

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-primary-600">
            Sports Tracker
          </Link>
          <nav className="flex gap-2">
            <NavLink to="/">Activities</NavLink>
            <NavLink to="/record">Record</NavLink>
            <NavLink to="/stats">Stats</NavLink>
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<ActivityList />} />
            <Route path="/activities/:id" element={<ActivityDetail />} />
            <Route path="/record" element={<RecordActivity />} />
            <Route path="/stats" element={<Stats />} />
          </Routes>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-4xl mx-auto px-4 text-center text-sm text-gray-500">
          Sports Tracker - Data stored locally in your browser
        </div>
      </footer>
    </div>
  );
}
