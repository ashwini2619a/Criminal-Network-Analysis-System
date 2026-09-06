import React, { Suspense } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { FloatingChatWidget } from './components/chat/FloatingChatWidget';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Loader2 } from 'lucide-react';

// Lazy-loaded 14 Screen Components for Zero-Lag, Instant Rendering
const Dashboard = React.lazy(() => import('./components/dashboard/Dashboard').then(m => ({ default: m.Dashboard })));
const IngestionCenter = React.lazy(() => import('./components/ingestion/IngestionCenter').then(m => ({ default: m.IngestionCenter })));
const GraphExplorer = React.lazy(() => import('./components/graph/GraphExplorer').then(m => ({ default: m.GraphExplorer })));
const GeoIntelMap = React.lazy(() => import('./components/map/GeoIntelMap').then(m => ({ default: m.GeoIntelMap })));
const CDRAnalyzer = React.lazy(() => import('./components/cdr/CDRAnalyzer').then(m => ({ default: m.CDRAnalyzer })));
const FinancialFlow = React.lazy(() => import('./components/financial/FinancialFlow').then(m => ({ default: m.FinancialFlow })));
const TimelineView = React.lazy(() => import('./components/timeline/TimelineView').then(m => ({ default: m.TimelineView })));
const ChatAssistant = React.lazy(() => import('./components/chat/ChatAssistant').then(m => ({ default: m.ChatAssistant })));
const SuspectProfile = React.lazy(() => import('./components/suspect/SuspectProfile').then(m => ({ default: m.SuspectProfile })));
const EvidenceVault = React.lazy(() => import('./components/evidence/EvidenceVault').then(m => ({ default: m.EvidenceVault })));
const AlertCenter = React.lazy(() => import('./components/alerts/AlertCenter').then(m => ({ default: m.AlertCenter })));
const ReportGenerator = React.lazy(() => import('./components/reports/ReportGenerator').then(m => ({ default: m.ReportGenerator })));
const CaseBoard = React.lazy(() => import('./components/caseboard/CaseBoard').then(m => ({ default: m.CaseBoard })));
const AdminPanel = React.lazy(() => import('./components/admin/AdminPanel').then(m => ({ default: m.AdminPanel })));
const FaceTracker = React.lazy(() => import('./components/faces/FaceTracker').then(m => ({ default: m.FaceTracker })));
const PersonTracker = React.lazy(() => import('./components/persons/PersonTracker').then(m => ({ default: m.PersonTracker })));

const TacticalScreenLoader = () => (
  <div className="h-full min-h-[400px] flex flex-col items-center justify-center space-y-3">
    <div className="p-3 rounded-full bg-sky-50 border border-sky-200 text-sky-600 animate-spin">
      <Loader2 className="w-6 h-6" />
    </div>
    <div className="text-xs font-mono text-slate-500 font-semibold tracking-wider uppercase">
      Loading Tactical Subsystem...
    </div>
  </div>
);

export default function App() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50 text-slate-900 font-sans antialiased">
      {/* Top Universal Tactical Header */}
      <Header onAlertClick={() => navigate('/alerts')} />

      {/* Main Body: Sidebar + Active Screen */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-slate-50 p-6">
          <ErrorBoundary>
            <Suspense fallback={<TacticalScreenLoader />}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/ingest" element={<IngestionCenter />} />
                <Route path="/graph" element={<GraphExplorer />} />
                <Route path="/map" element={<GeoIntelMap />} />
                <Route path="/cdr" element={<CDRAnalyzer />} />
                <Route path="/financial" element={<FinancialFlow />} />
                <Route path="/timeline" element={<TimelineView />} />
                <Route path="/chat" element={<ChatAssistant />} />
                <Route path="/suspect" element={<SuspectProfile />} />
                <Route path="/faces" element={<FaceTracker />} />
                <Route path="/persons" element={<PersonTracker />} />
                <Route path="/evidence" element={<EvidenceVault />} />
                <Route path="/alerts" element={<AlertCenter />} />
                <Route path="/reports" element={<ReportGenerator />} />
                <Route path="/caseboard" element={<CaseBoard />} />
                <Route path="/admin" element={<AdminPanel />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </ErrorBoundary>
        </main>
      </div>

      {/* Universal Floating AI Investigation Assistant (Bottom-Right on Every Screen) */}
      <FloatingChatWidget />
    </div>
  );
}
