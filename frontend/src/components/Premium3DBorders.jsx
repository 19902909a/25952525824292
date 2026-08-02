import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, Float, Sparkles, MeshTransmissionMaterial, Stars } from '@react-three/drei';
import * as THREE from 'three';

// --- Left Border: Mountain, Stream, Nature ---
const NatureBorder = () => {
  const streamRef = useRef();
  useFrame((state) => {
    if (streamRef.current) {
      streamRef.current.position.z = (state.clock.elapsedTime * 0.5) % 2;
    }
  });

  return (
    <group position={[-12, -2, -5]}>
      <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
        {/* Mountain */}
        <mesh position={[-2, 6, -10]} rotation={[0, Math.PI / 4, 0]}>
          <coneGeometry args={[10, 15, 4]} />
          <meshStandardMaterial color="#0f766e" roughness={0.8} />
        </mesh>
        {/* Trees */}
        <mesh position={[1, -1, -5]}>
          <sphereGeometry args={[2.5, 16, 16]} />
          <meshStandardMaterial color="#10b981" roughness={0.9} emissive="#065f46" emissiveIntensity={0.5} />
        </mesh>
        <mesh position={[-2, -2, -2]}>
          <sphereGeometry args={[1.8, 16, 16]} />
          <meshStandardMaterial color="#34d399" roughness={0.9} emissive="#047857" emissiveIntensity={0.5} />
        </mesh>
        {/* Stream */}
        <mesh position={[4, -5, -3]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[5, 20]} />
          <MeshTransmissionMaterial 
            color="#38bdf8" 
            resolution={512} 
            thickness={2} 
            roughness={0.1} 
            transmission={0.9} 
            ior={1.5}
            emissive="#0ea5e9"
            emissiveIntensity={0.8}
          />
        </mesh>
        {/* Animated Stream Water Surface */}
        <mesh ref={streamRef} position={[4, -4.8, -3]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[5, 20, 10, 10]} />
          <meshStandardMaterial color="#bae6fd" wireframe transparent opacity={0.6} />
        </mesh>
      </Float>
      {/* Leaves/Fireflies */}
      <Sparkles count={80} scale={20} size={8} speed={0.4} color="#86efac" position={[2, 2, -2]} />
    </group>
  );
};

// --- Right Border: Cyber City, Park, Roads ---
const CityBorder = () => {
  const trafficRef1 = useRef();
  const trafficRef2 = useRef();

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (trafficRef1.current) trafficRef1.current.position.z = (t * 15) % 40 - 20;
    if (trafficRef2.current) trafficRef2.current.position.z = -(t * 20) % 40 + 20;
  });

  return (
    <group position={[12, -2, -5]}>
      <Float speed={1} rotationIntensity={0.1} floatIntensity={0.2}>
        {/* Skyscrapers */}
        <mesh position={[2, 4, -10]}>
          <boxGeometry args={[4, 25, 4]} />
          <meshStandardMaterial color="#3730a3" roughness={0.2} metalness={0.8} emissive="#1e1b4b" emissiveIntensity={0.5} />
        </mesh>
        <mesh position={[6, 2, -5]}>
          <boxGeometry args={[3, 18, 3]} />
          <meshStandardMaterial color="#4f46e5" roughness={0.2} metalness={0.8} emissive="#312e81" emissiveIntensity={0.5} />
        </mesh>
        <mesh position={[0, -1, -2]}>
          <boxGeometry args={[2, 12, 2]} />
          <meshStandardMaterial color="#7c3aed" roughness={0.3} metalness={0.7} emissive="#4c1d95" emissiveIntensity={0.6} />
        </mesh>

        {/* Public Garden (Park) */}
        <mesh position={[-4, -7, 2]}>
          <boxGeometry args={[8, 1, 8]} />
          <meshStandardMaterial color="#064e3b" emissive="#022c22" emissiveIntensity={0.5} />
        </mesh>
        <mesh position={[-4, -6, 0]}>
          <sphereGeometry args={[2, 16, 16]} />
          <meshStandardMaterial color="#10b981" emissive="#047857" emissiveIntensity={0.4} />
        </mesh>

        {/* Fountain */}
        <mesh position={[-4, -6, 4]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1.5, 0.3, 16, 32]} />
          <meshStandardMaterial color="#94a3b8" emissive="#64748b" emissiveIntensity={0.5} />
        </mesh>
        <mesh position={[-4, -4.5, 4]}>
          <cylinderGeometry args={[0.2, 0.8, 3, 16]} />
          <MeshTransmissionMaterial color="#7dd3fc" transmission={0.9} emissive="#0284c7" emissiveIntensity={0.6} />
        </mesh>

        {/* Traffic / Roads */}
        <mesh position={[-6, -8, 0]}>
          <boxGeometry args={[2, 0.1, 40]} />
          <meshStandardMaterial color="#0f172a" />
        </mesh>
        <mesh ref={trafficRef1} position={[-6.5, -7.8, 0]}>
          <boxGeometry args={[0.3, 0.3, 3]} />
          <meshBasicMaterial color="#ef4444" />
        </mesh>
        <mesh ref={trafficRef2} position={[-5.5, -7.8, 0]}>
          <boxGeometry args={[0.3, 0.3, 3]} />
          <meshBasicMaterial color="#2dd4bf" />
        </mesh>
      </Float>
      {/* Neon Particles */}
      <Sparkles count={80} scale={20} size={6} speed={0.8} color="#f472b6" position={[-2, 2, -2]} />
    </group>
  );
};

// --- Bottom Border: Wind & Grass ---
const Grass = () => {
  const grassRef = useRef();
  
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const count = 200;

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (grassRef.current) {
      for (let i = 0; i < count; i++) {
        const x = (i % 40) - 20;
        const z = Math.floor(i / 40) - 2;
        // Wind effect
        const rotX = Math.sin(t + x * 0.5) * 0.2;
        
        dummy.position.set(x * 1.5, -12, z * 2);
        dummy.rotation.set(rotX, 0, 0);
        dummy.scale.set(0.1, 1 + Math.random(), 0.1);
        dummy.updateMatrix();
        grassRef.current.setMatrixAt(i, dummy.matrix);
      }
      grassRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <instancedMesh ref={grassRef} args={[null, null, count]}>
      <coneGeometry args={[1, 4, 4]} />
      <meshStandardMaterial color="#059669" />
    </instancedMesh>
  );
};

export const Premium3DBorders = () => {
  return (
    <div className="fixed inset-0 z-[-1] pointer-events-none">
      <Canvas camera={{ position: [0, 0, 10], fov: 75 }}>
        <ambientLight intensity={1.5} />
        <directionalLight position={[10, 20, 10]} intensity={2.5} color="#fbcfe8" />
        <directionalLight position={[-10, 20, -10]} intensity={2.5} color="#38bdf8" />
        <pointLight position={[0, 10, 0]} intensity={1} color="#ffffff" />
        
        <NatureBorder />
        <CityBorder />
        <Grass />
        
        {/* Weather / Sky */}
        <Stars radius={50} depth={50} count={3000} factor={6} saturation={0.5} fade speed={1} />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
};
