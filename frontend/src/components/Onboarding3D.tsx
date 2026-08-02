import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, ContactShadows, Environment, Stars } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, ArrowRight, Shield, Cpu, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import * as THREE from 'three';

// ---------------------------------------------------------
// 1. LOVA-BOT (Friendly, Nature/Plaza)
// ---------------------------------------------------------
const LovaBotEnv = () => {
  return (
    <group position={[0, -2, 0]}>
      {/* Floor */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="#a7f3d0" roughness={1} />
      </mesh>
      
      {/* Fountain Base */}
      <mesh receiveShadow castShadow position={[0, 0.2, 0]}>
        <cylinderGeometry args={[2, 2.2, 0.4, 32]} />
        <meshStandardMaterial color="#e2e8f0" />
      </mesh>
      {/* Water */}
      <mesh position={[0, 0.4, 0]}>
        <cylinderGeometry args={[1.9, 1.9, 0.1, 32]} />
        <meshPhysicalMaterial color="#38bdf8" transmission={0.9} opacity={1} transparent roughness={0.1} />
      </mesh>

      {/* Trees */}
      {[-3, 3].map((x, i) => (
        <group key={i} position={[x, 0, -3]}>
          <mesh position={[0, 1, 0]} castShadow>
            <cylinderGeometry args={[0.2, 0.2, 2]} />
            <meshStandardMaterial color="#78350f" />
          </mesh>
          <mesh position={[0, 2.5, 0]} castShadow>
            <coneGeometry args={[1.5, 3, 16]} />
            <meshStandardMaterial color="#22c55e" />
          </mesh>
        </group>
      ))}
    </group>
  );
};

const LovaBot = ({ isSpeaking }) => {
  const headRef = useRef(null);
  const leftArmRef = useRef(null);
  const rightArmRef = useRef(null);
  const bodyRef = useRef(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (headRef.current) {
      headRef.current.rotation.y = Math.sin(t * 2) * 0.2;
      headRef.current.position.y = 1.2 + (isSpeaking ? Math.abs(Math.sin(t * 10)) * 0.05 : 0);
    }
    // Arm swinging (walking motion)
    if (leftArmRef.current) leftArmRef.current.rotation.x = Math.sin(t * 4) * 0.5;
    if (rightArmRef.current) rightArmRef.current.rotation.x = -Math.sin(t * 4) * 0.5;
    // Body bouncing
    if (bodyRef.current) bodyRef.current.position.y = Math.abs(Math.sin(t * 4)) * 0.1;
  });

  return (
    <group ref={bodyRef} position={[0, 0, 0]}>
      {/* Body */}
      <mesh position={[0, 0.5, 0]} castShadow>
        <boxGeometry args={[1, 1.2, 0.8]} />
        <meshStandardMaterial color="#ffffff" roughness={0.3} metalness={0.2} />
      </mesh>
      {/* Screen */}
      <mesh position={[0, 0.5, 0.41]}>
        <planeGeometry args={[0.6, 0.6]} />
        <meshBasicMaterial color="#38bdf8" />
      </mesh>
      
      {/* Arms */}
      <group ref={leftArmRef} position={[-0.6, 0.8, 0]}>
        <mesh position={[0, -0.4, 0]} castShadow>
          <cylinderGeometry args={[0.12, 0.1, 0.8]} />
          <meshStandardMaterial color="#cbd5e1" />
        </mesh>
      </group>
      <group ref={rightArmRef} position={[0.6, 0.8, 0]}>
        <mesh position={[0, -0.4, 0]} castShadow>
          <cylinderGeometry args={[0.12, 0.1, 0.8]} />
          <meshStandardMaterial color="#cbd5e1" />
        </mesh>
      </group>

      {/* Head */}
      <group ref={headRef} position={[0, 1.2, 0]}>
        <mesh castShadow>
          <sphereGeometry args={[0.6, 32, 32]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>
        <mesh position={[-0.2, 0.1, 0.55]}>
          <circleGeometry args={[0.1]} />
          <meshBasicMaterial color={isSpeaking ? "#fbbf24" : "#10b981"} />
        </mesh>
        <mesh position={[0.2, 0.1, 0.55]}>
          <circleGeometry args={[0.1]} />
          <meshBasicMaterial color={isSpeaking ? "#fbbf24" : "#10b981"} />
        </mesh>
      </group>
    </group>
  );
};

// ---------------------------------------------------------
// 2. LOVA-AI (Advanced, Sleek, Glowing Nature)
// ---------------------------------------------------------
const LovaAIEnv = () => {
  return (
    <group position={[0, -2, 0]}>
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="#0f172a" roughness={0.8} />
      </mesh>
      
      {/* Glowing Fountain */}
      <mesh receiveShadow position={[0, 0.2, 0]}>
        <cylinderGeometry args={[2.5, 3, 0.4, 6]} />
        <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[0, 0.4, 0]}>
        <cylinderGeometry args={[2.4, 2.4, 0.1, 6]} />
        <meshBasicMaterial color="#06b6d4" />
      </mesh>

      {/* Crystal Trees */}
      {[-4, 4].map((x, i) => (
        <group key={i} position={[x, 1.5, -4]}>
          <mesh castShadow>
            <octahedronGeometry args={[1, 0]} />
            <meshPhysicalMaterial color="#38bdf8" transmission={1} opacity={0.8} transparent metalness={0.5} roughness={0.1} />
          </mesh>
        </group>
      ))}
    </group>
  );
};

const LovaAI = ({ isSpeaking }) => {
  const ringRef = useRef(null);
  const coreRef = useRef(null);
  const bodyRef = useRef(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (ringRef.current) {
      ringRef.current.rotation.x = t * 1.5;
      ringRef.current.rotation.y = t * 0.8;
      ringRef.current.rotation.z = t * 0.5;
    }
    // Hovering up and down smoothly
    if (bodyRef.current) {
      bodyRef.current.position.y = 0.5 + Math.sin(t * 1.5) * 0.3;
    }
    // Pulsing core effect when speaking
    if (coreRef.current && isSpeaking) {
      coreRef.current.scale.setScalar(1 + Math.sin(t * 15) * 0.1);
    }
  });

  return (
    <group ref={bodyRef} position={[0, 0.5, 0]}>
      {/* Sleek Body */}
      <mesh ref={coreRef} position={[0, 0, 0]} castShadow>
        <capsuleGeometry args={[0.5, 1, 4, 16]} />
        <meshStandardMaterial color="#1e293b" metalness={0.9} roughness={0.1} />
      </mesh>
      {/* Glowing Visor */}
      <mesh position={[0, 0.6, 0.45]} rotation={[0, 0, Math.PI / 2]}>
        <capsuleGeometry args={[0.1, 0.4, 4, 16]} />
        <meshBasicMaterial color={isSpeaking ? "#22d3ee" : "#3b82f6"} />
      </mesh>
      {/* Floating Rings */}
      <group ref={ringRef}>
        <mesh>
          <torusGeometry args={[1.2, 0.02, 16, 100]} />
          <meshBasicMaterial color="#0ea5e9" />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1.5, 0.02, 16, 100]} />
          <meshBasicMaterial color="#8b5cf6" />
        </mesh>
      </group>
    </group>
  );
};

// ---------------------------------------------------------
// 3. LOVA KING AI (Majestic, Fortress, Powerful)
// ---------------------------------------------------------
const LovaKingEnv = () => {
  return (
    <group position={[0, -2, 0]}>
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 30]} />
        <meshStandardMaterial color="#000000" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Fortress Pedestal */}
      <mesh receiveShadow castShadow position={[0, 0.5, 0]}>
        <boxGeometry args={[4, 1, 4]} />
        <meshStandardMaterial color="#111111" metalness={0.9} roughness={0.1} />
      </mesh>
      {/* Neon border */}
      <mesh position={[0, 1.01, 0]}>
        <boxGeometry args={[3.8, 0.05, 3.8]} />
        <meshBasicMaterial color="#fbbf24" />
      </mesh>

      {/* Monolithic Pillars */}
      {[-4, 4].map((x, i) => (
        <group key={i} position={[x, 4, -4]}>
          <mesh castShadow>
            <boxGeometry args={[1, 8, 1]} />
            <meshStandardMaterial color="#171717" metalness={1} roughness={0.1} />
          </mesh>
          <mesh position={[0, 0, 0.51]}>
            <planeGeometry args={[0.2, 6]} />
            <meshBasicMaterial color="#ef4444" />
          </mesh>
        </group>
      ))}
    </group>
  );
};

const LovaKingAI = ({ isSpeaking }) => {
  const headRef = useRef(null);
  const shouldersRef = useRef(null);
  const staffRef = useRef(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (headRef.current) {
      // Majestic slow nod and breathing
      headRef.current.position.y = 2.5 + Math.sin(t * 1.5) * 0.05;
      headRef.current.rotation.y = Math.sin(t * 0.5) * 0.3; // Look around
      if (isSpeaking) headRef.current.rotation.x = Math.sin(t * 8) * 0.05;
    }
    // Powerful chest breathing
    if (shouldersRef.current) {
      const breath = 1 + Math.sin(t * 1.5) * 0.03;
      shouldersRef.current.scale.set(breath, 1, breath);
    }
    // Hovering mystical orb/staff
    if (staffRef.current) {
      staffRef.current.position.y = 1 + Math.sin(t * 2) * 0.3;
      staffRef.current.rotation.y += 0.02;
      staffRef.current.rotation.x = Math.sin(t) * 0.2;
    }
  });

  return (
    <group position={[0, 1, 0]}>
      {/* Massive Body */}
      <group ref={shouldersRef}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <cylinderGeometry args={[0.8, 1.2, 2, 8]} />
          <meshStandardMaterial color="#09090b" metalness={1} roughness={0.2} />
        </mesh>
        {/* Armor Plates */}
        <mesh position={[0, 0.5, 0]} castShadow>
          <cylinderGeometry args={[0.9, 1.3, 1.8, 4]} />
          <meshStandardMaterial color="#fbbf24" metalness={1} roughness={0.3} wireframe />
        </mesh>
      </group>

      {/* Floating Power Orb */}
      <mesh ref={staffRef} position={[1.5, 1, 0.5]} castShadow>
        <octahedronGeometry args={[0.3, 0]} />
        <meshPhysicalMaterial color="#ef4444" emissive="#ef4444" emissiveIntensity={2} transmission={0.9} roughness={0.1} />
      </mesh>
      
      {/* Majestic Head */}
      <group ref={headRef} position={[0, 2.5, 0]}>
        <mesh castShadow>
          <octahedronGeometry args={[0.6, 1]} />
          <meshStandardMaterial color="#262626" metalness={0.8} />
        </mesh>
        {/* Crown */}
        <mesh position={[0, 0.6, 0]}>
          <coneGeometry args={[0.8, 0.5, 4]} />
          <meshBasicMaterial color="#fbbf24" />
        </mesh>
        {/* Piercing Eye */}
        <mesh position={[0, 0, 0.55]}>
          <planeGeometry args={[0.4, 0.1]} />
          <meshBasicMaterial color={isSpeaking ? "#ef4444" : "#b91c1c"} />
        </mesh>
      </group>
    </group>
  );
};

// ---------------------------------------------------------
// ONBOARDING COMPONENT
// ---------------------------------------------------------

const stepsData = [
  {
    name: "Lova-Bot",
    icon: <Bot className="w-5 h-5" />,
    color: "from-green-400 to-emerald-600",
    text: "Salut ! Je suis Lova-Bot. Je suis ton guide de base pour explorer la place principale et découvrir les fonctionnalités essentielles de Lovanet.",
    Component: LovaBot,
    Env: LovaBotEnv
  },
  {
    name: "Lova-AI",
    icon: <Cpu className="w-5 h-5" />,
    color: "from-sky-400 to-indigo-500",
    text: "Je suis Lova-AI, l'intelligence évoluée. Mes capacités avancées te permettent de personnaliser ton expérience, d'obtenir des recommandations précises et de naviguer dans l'univers technologique de Lovanet.",
    Component: LovaAI,
    Env: LovaAIEnv
  },
  {
    name: "Lova King AI",
    icon: <Shield className="w-5 h-5" />,
    color: "from-amber-400 to-red-600",
    text: "Moi, je suis Lova King AI. Je garde la forteresse moderne et protège les valeurs fortes de notre écosystème. Avec moi, tes données et tes succès sont en sécurité absolue.",
    Component: LovaKingAI,
    Env: LovaKingEnv
  }
];

export const Onboarding3D = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [step, setStep] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(true);

  useEffect(() => {
    const hasSeen = localStorage.getItem("lovanet_onboarding_seen_v4");
    if (!hasSeen) {
      setTimeout(() => setIsVisible(true), 1500);
    }
  }, []);

  useEffect(() => {
    setIsSpeaking(true);
    const timer = setTimeout(() => setIsSpeaking(false), 3000);
    return () => clearTimeout(timer);
  }, [step]);

  const handleNext = () => {
    if (step < stepsData.length - 1) {
      setStep(s => s + 1);
    } else {
      handleClose();
    }
  };

  const handleClose = () => {
    setIsVisible(false);
    localStorage.setItem("lovanet_onboarding_seen_v4", "true");
  };

  if (!isVisible) return null;

  const currentData = stepsData[step];
  const CurrentAvatar = currentData.Component;
  const CurrentEnv = currentData.Env;

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-md"
      >
        <div className="relative w-full max-w-5xl h-[85vh] flex flex-col items-center justify-center">
          
          <button 
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 bg-white/10 rounded-full hover:bg-white/20 transition text-white z-10"
          >
            <X className="w-6 h-6" />
          </button>

          <div className="w-full h-3/4 rounded-3xl overflow-hidden relative border border-white/10 shadow-2xl">
            <Canvas camera={{ position: [0, 1.5, 6], fov: 50 }}>
              <color attach="background" args={[step === 2 ? '#050505' : '#e0f2fe']} />
              <ambientLight intensity={step === 2 ? 0.5 : 1} />
              <directionalLight position={[10, 10, 5]} intensity={step === 2 ? 1 : 2} color={step === 2 ? "#fbbf24" : "#ffffff"} castShadow />
              
              {step === 2 && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />}
              
              {/* <Environment preset={step === 2 ? "night" : "city"} /> */ }
              
              <CurrentEnv />
              
              <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
                <CurrentAvatar isSpeaking={isSpeaking} />
              </Float>
              
              <OrbitControls enableZoom={false} maxPolarAngle={Math.PI / 2 + 0.1} minPolarAngle={Math.PI / 3} autoRotate autoRotateSpeed={2} />
            </Canvas>
          </div>

          <motion.div 
            key={step}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="mt-6 p-6 bg-white/10 border border-white/20 rounded-2xl backdrop-blur-md w-full max-w-3xl text-center"
          >
            <h3 className={`text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r ${currentData.color} mb-3 flex items-center justify-center gap-3`}>
              <span className={`text-${currentData.color.split(' ')[1].replace('to-', '')}`}>{currentData.icon}</span>
              {currentData.name}
            </h3>
            <p className="text-lg text-slate-200 mb-6 leading-relaxed px-4">
              {currentData.text}
            </p>
            
            <div className="flex justify-between items-center w-full px-4">
              <div className="flex gap-3">
                {stepsData.map((_, i) => (
                  <div key={i} className={`w-3 h-3 rounded-full transition-all duration-300 ${i === step ? 'bg-gradient-to-r ' + currentData.color + ' scale-125' : 'bg-white/20'}`} />
                ))}
              </div>
              <Button onClick={handleNext} className={`rounded-full bg-gradient-to-r ${currentData.color} border-none font-bold text-white shadow-lg hover:scale-105 transition-transform`}>
                {step < stepsData.length - 1 ? "Découvrir la suite" : "Entrer dans Lovanet"} <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
