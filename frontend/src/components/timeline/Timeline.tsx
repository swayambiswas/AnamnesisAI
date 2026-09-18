import React from 'react';
import { MemoryRecord } from '@/lib/api/types';
import { MemoryCard } from '@/components/memory/MemoryCard';
import { motion } from 'framer-motion';

interface TimelineProps {
  memories: MemoryRecord[];
}

export const Timeline: React.FC<TimelineProps> = ({ memories }) => {
  // Sort by valid_from
  const sorted = [...memories].sort((a, b) => {
    return new Date(a.valid_from || 0).getTime() - new Date(b.valid_from || 0).getTime();
  });

  return (
    <div className="relative py-8">
      {/* Center line */}
      <div className="absolute left-1/2 top-0 bottom-0 w-px bg-border -translate-x-1/2" />

      <div className="space-y-12">
        {sorted.map((memory, i) => {
          const isLeft = i % 2 === 0;
          return (
            <motion.div 
              key={memory.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className={`flex w-full ${isLeft ? 'justify-start' : 'justify-end'} relative`}
            >
              {/* Timeline dot */}
              <div className="absolute left-1/2 top-1/2 w-3 h-3 bg-background border-2 border-primary rounded-full -translate-x-1/2 -translate-y-1/2 z-10" />
              
              <div className={`w-5/12 ${isLeft ? 'pr-8' : 'pl-8'}`}>
                <MemoryCard memory={memory} compact />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
