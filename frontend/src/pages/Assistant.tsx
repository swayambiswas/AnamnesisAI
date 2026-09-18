import React, { useState } from 'react';
import { AgentResponse, MemoryRecord } from '@/lib/api/types';
import { Chat } from '@/components/chat/Chat';
import { MemoryCard } from '@/components/memory/MemoryCard';
import { ProvenancePanel } from '@/components/provenance/ProvenancePanel';
import { ConflictView } from '@/components/conflict/ConflictView';
import { Timeline } from '@/components/timeline/Timeline';
import { motion, AnimatePresence } from 'framer-motion';
import { UserCircle, Shield, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Assistant() {
  const [userId, setUserId] = useState('user_1');
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [view, setView] = useState<'context' | 'timeline'>('context');

  const handleResponse = (res: AgentResponse) => {
    setResponse(res);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Navigation */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-surface/30 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center space-x-6">
          <Link to="/" className="text-muted hover:text-primary transition-colors">
            <ArrowLeft size={18} />
          </Link>
          <div className="flex flex-col">
            <span className="text-sm font-bold tracking-widest uppercase text-white">Anamnesis</span>
            <span className="text-[10px] text-primary tracking-widest font-mono">TEMPORAL ENGINE</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs font-mono text-muted bg-surface px-3 py-1.5 rounded-full border border-white/5">
            <Shield size={12} />
            <span>ISOLATED SESSION</span>
          </div>
          <select 
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="bg-surface text-sm text-gray-200 py-1.5 px-3 rounded-lg border border-white/10 focus:outline-none focus:border-primary/50"
          >
            <option value="user_1">User 1</option>
            <option value="user_2">User 2</option>
          </select>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-4rem)]">
        
        {/* Chat Section */}
        <section className="lg:col-span-7 h-full flex flex-col relative z-10">
          <Chat userId={userId} onResponse={handleResponse} />
        </section>

        {/* Memory Context Section */}
        <section className="lg:col-span-5 h-full flex flex-col space-y-6 overflow-y-auto pr-2 pb-10">
          
          {/* View Toggles */}
          <div className="flex p-1 bg-surface rounded-lg border border-white/5">
            <button
              onClick={() => setView('context')}
              className={`flex-1 py-2 text-xs font-medium rounded-md transition-colors ${view === 'context' ? 'bg-black text-primary' : 'text-muted hover:text-gray-300'}`}
            >
              MEMORY CONTEXT
            </button>
            <button
              onClick={() => setView('timeline')}
              className={`flex-1 py-2 text-xs font-medium rounded-md transition-colors ${view === 'timeline' ? 'bg-black text-primary' : 'text-muted hover:text-gray-300'}`}
            >
              TIMELINE
            </button>
          </div>

          <AnimatePresence mode="wait">
            {view === 'context' && (
              <motion.div
                key="context"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {/* Conflict Resolution */}
                {response?.conflict_detected && response.memories && (
                  <ConflictView memories={response.memories} />
                )}

                {/* Primary Memory Context */}
                <div className="space-y-4">
                  <h3 className="text-xs font-semibold tracking-widest text-muted uppercase">Active Context</h3>
                  {!response ? (
                    <div className="h-32 rounded-xl border border-dashed border-white/10 flex items-center justify-center text-muted text-sm">
                      Waiting for query...
                    </div>
                  ) : response.memories && response.memories.length > 0 ? (
                    <div className="space-y-3">
                      {response.memories.map((mem: MemoryRecord) => (
                        <MemoryCard key={mem.id} memory={mem} />
                      ))}
                    </div>
                  ) : (
                    <div className="p-6 rounded-xl border border-white/5 bg-surface text-center">
                      <h4 className="text-sm font-medium text-gray-300 mb-1">NO RELEVANT MEMORY</h4>
                      <p className="text-xs text-muted">I couldn't find a stored memory relevant to this question. Try asking about something you've previously shared.</p>
                    </div>
                  )}
                </div>

                {/* Provenance */}
                <ProvenancePanel response={response} />
              </motion.div>
            )}

            {view === 'timeline' && (
              <motion.div
                key="timeline"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="bg-black/20 rounded-xl p-6 border border-white/5 min-h-[500px]"
              >
                <h3 className="text-xs font-semibold tracking-widest text-muted uppercase mb-8">Memory Evolution</h3>
                {response?.memories && response.memories.length > 0 ? (
                  <Timeline memories={response.memories} />
                ) : (
                  <p className="text-sm text-muted text-center mt-10">Ask a timeline query like "How did my language preference change?" to visualize temporal history.</p>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </main>
    </div>
  );
}
