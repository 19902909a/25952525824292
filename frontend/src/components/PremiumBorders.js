import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

const Leaf = ({ delay, x, duration }) => (
  <motion.div
    initial={{ y: -20, x, rotate: 0, opacity: 0 }}
    animate={{ 
      y: ['0vh', '100vh'], 
      x: [x, x + 50, x - 50, x + 20], 
      rotate: [0, 180, 360],
      opacity: [0, 1, 1, 0]
    }}
    transition={{ duration, repeat: Infinity, delay, ease: "linear" }}
    className="absolute top-0 w-3 h-3 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 blur-[1px]"
    style={{ borderBottomRightRadius: '0px' }}
  />
);

const Particle = ({ color, duration, delay, x, y }) => (
  <motion.div
    initial={{ x, y, scale: 0, opacity: 0 }}
    animate={{ 
      y: [y, y - 100], 
      x: [x, x + (Math.random() * 40 - 20)],
      scale: [0, 1.5, 0],
      opacity: [0, 0.8, 0]
    }}
    transition={{ duration, repeat: Infinity, delay, ease: "easeInOut" }}
    className={`absolute w-1.5 h-1.5 rounded-full blur-[2px] ${color}`}
  />
);

const Cloud = ({ delay, y, duration, scale }) => (
  <motion.div
    initial={{ x: '-10%', opacity: 0.2 }}
    animate={{ x: '110%', opacity: [0.1, 0.4, 0.1] }}
    transition={{ duration, repeat: Infinity, delay, ease: "linear" }}
    className="absolute bg-white/10 blur-3xl rounded-full"
    style={{ top: y, width: 300 * scale, height: 100 * scale }}
  />
);

export const PremiumBorders = () => {
  const leaves = useMemo(() => Array.from({ length: 15 }).map((_, i) => ({
    id: `leaf-${i}`,
    x: Math.random() * 100,
    delay: Math.random() * 10,
    duration: 10 + Math.random() * 10
  })), []);

  const particles = useMemo(() => Array.from({ length: 25 }).map((_, i) => ({
    id: `part-${i}`,
    x: Math.random() * 100,
    y: Math.random() * 100 + 50,
    delay: Math.random() * 5,
    duration: 3 + Math.random() * 4,
    color: i % 2 === 0 ? 'bg-cyan-400' : 'bg-fuchsia-400'
  })), []);

  return (
    <div className="fixed inset-0 pointer-events-none z-[-5] overflow-hidden bg-[#050914]">
      {/* Ciel & Nuages (Haut) */}
      <div className="absolute top-0 left-0 right-0 h-[40vh] bg-gradient-to-b from-blue-900/20 via-indigo-900/10 to-transparent">
        <Cloud delay={0} y="5%" duration={40} scale={1} />
        <Cloud delay={15} y="15%" duration={55} scale={1.5} />
        <Cloud delay={5} y="10%" duration={45} scale={0.8} />
      </div>

      {/* Montagne, Marmottes & Ruisseau (Bord Gauche) */}
      <div className="absolute top-0 bottom-0 left-0 w-[15vw] min-w-[200px] border-r border-white/5 bg-[linear-gradient(90deg,rgba(16,185,129,0.05)_0%,transparent_100%)]">
        {/* Silhouette de montagne */}
        <div className="absolute top-1/4 -left-20 w-64 h-96 bg-emerald-900/20 rounded-[100px] rotate-45 blur-2xl" />
        <div className="absolute top-1/2 -left-10 w-48 h-72 bg-teal-800/20 rounded-[80px] -rotate-12 blur-xl" />
        {/* Ruisseau animée */}
        <motion.div 
          animate={{ backgroundPosition: ['0% 0%', '0% 100%'] }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          className="absolute top-0 bottom-0 right-10 w-8 blur-md mix-blend-screen opacity-40"
          style={{ backgroundImage: 'linear-gradient(180deg, transparent, #38bdf8, transparent)', backgroundSize: '100% 200%' }}
        />
        {/* Chutes de feuilles (Vent) */}
        {leaves.map(l => <Leaf key={l.id} {...l} x={`${l.x}%`} />)}
      </div>

      {/* Ville Cyberpunk & Jardin Public (Bord Droit) */}
      <div className="absolute top-0 bottom-0 right-0 w-[15vw] min-w-[200px] border-l border-white/5 bg-[linear-gradient(-90deg,rgba(236,72,153,0.05)_0%,transparent_100%)]">
        {/* Gratte-ciels (blocs) */}
        <div className="absolute bottom-0 -right-10 w-32 h-[60vh] bg-indigo-950/30 rounded-t-3xl blur-xl" />
        <div className="absolute bottom-0 right-10 w-24 h-[40vh] bg-fuchsia-950/20 rounded-t-2xl blur-lg" />
        {/* Routes lumineuses (Trafic) */}
        <motion.div 
          animate={{ y: ['100vh', '-20vh'] }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          className="absolute right-20 w-1 h-32 bg-gradient-to-t from-transparent via-cyan-400 to-transparent blur-[2px]"
        />
        <motion.div 
          animate={{ y: ['-20vh', '100vh'] }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear", delay: 1.5 }}
          className="absolute right-12 w-1 h-32 bg-gradient-to-b from-transparent via-pink-500 to-transparent blur-[2px]"
        />
        {/* Jardin public (particules d'énergie) */}
        <div className="absolute bottom-20 right-0 left-0 h-64 bg-emerald-500/5 blur-3xl rounded-full" />
        {particles.map(p => <Particle key={p.id} {...p} x={`${p.x}%`} y={`${p.y}%`} />)}
      </div>

      {/* Herbes & Vent (Bas) */}
      <div className="absolute bottom-0 left-0 right-0 h-[20vh] bg-gradient-to-t from-green-950/20 to-transparent flex items-end justify-around overflow-hidden px-[10vw]">
        {Array.from({ length: 50 }).map((_, i) => (
          <motion.div
            key={`grass-${i}`}
            animate={{ rotate: [-5, 10, -5] }}
            transition={{ duration: 2 + Math.random() * 2, repeat: Infinity, ease: "easeInOut", delay: Math.random() }}
            className="w-1 bg-gradient-to-t from-emerald-800 to-green-500/50 rounded-t-full origin-bottom blur-[1px]"
            style={{ height: `${20 + Math.random() * 60}px`, opacity: 0.3 + Math.random() * 0.5 }}
          />
        ))}
      </div>
    </div>
  );
};
