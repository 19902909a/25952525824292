import React from 'react';
import { motion } from 'framer-motion';

export const BreakoutDecorations = () => {
  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      {/* 3. Piliers de lumière orbitaux */}
      <div className="absolute top-0 bottom-0 left-0 w-32 bg-gradient-to-r from-cyan-500/10 to-transparent mix-blend-screen animate-pulse" style={{ filter: 'blur(20px)' }} />
      <div className="absolute top-0 bottom-0 right-0 w-32 bg-gradient-to-l from-fuchsia-500/10 to-transparent mix-blend-screen animate-pulse" style={{ filter: 'blur(20px)' }} />

      {/* 7. Lame d'épée en filigrane (Katana glassmorphism) */}
      <div 
        className="absolute top-[-10%] -left-[10%] w-[120%] h-16 bg-white/[0.01] backdrop-blur-md border-t border-b border-white/10 mix-blend-overlay"
        style={{ transform: 'rotate(25deg)', boxShadow: '0 0 50px rgba(255,255,255,0.05)' }}
      />
    </div>
  );
};

export const ShurikenDeco = ({ className }) => (
  <svg className={`pointer-events-none absolute ${className} drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]`} width="80" height="80" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M50 0L55 45L100 50L55 55L50 100L45 55L0 50L45 45L50 0Z" fill="url(#shuriken-grad)" />
    <circle cx="50" cy="50" r="10" fill="#0f172a" stroke="url(#shuriken-grad)" strokeWidth="2"/>
    <defs>
      <linearGradient id="shuriken-grad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
        <stop stopColor="#e2e8f0" />
        <stop offset="1" stopColor="#94a3b8" />
      </linearGradient>
    </defs>
  </svg>
);

export const FloatingCardsDeco = () => (
  <div className="absolute -right-16 top-10 pointer-events-none w-32 h-40 hidden lg:block" style={{ perspective: '1000px' }}>
    <motion.div 
      animate={{ y: [0, -10, 0], rotateZ: [10, 12, 10] }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      className="absolute inset-0 bg-[url('https://placehold.co/200x300/1a1a2e/cyan?text=Card')] bg-cover rounded-xl border border-cyan-400/50 shadow-[0_0_30px_rgba(34,211,238,0.3)]"
      style={{ transform: 'rotateY(-20deg) rotateX(10deg)' }}
    />
    <motion.div 
      animate={{ y: [0, 10, 0], rotateZ: [-5, -7, -5] }}
      transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
      className="absolute -bottom-10 -left-10 w-24 h-32 bg-[url('https://placehold.co/200x300/1a1a2e/fuchsia?text=Rare')] bg-cover rounded-xl border border-fuchsia-400/50 shadow-[0_0_30px_rgba(217,70,239,0.3)]"
      style={{ transform: 'rotateY(15deg) rotateX(-5deg)' }}
    />
  </div>
);
