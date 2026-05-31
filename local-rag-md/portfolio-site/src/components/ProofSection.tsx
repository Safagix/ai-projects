"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform, useInView } from "framer-motion";
import { Section } from "./Section";
import { useI18n } from "@/lib/i18n";

function CounterValue({ target, isInView }: { target: string; isInView: boolean }) {
  const numeric = parseFloat(target) || 0;
  const mv = useMotionValue(0);
  const spring = useSpring(mv, { stiffness: 80, damping: 20 });
  const display = useTransform(spring, (v) => Math.round(v).toString());
  const [final, setFinal] = useState("0");

  useEffect(() => {
    if (isInView) mv.set(numeric);
  }, [isInView, numeric, mv]);

  useEffect(() => {
    const unsubscribe = display.on("change", (v) => {
      if (target.includes("+")) setFinal(`${v}+`);
      else if (target.includes("-")) setFinal(`${target}`);
      else setFinal(v);
    });
    return unsubscribe;
  }, [display, target]);

  return (
    <motion.span
      className="block text-5xl font-semibold tracking-tighter text-white"
      style={{ fontFamily: "var(--font-display)" }}
    >
      {final}
    </motion.span>
  );
}

export function ProofSection() {
  const { t } = useI18n();
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  const stats = [
    { label: t("proof.r1label"), value: t("proof.r1val") },
    { label: t("proof.r2label"), value: t("proof.r2val") },
    { label: t("proof.r3label"), value: t("proof.r3val") },
    { label: t("proof.r4label"), value: t("proof.r4val") },
    { label: t("proof.r5label"), value: t("proof.r5val") },
  ];

  return (
    <Section id="proof" eyebrow={t("proof.eyebrow")} headline={t("proof.headline")}>
      <div ref={ref} className="grid grid-cols-2 gap-8 md:grid-cols-5">
        {stats.map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 16 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: i * 0.1, ease: [0.32, 0.72, 0, 1] }}
            className="flex flex-col items-start"
          >
            <CounterValue target={stat.value} isInView={isInView} />
            <div className="mt-4 h-px w-8 bg-emerald-500/30" />
            <span className="mt-2 text-xs uppercase tracking-[0.15em] text-slate-500">{stat.label}</span>
          </motion.div>
        ))}
      </div>
    </Section>
  );
}
