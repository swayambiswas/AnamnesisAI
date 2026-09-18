import { Routes, Route } from 'react-router-dom';
import Landing from '@/pages/Landing';
import Assistant from '@/pages/Assistant';
import { AnimatePresence } from 'framer-motion';

function App() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/assistant" element={<Assistant />} />
      </Routes>
    </AnimatePresence>
  );
}

export default App;

