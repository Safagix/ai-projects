"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export function Eyebrow({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.span
      initial={{ opacity: 0, y: 8 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
      className={cn("inline-block rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-emerald-400 font-medium", className)}
    >
      {children}
    </motion.span>
  );
}

export function SectionHeadline({ children }: { children: React.ReactNode }) {
  return (
    <motion.h2
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: 0.1, ease: [0.32, 0.72, 0, 1] }}
      className="mt-4 text-3xl md:text-5xl tracking-tight leading-[0.95] text-white"
      style={{ fontFamily: "var(--font-display)" }}
    >
      {children}
    </motion.h2>
  );
}

interface SectionProps {
  id: string;
  eyebrow: string;
  headline: string;
  children: React.ReactNode;
}

export function Section({ id, eyebrow, headline, children }: SectionProps) {
  return (
    <section id={id} className="relative z-10 py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-4 md:px-8">
        <Eyebrow>{eyebrow}</Eyebrow>
        <SectionHeadline>{headline}</SectionHeadline>
        <div className="mt-12">{children}</div>
      </div>
    </section>
  );
}
