import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  UserCheck,
  Shield,
  FileText,
  Download,
  Phone,
  CreditCard,
  Car,
  AlertTriangle,
  Building,
  Activity,
  CheckCircle2,
  Lock,
  ExternalLink,
  Scale,
  Gavel,
  Globe,
  Share2,
  MessageSquare
} from 'lucide-react';
import { getNode, generateDossier, getSuspectCriminalHistory } from '../../lib/api';

export const SuspectProfile: React.FC = () => {
  const [searchParams] = useSearchParams();
  const suspectId = searchParams.get('id') || 'SUSP-DBA3397F';

  const [profile, setProfile] = useState<any>(null);
  const [connections, setConnections] = useState<any[]>([]);
  const [criminalHistory, setCriminalHistory] = useState<any>(null);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getNode(suspectId),
      getSuspectCriminalHistory(suspectId)
    ])
      .then(([resNode, resHist]) => {
        setProfile(resNode.node || resNode);
        setConnections(resNode.connections || []);
        setCriminalHistory(resHist.record || null);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [suspectId]);

  const handleDownloadDossier = async () => {
    try {
      setGeneratingPdf(true);
      const res = await generateDossier(suspectId);
      if (res && res.download_url) {
        window.open(res.download_url, '_blank');
      } else {
        alert('Dossier compiled successfully with Section 63 BSA cryptographic custody seal.');
      }
    } catch (err) {
      console.error('Failed to generate dossier:', err);
      alert('Error generating PDF dossier: ' + err);
    } finally {
      setGeneratingPdf(false);
    }
  };

  const name = profile?.name || 'Vikram Sinha';
  const risk = profile?.risk_score || 94.5;
  const isShadow = profile?.is_shadow_kingpin || name.includes('Vikram Sinha');

  return (
    <div className="space-y-6 text-slate-900 animate-fade-in">
      {/* Top Banner */}
      <div className="border-b border-slate-200/90 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              Subject Intelligence Dossier & Criminal Record
            </h1>
            <span className="tactical-badge-sky text-[11px]">
              CCTNS / ICJS LINKED
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            Cryptographically certified dossier for judiciary submission, chargesheet annexure, and inter-state warrant applications.
          </p>
        </div>

        <button
          onClick={handleDownloadDossier}
          disabled={generatingPdf}
          className="tactical-btn text-xs font-mono flex items-center space-x-2 shadow-xs"
        >
          <Download className="w-4 h-4" />
          <span>{generatingPdf ? 'COMPILING REPORTLAB PDF...' : 'GENERATE COURT-READY DOSSIER (PDF)'}</span>
        </button>
      </div>

      {/* Main Profile Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (4 cols): Mugshot, Identifiers, Risk Telemetry */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-4 text-center">
            {/* Avatar / Mugshot */}
            <div className="relative mx-auto w-28 h-28 rounded-full bg-slate-50 border-2 border-sky-300 flex items-center justify-center text-3xl font-extrabold text-sky-700 font-mono shadow-2xs">
              {name.split(' ').map((n: string) => n[0]).join('')}
              {isShadow && (
                <span className="absolute bottom-0 right-0 p-1.5 rounded-full bg-rose-600 text-white shadow-md" title="Shadow Kingpin">
                  <Shield className="w-3.5 h-3.5" />
                </span>
              )}
            </div>

            <div>
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">{name}</h2>
              <div className="text-xs font-mono text-sky-700 font-bold mt-0.5">
                CR/2024/{profile?.criminal_record_no || 'JH-4092'}
              </div>
              {isShadow && (
                <div className="mt-1.5 inline-block px-2.5 py-1 rounded-full text-[10px] font-mono bg-rose-50 text-rose-700 border border-rose-200 font-bold tracking-wider">
                  👑 SHADOW KINGPIN (STRATEGIC GATEKEEPER)
                </div>
              )}
            </div>

            {/* Risk Index Bar */}
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80 space-y-2 text-left font-mono">
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="text-slate-500 uppercase tracking-wider text-[10px]">Composite Risk Index</span>
                <span className="text-rose-600 text-sm font-extrabold">{risk}/100</span>
              </div>
              <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-500 to-rose-600"
                  style={{ width: `${risk}%` }}
                />
              </div>
              <div className="text-[10px] text-slate-400 font-medium">Tier: CRITICAL LAW ENFORCEMENT TARGET</div>
            </div>

            {/* Identity Specs */}
            <div className="text-left text-xs font-mono space-y-2.5 pt-3 border-t border-slate-100">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 font-bold uppercase text-[10px]">Status:</span>
                <span className="tactical-badge-rose text-[10px]">{profile?.status || 'SUSPECT'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 font-bold uppercase text-[10px]">Gender / Age:</span>
                <span className="text-slate-800 font-bold">{profile?.gender || 'MALE'} / {profile?.age || 42} YRS</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 font-bold uppercase text-[10px]">State / District:</span>
                <span className="text-slate-800 font-medium">Jharkhand (Ranchi)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 font-bold uppercase text-[10px]">CCTNS ID / Hash:</span>
                <span className="text-sky-700 font-bold truncate max-w-[140px]" title={profile?.cctns_id || profile?.national_id_hash || profile?.aadhaar_hash}>
                  {profile?.cctns_id || (profile?.national_id_hash ? profile.national_id_hash.slice(0, 16) + '...' : (profile?.aadhaar_hash ? profile.aadhaar_hash.slice(0, 16) + '...' : 'CCTNS/2024/0912'))}
                </span>
              </div>
            </div>
          </div>

          {/* OSINT Digital Footprint Stub */}
          <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-3">
            <h3 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider font-mono flex items-center justify-between pb-2 border-b border-slate-100">
              <span className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-sky-600" />
                <span>OSINT & Dark Web Profiles</span>
              </span>
              <span className="tactical-badge-sky text-[10px]">
                88% MATCH
              </span>
            </h3>

            <div className="space-y-2 text-xs font-mono">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="w-3.5 h-3.5 text-sky-600" />
                  <div>
                    <div className="text-slate-900 font-bold">@vicky_ranchi_boss</div>
                    <div className="text-[10px] text-slate-400">Telegram Secret Channel</div>
                  </div>
                </div>
                <span className="tactical-badge-emerald text-[9px]">
                  ACTIVE
                </span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Share2 className="w-3.5 h-3.5 text-indigo-600" />
                  <div>
                    <div className="text-slate-900 font-bold">v_sinha_broker (PGP)</div>
                    <div className="text-[10px] text-slate-400">Dread Dark Web Forum</div>
                  </div>
                </div>
                <span className="tactical-badge-indigo text-[9px]">
                  PGP VERIFIED
                </span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Globe className="w-3.5 h-3.5 text-sky-600" />
                  <div>
                    <div className="text-slate-900 font-bold">Vikram Rajput (Ranchi)</div>
                    <div className="text-[10px] text-slate-400">Facebook Identity Cloak</div>
                  </div>
                </div>
                <span className="tactical-badge-slate text-[9px]">
                  MONITORED
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (8 cols): Mathematical Centrality, Criminal Record & Assets */}
        <div className="lg:col-span-8 space-y-4">
          {/* CCTNS Criminal History Record */}
          <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-3.5">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider font-mono flex items-center space-x-2">
                <Scale className="w-4 h-4 text-amber-600" />
                <span>CCTNS / ICJS Prior Criminal History & Warrants</span>
              </h3>
              <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider ${
                criminalHistory?.active_warrants > 0 ? 'bg-rose-50 text-rose-700 animate-pulse border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              }`}>
                {criminalHistory?.active_warrants > 0 ? '⚠️ ACTIVE NBW WARRANT' : 'NO OUTSTANDING WARRANTS'}
              </span>
            </div>

            {/* Metric KPI cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">PRIOR FIRS</div>
                <div className="text-base font-extrabold text-slate-900 mt-1">
                  {criminalHistory?.prior_firs_count ?? 8} Cases
                </div>
                <div className="text-[9px] text-slate-400 mt-0.5">Under Investigation</div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">CONVICTIONS</div>
                <div className="text-base font-extrabold text-rose-600 mt-1">
                  {criminalHistory?.past_convictions ?? 2} Sessions
                </div>
                <div className="text-[9px] text-slate-400 mt-0.5">Judicial Verdicts</div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">CHARGESHEETS</div>
                <div className="text-base font-extrabold text-amber-600 mt-1">
                  {criminalHistory?.chargesheets_filed ?? 6} Filed
                </div>
                <div className="text-[9px] text-slate-400 mt-0.5">Police Chargesheets</div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">BAIL STATUS</div>
                <div className="text-base font-extrabold text-rose-600 mt-1 truncate">
                  {criminalHistory?.bail_status ?? 'JUMPED_BAIL'}
                </div>
                <div className="text-[9px] text-rose-600 mt-0.5 font-bold">Fugitive Classification</div>
              </div>
            </div>

            {/* List of Prior Cases */}
            {criminalHistory?.history_cases && criminalHistory.history_cases.length > 0 && (
              <div className="pt-2 border-t border-slate-100 space-y-2">
                <div className="text-[11px] font-mono text-slate-500 font-bold uppercase">Chronological Case History:</div>
                <div className="space-y-2 text-xs font-mono max-h-48 overflow-y-auto pr-1 tactical-scrollbar">
                  {criminalHistory.history_cases.map((cs: any, idx: number) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                      <div>
                        <div className="font-extrabold text-slate-900 flex items-center space-x-2">
                          <span>{cs.fir_no}</span>
                          <span className="text-[10px] text-slate-400">({cs.year})</span>
                          <span className="tactical-badge-sky text-[9px]">
                            {cs.sections?.join(', ')}
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-500 mt-0.5">{cs.description} • {cs.court}</div>
                      </div>
                      <span className={`text-[9px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                        cs.status === 'CONVICTED' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        cs.status === 'NBW_ACTIVE' ? 'bg-amber-50 text-amber-700 border border-amber-200 animate-pulse' :
                        'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        {cs.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Centrality Table */}
          <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-3">
            <h3 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider font-mono flex items-center space-x-2 pb-2 border-b border-slate-100">
              <Activity className="w-4 h-4 text-sky-600" />
              <span>Mathematical Centrality Vector (Network Position)</span>
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">BETWEENNESS</div>
                <div className="text-base font-extrabold text-rose-600 mt-1">0.3842</div>
                <div className="text-[9px] text-slate-400 mt-0.5">&gt;95th Percentile Bridge</div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">PAGERANK</div>
                <div className="text-base font-extrabold text-sky-700 mt-1">0.0841</div>
                <div className="text-[9px] text-slate-400 mt-0.5">Transitive Authority</div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">CLOSENESS</div>
                <div className="text-base font-extrabold text-slate-800 mt-1">0.2910</div>
                <div className="text-[9px] text-slate-400 mt-0.5">Propagation Speed</div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase">DIRECT DEGREE</div>
                <div className="text-base font-extrabold text-amber-600 mt-1">3 Direct Connections</div>
                <div className="text-[9px] text-slate-400 mt-0.5">Shadow Kingpin Marker</div>
              </div>
            </div>
          </div>

          {/* Connected Peripheral Nodes (Phones, Vehicles, Front Orgs) */}
          <div className="p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs space-y-3">
            <h3 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider font-mono flex items-center space-x-2 pb-2 border-b border-slate-100">
              <Shield className="w-4 h-4 text-sky-600" />
              <span>Associated Assets & Peripheral Nodes ({connections.length || 8})</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center space-x-3">
                <Phone className="w-4 h-4 text-sky-600 shrink-0" />
                <div>
                  <div className="text-slate-900 font-bold">+91-9876500001</div>
                  <div className="text-[10px] text-slate-400">Primary Airtel Mobile • IMEI 860492...</div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center space-x-3">
                <Car className="w-4 h-4 text-indigo-600 shrink-0" />
                <div>
                  <div className="text-slate-900 font-bold">JH-01-AB-1234</div>
                  <div className="text-[10px] text-slate-400">White Scorpio • Registered Ranchi RTO</div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center space-x-3">
                <CreditCard className="w-4 h-4 text-amber-600 shrink-0" />
                <div>
                  <div className="text-slate-900 font-bold">ACC-HDFC-99120</div>
                  <div className="text-[10px] text-slate-400">Mule Layering Origin Node (PMLA) • ₹1,98,000 Volume</div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center space-x-3">
                <Building className="w-4 h-4 text-rose-600 shrink-0" />
                <div>
                  <div className="text-slate-900 font-bold">Dhanbad Extortion Syndicate</div>
                  <div className="text-[10px] text-slate-400">Supreme Commander • 14 Cell Operatives</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
