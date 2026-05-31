"use client";

import { motion } from "framer-motion";
import { useTheme } from "next-themes";
import { Brain, Moon, Sun, Target, Swords, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

export default function Home() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <div className="flex flex-col min-h-screen relative overflow-hidden">
      {/* Navbar Minimalista */}
      <nav className="flex items-center justify-between px-8 py-4 z-50">
        <div className="flex items-center gap-2 text-primary">
          <Brain className="w-6 h-6" />
          <span className="font-bold text-lg tracking-tight">EiraLearn</span>
        </div>
        <div>
          {mounted && (
            <Button variant="ghost" onClick={toggleTheme} className="rounded-full w-10 h-10 p-0">
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>
          )}
        </div>
      </nav>

      {/* Hero Section con Animaciones */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="text-center max-w-2xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-elevated border border-border text-sm font-medium text-foreground-muted mb-8 shadow-sm">
            <span className="flex w-2 h-2 rounded-full bg-success"></span>
            MEXT Preparation Protocol Active
          </div>

          <h1 className="text-5xl sm:text-7xl font-bold tracking-tight text-foreground mb-6">
            Gimnasio <span className="text-accent">Cognitivo</span>
          </h1>

          <p className="text-lg text-foreground-muted mb-10 w-full max-w-xl mx-auto leading-relaxed">
            Entrenamiento quirúrgico de matemáticas e idiomas para asegurar tu beca. Analítica profunda, simulación hiperrealista.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button className="h-12 px-8 text-base shadow-lg shadow-primary/20">
              <Swords className="w-5 h-5 mr-2" />
              Modo Colisión
            </Button>
            <Button variant="outline" className="h-12 px-8 text-base">
              <Target className="w-5 h-5 mr-2" />
              Diagnóstico
            </Button>
          </div>
        </motion.div>
      </main>

      {/* Grid de Fondo decorativo "Scholar's Desk" */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-30 dark:opacity-20 flex items-center justify-center">
        <div className="w-[800px] h-[800px] bg-primary blur-[160px] opacity-10 rounded-full center absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
      </div>
    </div>
  );
}
