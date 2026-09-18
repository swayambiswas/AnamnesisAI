import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Clock, ShieldAlert, GitMerge, FileQuestion } from 'lucide-react';

export default function Landing() {
  // Simple scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-background text-gray-100 selection:bg-primary selection:text-black">
      {/* Navigation */}
      <nav className="fixed w-full z-50 px-6 py-4 flex justify-between items-center bg-background/80 backdrop-blur-lg border-b border-white/5">
        <div className="text-sm font-bold tracking-widest uppercase">Anamnesis</div>
        <Link 
          to="/assistant" 
          className="text-xs font-semibold tracking-widest uppercase bg-primary text-black px-5 py-2.5 rounded hover:bg-primary/90 transition-colors"
        >
          Enter the Memory
        </Link>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 pt-20 overflow-hidden">
        {/* Background typographic elements */}
        <div className="absolute inset-0 pointer-events-none opacity-5 flex flex-col justify-between overflow-hidden">
          <h1 className="text-[15vw] font-bold leading-none tracking-tighter ml-[-2vw]">TEMPORAL</h1>
          <h1 className="text-[15vw] font-bold leading-none tracking-tighter text-right mr-[-2vw]">MEMORY</h1>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight leading-[1.1] mb-6">
              An AI that <br />
              <span className="text-primary italic font-serif pr-2">remembers</span> what changed.
            </h1>
            <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
              A temporal memory engine that maintains what is currently true, preserves what used to be true, and explicitly explains why.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 1 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link 
              to="/assistant" 
              className="group flex items-center justify-center space-x-2 bg-primary text-black px-8 py-4 rounded font-semibold tracking-widest uppercase w-full sm:w-auto hover:bg-white hover:text-black transition-all"
            >
              <span>Enter the Memory</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-32 px-6 bg-surface">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-5xl font-bold mb-6 leading-tight">Vector similarity <br/><span className="text-muted">isn't memory.</span></h2>
              <p className="text-gray-400 text-lg leading-relaxed mb-8">
                Semantic retrieval alone does not determine whether a fact is current, historical, superseded, or completely forgotten. Standard RAG feeds everything into the context window, forcing the LLM to guess the truth.
              </p>
              <ul className="space-y-4">
                {['Current State', 'Historical Context', 'Temporal Validity', 'Contradictions'].map((item, i) => (
                  <motion.li 
                    key={item}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center space-x-3 text-sm font-medium tracking-wide uppercase text-gray-300"
                  >
                    <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                    <span>{item}</span>
                  </motion.li>
                ))}
              </ul>
            </div>
            
            <div className="relative aspect-square md:aspect-auto md:h-[500px] border border-white/10 rounded-2xl bg-black/50 p-8 flex flex-col justify-between overflow-hidden">
              <div className="absolute top-0 right-0 p-32 bg-primary/5 blur-[100px] rounded-full pointer-events-none" />
              <div className="space-y-4">
                <div className="p-4 bg-surface rounded-xl border border-white/5 opacity-50 translate-x-4">
                  <div className="text-xs text-muted font-mono mb-2">2025 • SCORE: 0.98</div>
                  <div className="text-gray-400">I use Python.</div>
                </div>
                <div className="p-4 bg-surface rounded-xl border border-primary/30 relative z-10 shadow-2xl shadow-primary/10">
                  <div className="text-xs text-primary font-mono mb-2">NOW • SCORE: 0.98</div>
                  <div className="text-white">I use C++.</div>
                </div>
              </div>
              <div className="mt-8 text-center text-xs font-mono text-muted uppercase tracking-widest">
                Both are semantically identical.<br/>Only one is currently true.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-32 px-6">
        <div className="max-w-6xl mx-auto space-y-32">
          
          {/* Timeline Evolution */}
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="order-2 md:order-1 relative">
              <div className="absolute left-6 top-0 bottom-0 w-px bg-border" />
              <div className="space-y-8">
                {[
                  { lang: 'Python', status: 'SUPERSEDED', date: '2025' },
                  { lang: 'Java', status: 'SUPERSEDED', date: 'Early 2026' },
                  { lang: 'C++', status: 'ACTIVE', date: 'Present' }
                ].map((item, i) => (
                  <motion.div 
                    key={item.lang}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.2 }}
                    className="flex items-center pl-16 relative"
                  >
                    <div className={`absolute left-5 w-3 h-3 rounded-full border-2 bg-background -translate-x-1/2 ${item.status === 'ACTIVE' ? 'border-primary' : 'border-muted'}`} />
                    <div className={`p-6 w-full rounded-xl border ${item.status === 'ACTIVE' ? 'border-primary/30 bg-primary/5' : 'border-white/5 bg-surface/50'}`}>
                      <div className="flex justify-between items-start mb-2">
                        <span className={`text-xs font-mono tracking-wider ${item.status === 'ACTIVE' ? 'text-primary' : 'text-muted'}`}>{item.status}</span>
                        <span className="text-xs text-gray-500 font-mono">{item.date}</span>
                      </div>
                      <div className="text-xl font-bold">{item.lang}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
            <div className="order-1 md:order-2">
              <Clock className="w-12 h-12 text-primary mb-6" />
              <h3 className="text-3xl font-bold mb-4">Memory Evolves</h3>
              <p className="text-gray-400 text-lg">Current truth ≠ latest retrieved sentence. Anamnesis explicitly tracks the supersession of facts, allowing timeline reconstruction and precise historical queries.</p>
            </div>
          </div>

          {/* Contradictions */}
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <GitMerge className="w-12 h-12 text-primary mb-6" />
              <h3 className="text-3xl font-bold mb-4">Explicit Contradictions</h3>
              <p className="text-gray-400 text-lg">When you provide conflicting information ("I like cats" vs "I like dogs"), the system doesn't randomly guess. It flags the contradiction via the deterministic engine and forces the LLM to acknowledge the conflict.</p>
            </div>
            <div className="bg-surface rounded-2xl p-8 border border-white/5">
              <div className="flex justify-between items-center border-b border-white/5 pb-4 mb-4">
                <span className="text-sm font-semibold uppercase tracking-wider text-amber-500 flex items-center"><ShieldAlert size={16} className="mr-2"/> Conflict Detected</span>
              </div>
              <div className="space-y-3 font-mono text-sm">
                <div className="p-3 bg-black/40 rounded text-gray-300">User likes <span className="text-white">Dogs</span></div>
                <div className="p-3 bg-black/40 rounded text-gray-300">User likes <span className="text-white">Cats</span></div>
              </div>
            </div>
          </div>

          {/* Provenance */}
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="order-2 md:order-1 bg-surface rounded-2xl p-8 border border-white/5">
               <div className="text-xs text-muted font-mono mb-4 uppercase tracking-widest">Why this answer?</div>
               <div className="space-y-4">
                 <div className="flex items-center space-x-3 text-sm">
                   <div className="w-2 h-2 rounded-full bg-primary" />
                   <span className="font-mono text-gray-300">semantic_match</span>
                 </div>
                 <div className="flex items-center space-x-3 text-sm">
                   <div className="w-2 h-2 rounded-full bg-primary" />
                   <span className="font-mono text-gray-300">current_state_match</span>
                 </div>
                 <div className="flex items-center space-x-3 text-sm">
                   <div className="w-2 h-2 rounded-full bg-primary" />
                   <span className="font-mono text-gray-300">active_memory</span>
                 </div>
               </div>
            </div>
            <div className="order-1 md:order-2">
              <FileQuestion className="w-12 h-12 text-primary mb-6" />
              <h3 className="text-3xl font-bold mb-4">Absolute Provenance</h3>
              <p className="text-gray-400 text-lg">Every memory injected into the LLM context is accompanied by deterministic rationale. You always know exactly which memories were used and why they survived the strict filtration pipeline.</p>
            </div>
          </div>

        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6 bg-primary text-black text-center">
        <h2 className="text-4xl md:text-6xl font-bold tracking-tight mb-8">Give your assistant a memory.</h2>
        <Link 
          to="/assistant" 
          className="inline-block bg-black text-white px-10 py-5 rounded font-bold tracking-widest uppercase hover:bg-surface transition-colors"
        >
          Enter Anamnesis
        </Link>
      </section>
    </div>
  );
}

