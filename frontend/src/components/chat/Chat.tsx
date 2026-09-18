import React, { useState } from 'react';
import { AgentResponse, sendMessage } from '@/lib/api/mock';
import { Send, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ChatProps {
  userId: string;
  onResponse: (response: AgentResponse) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export const Chat: React.FC<ChatProps> = ({ userId, onResponse }) => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Hello. I am Anamnesis. I remember your context over time. Ask me about your current, past, or timeline.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const query = input.trim();
    setInput('');
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendMessage(userId, query);
      const asstMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', content: response.answer };
      setMessages(prev => [...prev, asstMsg]);
      onResponse(response);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: 'Error communicating with backend.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface border border-white/5 rounded-2xl overflow-hidden">
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <AnimatePresence>
          {messages.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "max-w-[85%] rounded-2xl p-4",
                msg.role === 'user' 
                  ? "ml-auto bg-primary text-black font-medium"
                  : "bg-black/40 text-gray-200 border border-white/5"
              )}
            >
              <p className="text-sm leading-relaxed">{msg.content}</p>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-black/40 text-gray-400 border border-white/5 max-w-[85%] rounded-2xl p-4 flex items-center space-x-3"
            >
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Retrieving memory...</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-white/5 bg-black/20">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about your memory..."
            className="w-full bg-surface border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/50 transition-colors"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 disabled:opacity-50 disabled:hover:bg-primary/10 transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </form>
    </div>
  );
};
