import React from 'react';
import { AgentResponse } from '@/lib/api/types';
import { Network, CheckCircle2, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

interface ProvenancePanelProps {
  response: AgentResponse | null;
}

export const ProvenancePanel: React.FC<ProvenancePanelProps> = ({ response }) => {
  if (!response || response.sources.length === 0) {
    return (
      <div className="p-6 border border-white/5 rounded-xl bg-surface/30 text-center">
        <Network className="w-8 h-8 text-muted mx-auto mb-3" />
        <h4 className="text-sm font-medium text-gray-300">No Provenance Data</h4>
        <p className="text-xs text-muted mt-1">Answer was generated without specific memory retrieval or memory was forgotten.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 pb-2 border-b border-white/5">
        <Network size={16} className="text-primary" />
        <h3 className="text-sm font-semibold tracking-wide uppercase text-gray-200">Why this answer?</h3>
      </div>
      
      <div className="space-y-3">
        {response.sources.map((source, idx) => (
          <motion.div 
            key={`${source.memory_id}-${idx}`}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="p-3 rounded-lg border border-white/10 bg-black/20"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-mono text-muted">{source.memory_id}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface border border-white/5 text-gray-300">
                {(source.confidence * 100).toFixed(0)}% CONF
              </span>
            </div>
            
            <div className="space-y-1.5">
              {source.reason.map((r, i) => (
                <div key={i} className="flex items-center space-x-2 text-xs text-gray-300">
                  {r === 'active_memory' || r === 'current_state_match' ? (
                    <CheckCircle2 size={12} className="text-primary" />
                  ) : r === 'superseded_memory' ? (
                    <AlertTriangle size={12} className="text-amber-500" />
                  ) : (
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 ml-0.5" />
                  )}
                  <span className="font-mono">{r.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
