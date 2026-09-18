import React from 'react';
import { MemoryRecord } from '@/lib/api/types';
import { MemoryCard } from '@/components/memory/MemoryCard';
import { AlertTriangle, ArrowRightLeft } from 'lucide-react';
import { motion } from 'framer-motion';

interface ConflictViewProps {
  memories: MemoryRecord[];
}

export const ConflictView: React.FC<ConflictViewProps> = ({ memories }) => {
  if (memories.length < 2) return null;

  return (
    <div className="p-6 rounded-xl border border-amber-500/30 bg-amber-500/5">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 rounded-lg bg-amber-500/20">
          <AlertTriangle className="text-amber-500 w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-amber-500 tracking-wide uppercase">Contradiction Detected</h3>
          <p className="text-xs text-amber-500/70 mt-0.5">The system retrieved active memories that conflict.</p>
        </div>
      </div>
      
      <div className="flex flex-col md:flex-row items-center justify-center gap-4">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="w-full md:w-5/12">
          <MemoryCard memory={memories[0]} />
        </motion.div>
        
        <div className="flex-shrink-0 text-amber-500/50">
          <ArrowRightLeft className="w-6 h-6" />
        </div>
        
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="w-full md:w-5/12">
          <MemoryCard memory={memories[1]} />
        </motion.div>
      </div>
    </div>
  );
};

