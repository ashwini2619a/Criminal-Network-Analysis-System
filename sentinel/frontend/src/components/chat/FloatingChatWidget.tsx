import React, { useState } from 'react';
import { Bot, Sparkles, MessageSquare, ChevronDown } from 'lucide-react';
import { ChatAssistant } from './ChatAssistant';

export const FloatingChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="fixed bottom-5 right-5 z-50 select-none">
      {isOpen ? (
        <div
          className={`transition-all duration-300 ease-in-out shadow-card-elevated rounded-2xl overflow-hidden border border-slate-300/90 bg-white flex flex-col animate-scale-in ${
            isExpanded
              ? 'w-[720px] h-[620px] max-w-[calc(100vw-2rem)] max-h-[calc(100vh-4rem)]'
              : 'w-[360px] h-[500px] max-w-[calc(100vw-2rem)] max-h-[calc(100vh-4rem)]'
          }`}
        >
          <ChatAssistant
            isWidget={true}
            isExpanded={isExpanded}
            onToggleExpand={() => setIsExpanded(prev => !prev)}
            onClose={() => setIsOpen(false)}
            className="h-full flex flex-col bg-white"
          />
        </div>
      ) : (
        <button
          onClick={() => setIsOpen(true)}
          className="group relative flex items-center space-x-2.5 px-3.5 py-2 rounded-full bg-white/95 hover:bg-white text-slate-800 border border-slate-300/90 hover:border-sky-400 shadow-md hover:shadow-sky-500/15 backdrop-blur-md transition-all duration-200 hover:-translate-y-0.5 cursor-pointer"
          title="Open SENTINEL AI Investigation Copilot"
        >
          {/* Pulsing Live Status Dot */}
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>

          <div className="p-1 rounded-md bg-sky-50 border border-sky-200 text-sky-600 group-hover:text-sky-700 transition-colors">
            <Bot className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
          </div>

          <div className="text-left font-sans pr-0.5">
            <div className="text-xs font-bold text-slate-900 flex items-center space-x-1.5">
              <span>SENTINEL AI</span>
              <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-purple-50 text-purple-700 border border-purple-200 font-bold">
                NVIDIA
              </span>
            </div>
            <div className="text-[10px] text-slate-500 font-mono">
              Investigation Copilot
            </div>
          </div>
        </button>
      )}
    </div>
  );
};

export default FloatingChatWidget;
