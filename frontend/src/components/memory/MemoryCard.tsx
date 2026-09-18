import React from 'react';
import { MemoryRecord } from '@/lib/api/types';
import { cn } from '@/lib/utils';
import { Clock, History, AlertCircle, EyeOff, Archive } from 'lucide-react';
import { motion } from 'framer-motion';

interface MemoryCardProps {
  memory: MemoryRecord;
  className?: string;
  onClick?: () => void;
  compact?: boolean;
}

const statusConfig = {
  ACTIVE: { icon: Clock, color: 'text-primary', bg: 'bg-primary/10', border: 'border-primary/30' },
  SUPERSEDED: { icon: History, color: 'text-muted', bg: 'bg-surface', border: 'border-border' },
  FORGOTTEN: { icon: EyeOff, color: 'text-red-500/70', bg: 'bg-red-500/5', border: 'border-red-500/20' },
  CONTRADICTION: { icon: AlertCircle, color: 'text-amber-500', bg: 'bg-amber-500/10', border: 'border-amber-500/30' },
  ARCHIVED: { icon: Archive, color: 'text-muted', bg: 'bg-surface', border: 'border-border' },
  EXPIRED: { icon: History, color: 'text-muted', bg: 'bg-surface', border: 'border-border' }
};

export const MemoryCard: React.FC<MemoryCardProps> = ({ memory, className, onClick, compact }) => {
  const config = statusConfig[memory.status as keyof typeof statusConfig] || statusConfig.SUPERSEDED;
  const Icon = config.icon;

  return (
    <motion.div 
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={cn(
        "relative rounded-xl border p-4 transition-all duration-300",
        "backdrop-blur-sm",
        config.bg, config.border,
        onClick && "cursor-pointer hover:border-primary/50",
        className
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={cn("p-1.5 rounded-md", "bg-black/20")}>
            <Icon size={14} className={config.color} />
          </div>
          <span className={cn("text-xs font-mono font-medium tracking-wider", config.color)}>
            {memory.status}
          </span>
        </div>
        <span className="text-[10px] font-mono text-muted">{memory.id}</span>
      </div>

      {!compact && (
        <div className="mb-4">
          <p className="text-sm text-gray-300 mb-1">Extracted Fact</p>
          <div className="flex items-center space-x-2 font-mono text-sm bg-black/40 p-2 rounded border border-white/5 overflow-x-auto">
            <span className="text-blue-400">{memory.subject}</span>
            <span className="text-muted">→</span>
            <span className="text-purple-400">{memory.predicate}</span>
            <span className="text-muted">→</span>
            <span className="text-green-400">{memory.object}</span>
          </div>
        </div>
      )}

      <div className="flex flex-col space-y-1">
        <span className="text-sm font-medium text-gray-200">"{memory.content}"</span>
        <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
          <div className="flex flex-col">
            <span className="text-[10px] text-muted uppercase tracking-wider">Valid From</span>
            <span className="text-xs font-mono text-gray-400">
              {memory.valid_from ? new Date(memory.valid_from).toLocaleDateString() : 'N/A'}
            </span>
          </div>
          <div className="flex flex-col text-right">
            <span className="text-[10px] text-muted uppercase tracking-wider">Confidence</span>
            <span className="text-xs font-mono text-primary">{(memory.confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

