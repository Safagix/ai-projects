"use client";

import { useEffect, useRef } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
import * as THREE from "three";
import { useI18n } from "@/lib/i18n";

export function HeroSection() {
  const { t } = useI18n();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 80, damping: 20 });
  const springY = useSpring(mouseY, { stiffness: 80, damping: 20 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const isMobile = typeof window !== "undefined" && window.innerWidth < 768;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1 : 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.set(0, 0, 8);

    const geo = new THREE.IcosahedronGeometry(2, isMobile ? 2 : 4);
    const mat = new THREE.ShaderMaterial({
      vertexShader: `uniform float uTime; varying vec3 vNormal; varying vec3 vPosition;
        void main() { vec3 pos = position; pos.z += sin(pos.x*3.0+uTime)*0.12; pos.y += cos(pos.z*3.0+uTime)*0.12;
        vNormal = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(pos,1.0); vPosition = mv.xyz;
        gl_Position = projectionMatrix*mv; }`,
      fragmentShader: `varying vec3 vNormal; varying vec3 vPosition;
        void main() { vec3 d = normalize(-vPosition); float f = pow(1.0-abs(dot(d,vNormal)),3.0);
        gl_FragColor = vec4(mix(vec3(0.05,0.12,0.08),vec3(0.2,0.65,0.4),f),1.0); }`,
      uniforms: { uTime: { value: 0 } },
      transparent: true,
    });
    const mesh = new THREE.Mesh(geo, mat);
    scene.add(mesh);

    const pCount = isMobile ? 80 : 400;
    const pGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(pCount * 3);
    for (let i = 0; i < pCount; i++) {
      const r = 3 + Math.random() * 3;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    pGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const pMat = new THREE.PointsMaterial({ color: 0x10b981, size: 0.02, transparent: true, opacity: 0.6 });
    const particles = new THREE.Points(pGeo, pMat);
    scene.add(particles);

    const clock = new THREE.Clock();
    let raf: number;
    const animate = () => {
      const elapsed = clock.getElapsedTime();
      mat.uniforms.uTime.value = elapsed;
      const tx = springX.get();
      const ty = springY.get();
      mesh.rotation.y += (tx * Math.PI - mesh.rotation.y) * 0.03;
      mesh.rotation.x += (ty * 0.5 - mesh.rotation.x) * 0.03;
      particles.rotation.y += 0.0005;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(animate);
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;
      if (w === 0 || h === 0) return;
      renderer.setSize(w, h, false);
      camera.aspect = w / Math.max(h, 1);
      camera.updateProjectionMatrix();
    };
    resize();
    window.addEventListener("resize", resize);
    animate();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      scene.traverse((c) => {
        if (c instanceof THREE.Mesh || c instanceof THREE.Points) {
          c.geometry.dispose();
          (c.material as THREE.Material).dispose();
        }
      });
      renderer.dispose();
    };
  }, [springX, springY]);

  const handleMouse = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    mouseX.set(((e.clientX - rect.left) / rect.width) * 2 - 1);
    mouseY.set(-((e.clientY - rect.top) / rect.height) * 2 + 1);
  };

  return (
    <section className="relative min-h-[100dvh] w-full overflow-hidden bg-[#050505]" onMouseMove={handleMouse}>
      <div className="mx-auto flex max-w-7xl flex-col md:flex-row items-center gap-12 px-4 py-24 md:py-0 md:px-8">
        <motion.div
          initial={{ opacity: 0, y: 32, filter: "blur(8px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 0.8, ease: [0.32, 0.72, 0, 1] }}
          className="flex w-full md:w-1/2 flex-col items-start gap-6"
        >
          <div className="flex h-[88px] w-[88px] items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.02] text-2xl font-semibold text-emerald-400" style={{ fontFamily: "var(--font-display)" }}>
            SX
          </div>
          <h1 className="text-4xl md:text-6xl tracking-tighter leading-[0.9] text-white" style={{ fontFamily: "var(--font-display)" }}>
            {t("hero.name")}
          </h1>
          <span className="rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-emerald-400 font-medium">
            {t("hero.role")}
          </span>
          <p className="max-w-[42ch] text-lg leading-relaxed text-slate-400">
            {t("hero.edge")}
          </p>
          <a
            href="#projects"
            className="group inline-flex items-center gap-2 rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-black transition-all duration-150 ease hover:scale-[0.98] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050505]"
          >
            {t("hero.cta")}
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-black/15 transition-transform duration-300 ease-out group-hover:translate-x-0.5 group-hover:-translate-y-px">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 17L17 7"/><path d="M7 7h10v10"/></svg>
            </span>
          </a>
        </motion.div>
        <div className="relative h-[50vh] w-full md:h-screen md:w-1/2">
          <canvas ref={canvasRef} className="h-full w-full" />
        </div>
      </div>
    </section>
  );
}
