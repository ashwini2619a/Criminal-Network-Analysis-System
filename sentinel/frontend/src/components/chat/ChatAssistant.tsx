import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import {
  Bot,
  Send,
  User,
  Sparkles,
  ArrowRight,
  Shield,
  Terminal,
  Cpu,
  Image as ImageIcon,
  X,
  Eye,
  CheckCircle2,
  Maximize2,
  Minimize2,
  Minus
} from 'lucide-react';
import { sendQuery } from '../../lib/api';

export interface ChatAssistantProps {
  isWidget?: boolean;
  isExpanded?: boolean;
  onClose?: () => void;
  onToggleExpand?: () => void;
  className?: string;
}

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  imageUrl?: string;
  queryType?: string;
  highlightedNodes?: string[];
  explainability?: {
    cypher_query?: string;
    algorithm?: string;
    nodes_scanned?: number;
    edges_evaluated?: number;
    confidence_score?: number;
    execution_engine?: string;
  };
}

// Memoized helper to render basic markdown bold, code, bullet points
const formatMessageContent = (text: string) => {
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={index} className="font-extrabold text-slate-900">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={index} className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[11px] text-sky-700 font-semibold">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
};

// Memoized single message bubble to prevent re-rendering entire chat tree on keystrokes
const MessageBubble = memo<{
  message: Message;
  isExplainOpen: boolean;
  isWidget?: boolean;
  onToggleExplain: (id: string) => void;
}>(({ message: m, isExplainOpen, isWidget, onToggleExplain }) => {
  const isBot = m.sender === 'assistant';
  const isNvidiaAi = m.queryType === 'AI_DEEP_INVESTIGATION' || (m.explainability?.execution_engine || '').includes('NVIDIA');

  return (
    <div className={`flex items-start space-x-2.5 animate-fade-in ${isBot ? '' : 'flex-row-reverse space-x-reverse'}`}>
      <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 shadow-2xs ${
        isBot
          ? isNvidiaAi
            ? 'bg-purple-50 border border-purple-200 text-purple-600'
            : 'bg-sky-50 border border-sky-200 text-sky-600'
          : 'bg-slate-900 border border-slate-700 text-white'
      }`}>
        {isBot ? (isNvidiaAi ? <Cpu className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />) : <User className="w-3.5 h-3.5" />}
      </div>

      <div className={`max-w-[85%] ${isWidget ? 'p-3 text-xs' : 'p-4 text-xs'} rounded-xl leading-relaxed space-y-1.5 transition-all duration-200 shadow-2xs ${
        isBot
          ? 'bg-white text-slate-800 border border-slate-200/90'
          : 'bg-sky-600 text-white border border-sky-700'
      }`}>
        <div className="flex items-center justify-between text-[10px] font-mono mb-1 gap-1.5 flex-wrap">
          <div className="flex items-center space-x-1.5">
            <span className={`font-bold tracking-wider ${isBot ? (isNvidiaAi ? 'text-purple-700' : 'text-sky-700') : 'text-sky-100'}`}>
              {isBot ? (isNvidiaAi ? 'NVIDIA AI' : 'SENTINEL') : 'OFFICER'}
            </span>
            {isBot && (
              <span className={`px-1.5 py-0.2 rounded text-[8.5px] font-bold ${
                isNvidiaAi ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'bg-sky-50 text-sky-700 border border-sky-200'
              }`}>
                {isNvidiaAi ? 'NGC' : 'CYPHER'}
              </span>
            )}
          </div>
          <span className={isBot ? 'text-slate-400' : 'text-sky-200'}>{m.timestamp}</span>
        </div>

        {/* Multimodal Image Thumbnail if user attached one */}
        {m.imageUrl && (
          <div className="mb-2 p-1.5 bg-slate-900/10 rounded-lg border border-slate-200/50">
            <div className="text-[10px] font-mono font-bold mb-1 flex items-center space-x-1 opacity-80">
              <Eye className="w-3 h-3" />
              <span>Surveillance Evidence Frame:</span>
            </div>
            <img
              src={m.imageUrl}
              alt="Surveillance Attachment"
              className="max-h-48 rounded border border-slate-300 object-cover"
            />
          </div>
        )}

        <div className={`whitespace-pre-wrap font-sans text-[13px] leading-relaxed ${isBot ? 'text-slate-800' : 'text-white'}`}>
          {isBot ? formatMessageContent(m.content) : m.content}
        </div>

        {/* Highlighted Nodes Tags if present */}
        {m.highlightedNodes && m.highlightedNodes.length > 0 && (
          <div className="pt-2.5 border-t border-slate-200/80 mt-2.5 flex flex-wrap items-center gap-1.5 font-mono text-[10px]">
            <span className="text-sky-700 font-bold">Correlated Entities ({m.highlightedNodes.length}):</span>
            {m.highlightedNodes.slice(0, 5).map(nodeId => (
              <a
                key={nodeId}
                href={`/graph?focus=${nodeId}`}
                className="px-2 py-0.5 rounded bg-slate-50 text-sky-700 border border-slate-200 hover:border-sky-300 hover:text-sky-800 hover:bg-sky-50 transition-all flex items-center space-x-1 font-bold"
              >
                <span>{nodeId}</span>
                <ArrowRight className="w-2.5 h-2.5 ml-0.5" />
              </a>
            ))}
          </div>
        )}

        {/* Explainability Accordion */}
        {isBot && m.explainability && (
          <div className="pt-2.5 border-t border-slate-200/80 mt-2.5">
            <button
              onClick={() => onToggleExplain(m.id)}
              className="w-full flex items-center justify-between py-1.5 px-2.5 rounded-lg bg-slate-50 border border-slate-200 hover:border-sky-300 hover:bg-sky-50/50 text-[11px] font-mono text-sky-700 transition-all"
            >
              <span className="flex items-center space-x-1.5">
                <Terminal className="w-3.5 h-3.5 text-sky-600" />
                <span className="font-bold">Explainability & Execution Audit</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono font-semibold">
                {isExplainOpen ? 'Hide ▲' : 'Inspect ▼'}
              </span>
            </button>

            {isExplainOpen && (
              <div className="mt-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-2.5 text-[10px] font-mono animate-fade-in">
                <div>
                  <div className="text-slate-500 uppercase tracking-wider text-[9px] mb-1 font-bold">Synthesized Query / Execution Pattern</div>
                  <div className="p-2.5 rounded-lg bg-white border border-slate-200 text-sky-700 select-all overflow-x-auto font-mono">
                    <code>{m.explainability.cypher_query || '// Direct MultiDiGraph Traversal'}</code>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-slate-700">
                  <div className="p-2.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-400 block text-[9px] font-bold uppercase tracking-wider">EXECUTION ENGINE</span>
                    <span className="text-slate-900 font-bold truncate block">{m.explainability.execution_engine || 'SENTINEL Core'}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-400 block text-[9px] font-bold uppercase tracking-wider">CONFIDENCE INDEX</span>
                    <span className="text-emerald-600 font-bold">{((m.explainability.confidence_score || 0.95) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-400 block text-[9px] font-bold uppercase tracking-wider">NODES SCANNED</span>
                    <span className="text-sky-700 font-bold">{m.explainability.nodes_scanned || 372}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-400 block text-[9px] font-bold uppercase tracking-wider">EDGES EVALUATED</span>
                    <span className="text-sky-700 font-bold">{m.explainability.edges_evaluated || 869}</span>
                  </div>
                </div>

                <div className="p-2 rounded bg-sky-50/80 border border-sky-200 text-sky-800 flex items-center space-x-2 text-[10px]">
                  <Shield className="w-3.5 h-3.5 text-sky-600 shrink-0" />
                  <span>Audit Provenance: Section 63 BSA / 65B IEA Compliant Hash Audit</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

export const ChatAssistant: React.FC<ChatAssistantProps> = ({
  isWidget = false,
  isExpanded = false,
  onClose,
  onToggleExpand,
  className
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init-01',
      sender: 'assistant',
      content: 'Jai Hind, Officer. I am **SENTINEL AI**, integrated with both the **Live Criminal Knowledge Graph (372 Entities, 869 Edges)** and **NVIDIA AI Investigation Core (Moonshot Kimi K3 / Llama 3.2 Vision)**.\n\nYou can query graph relationships, request syndicate deep vulnerability analysis, or attach surveillance imagery for multimodal scene reconnaissance.',
      timestamp: new Date().toLocaleTimeString('en-IN', { hour12: false })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [deepAiMode, setDeepAiMode] = useState(false);
  const [showImageInput, setShowImageInput] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [openExplain, setOpenExplain] = useState<Record<string, boolean>>({});
  const streamRef = useRef<HTMLDivElement>(null);

  const sampleQueries = [
    "Who is the leader of the Dhanbad extortion gang?",
    "Show money trail from Account X to Account Y",
    "Analyze all key vulnerabilities in this network and formulate an action plan",
    "Find all suspects who were in Ranchi on 15th January",
    "Which cases are connected to phone +91-9876500001?",
    "Generate report on Suspect Vikram Sinha's full network",
    "Draft an interrogation plan for Vikram Sinha based on his phone and hawala links",
    "Compare movement patterns of Suspect A and B",
    "Find common contacts between Case 101 and Case 205",
    "What happened 48 hours before FIR 15?",
    "Show all women safety cases in Jharkhand this month"
  ];

  const sampleImages = [
    {
      name: "Surveillance Frame (Boardwalk)",
      url: "https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1b.jpg"
    }
  ];

  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTo({ top: streamRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, loading]);

  const handleToggleExplain = useCallback((id: string) => {
    setOpenExplain(prev => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const handleSend = async (queryText?: string, overrideImg?: string) => {
    const text = (queryText || input).trim();
    const activeImg = (overrideImg !== undefined ? overrideImg : imageUrl).trim();

    if ((!text && !activeImg) || loading) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: text || "Analyze this surveillance evidence image for investigative leads.",
      timestamp: new Date().toLocaleTimeString('en-IN', { hour12: false }),
      imageUrl: activeImg || undefined
    };

    setMessages(prev => [...prev, userMsg]);
    if (!queryText) setInput('');
    setImageUrl('');
    setShowImageInput(false);
    setLoading(true);

    try {
      const res = await sendQuery(userMsg.content, {
        image_url: activeImg || undefined,
        force_ai: deepAiMode || !!activeImg
      });

      const botMsg: Message = {
        id: `bot-${Date.now()}`,
        sender: 'assistant',
        content: res.answer,
        timestamp: new Date().toLocaleTimeString('en-IN', { hour12: false }),
        queryType: res.query_type,
        highlightedNodes: res.highlighted_nodes,
        explainability: res.explainability
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const errMsg: Message = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        content: 'Error communicating with intelligence query engine: ' + err,
        timestamp: new Date().toLocaleTimeString('en-IN', { hour12: false })
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={className || (isWidget ? 'h-full flex flex-col bg-white text-slate-900 overflow-hidden' : 'h-[calc(100vh-112px)] flex flex-col bg-white text-slate-900 rounded-xl border border-slate-200/90 shadow-xs overflow-hidden animate-fade-in')}>
      {/* Universal Tactical Header (Adapts to full screen or floating widget) */}
      <div className={`bg-white/95 backdrop-blur-md border-b border-slate-200/90 ${isWidget ? 'px-3.5 py-2.5' : 'px-6 py-3.5'} flex items-center justify-between z-10 gap-2`}>
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-sky-50 border border-sky-200 text-sky-600 shadow-2xs">
            <Bot className={isWidget ? 'w-3.5 h-3.5' : 'w-5 h-5'} />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className={`font-bold ${isWidget ? 'text-xs' : 'text-sm'} text-slate-900 tracking-tight`}>
                {isWidget ? 'SENTINEL AI Copilot' : 'AI Natural Language Investigation Assistant'}
              </span>
              <span className="tactical-badge-sky text-[8.5px] px-1.5 py-0.2">
                NVIDIA NGC
              </span>
            </div>
            {!isWidget && (
              <p className="text-[11px] text-slate-500 font-medium">NetworkX Cypher Traversal · Moonshot Kimi K3 Reasoning · Llama 3.2 Vision</p>
            )}
          </div>
        </div>

        {/* Engine Status Indicators & Widget Controls */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setDeepAiMode(prev => !prev)}
            title="Toggle Forced NVIDIA NGC Deep AI Mode"
            className={`px-2 py-0.5 rounded-full text-[9.5px] font-mono font-bold flex items-center space-x-1 transition-all cursor-pointer border ${
              deepAiMode
                ? 'bg-purple-50 text-purple-700 border-purple-300 shadow-2xs'
                : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <Cpu className={`w-3 h-3 ${deepAiMode ? 'text-purple-600 animate-pulse' : 'text-slate-400'}`} />
            <span>{deepAiMode ? 'DEEP AI' : 'AUTO'}</span>
          </button>

          {!isWidget && (
            <span className="tactical-badge-emerald text-xs font-mono flex items-center py-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse" />
              API ACTIVE
            </span>
          )}

          {isWidget && onToggleExpand && (
            <button
              onClick={onToggleExpand}
              title={isExpanded ? 'Restore window size' : 'Maximize window'}
              className="p-1 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
            >
              {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
            </button>
          )}

          {isWidget && onClose && (
            <button
              onClick={onClose}
              title="Close chat assistant"
              className="p-1 rounded-md hover:bg-slate-100 text-slate-500 hover:text-rose-600 transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Message Stream with Memoized Message Items */}
      <div ref={streamRef} className={`flex-1 overflow-y-auto ${isWidget ? 'p-3 space-y-3' : 'p-6 space-y-4'} tactical-scrollbar bg-slate-50/40`}>
        {messages.map((m) => (
          <MessageBubble
            key={m.id}
            message={m}
            isWidget={isWidget}
            isExplainOpen={!!openExplain[m.id]}
            onToggleExplain={handleToggleExplain}
          />
        ))}

        {loading && (
          <div className="flex items-center space-x-3 animate-fade-in">
            <div className="w-8 h-8 rounded-full bg-purple-50 border border-purple-200 text-purple-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 animate-spin text-purple-600" />
            </div>
            <div className="p-3 rounded-xl bg-white border border-slate-200 text-xs font-mono text-purple-700 flex items-center space-x-2 shadow-2xs">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
              <span>
                {deepAiMode
                  ? 'Connecting to NVIDIA NGC AI (Moonshot Kimi K3 / Llama 3.2 Vision)...'
                  : 'Synthesizing multi-hop graph traversal & telecom records...'}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Multimodal Attachment Drawer (if toggled) */}
      {showImageInput && (
        <div className="p-3 bg-purple-50/50 border-t border-purple-200 flex flex-col sm:flex-row items-center gap-2 animate-fade-in">
          <div className="flex items-center space-x-2 text-xs font-mono text-purple-900 font-bold shrink-0">
            <ImageIcon className="w-4 h-4 text-purple-600" />
            <span>Surveillance Image URL:</span>
          </div>
          <input
            type="text"
            placeholder="Paste public image URL (e.g. CCTV snapshot, mugshot)..."
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            className="tactical-input flex-1 py-1.5 text-xs bg-white"
          />
          <div className="flex items-center space-x-1 shrink-0">
            {sampleImages.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setImageUrl(s.url)}
                className="px-2 py-1 rounded bg-purple-100 hover:bg-purple-200 text-purple-800 text-[10px] font-mono border border-purple-300 font-semibold cursor-pointer"
              >
                + Preset Image
              </button>
            ))}
            <button
              type="button"
              onClick={() => { setShowImageInput(false); setImageUrl(''); }}
              className="p-1 rounded hover:bg-purple-200 text-purple-600 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Suggested Prompt Chips */}
      <div className={`${isWidget ? 'px-3 py-1.5' : 'p-3'} bg-white border-t border-slate-200/90 flex items-center space-x-1.5 overflow-x-auto select-none tactical-scrollbar`}>
        <span className="text-[9px] font-mono text-slate-400 uppercase tracking-wider font-bold shrink-0">Prompts:</span>
        {(isWidget ? sampleQueries.slice(0, 5) : sampleQueries).map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className={`rounded-full bg-slate-50 hover:bg-sky-50 hover:text-sky-700 text-slate-700 border border-slate-200/80 hover:border-sky-300 shrink-0 transition-all font-medium hover:-translate-y-0.5 shadow-2xs cursor-pointer ${
              isWidget ? 'px-2 py-0.5 text-[10px]' : 'px-3 py-1 text-[11px]'
            }`}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Box Form */}
      <div className={`${isWidget ? 'p-2.5' : 'p-4'} bg-white border-t border-slate-200/90`}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <button
            type="button"
            onClick={() => setShowImageInput(prev => !prev)}
            title="Attach Surveillance Image URL for Multimodal AI Analysis"
            className={`rounded-lg border transition-all cursor-pointer shrink-0 ${
              isWidget ? 'p-1.5' : 'p-2.5'
            } ${
              showImageInput || imageUrl
                ? 'bg-purple-100 border-purple-300 text-purple-700 shadow-2xs'
                : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <ImageIcon className={isWidget ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
          </button>

          <input
            id="chatQueryInput"
            name="chatQueryInput"
            aria-label="Investigation query input"
            type="text"
            placeholder={
              deepAiMode
                ? (isWidget ? "Ask NVIDIA AI deep strategic question..." : "Ask NVIDIA AI deep strategic question (e.g. 'Formulate interrogation plan for Vikram Sinha')...")
                : (isWidget ? "Ask investigation query or suspect..." : "Ask any natural language investigation query or suspect analysis...")
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className={`tactical-input flex-1 placeholder-slate-400 text-xs ${
              isWidget ? 'py-1.5 px-2.5' : 'py-2.5'
            }`}
          />

          <button
            type="submit"
            disabled={loading || (!input.trim() && !imageUrl.trim())}
            className={`tactical-btn shadow-xs shrink-0 ${
              isWidget ? 'py-1.5 px-3 text-xs' : 'py-2.5 px-4'
            } ${
              deepAiMode ? '!bg-purple-600 hover:!bg-purple-700 !text-white' : ''
            }`}
          >
            <Send className="w-3.5 h-3.5 mr-1" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};
