"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Section } from "./Section";
import { useI18n } from "@/lib/i18n";

export function ProcessSection() {
  const { t } = useI18n();
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const steps = [
    { label: t("process.s1label"), desc: t("process.s1desc") },
    { label: t("process.s2label"), desc: t("process.s2desc") },
    { label: t("process.s3label"), desc: t("process.s3desc") },
    { label: t("process.s4label"), desc: t("process.s4desc") },
  ];

  const container = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.2 } },
  };

  const easeOut = [0.32, 0.72, 0, 1] as const;
  const item = {
    hidden: { opacity: 0, y: 12 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: easeOut } },
  };

  return (
    <Section id="process" eyebrow={t("process.eyebrow")} headline={t("process.headline")}>
      <div ref={ref}>
        <motion.div
          className="flex flex-col items-center gap-8 md:flex-row md:items-start md:justify-between"
          variants={container}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
        >
          {steps.map((step, i) => (
            <motion.div key={i} className="flex flex-col items-center gap-3 md:flex-1" variants={item}>
              <motion.div
                className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 text-sm font-semibold text-emerald-400 ring-1 ring-emerald-400/20"
                animate={isInView ? { boxShadow: ["0 0 0px rgba(16,185,129,0)", "0 0 20px rgba(16,185,129,0.3)", "0 0 0px rgba(16,185,129,0)"] } : {}}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
              >
                {i + 1}
              </motion.div>
              <div className="text-center">
                <p className="text-sm font-semibold text-white">{step.label}</p>
                <p className="mt-1 max-w-[20ch] text-xs leading-relaxed text-slate-500">{step.desc}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        <svg className="mt-6 hidden h-6 w-full md:block" viewBox="0 0 800 24" preserveAspectRatio="none">
          {steps.slice(0, -1).map((_, i) => {
            const x1 = i * 200 + 100;
            const x2 = x1 + 200;
            return (
              <motion.line
                key={i}
                x1={x1} y1={12} x2={x2} y2={12}
                stroke="rgba(16,185,129,0.2)"
                strokeWidth={1}
                strokeDasharray="4 4"
                initial={{ pathLength: 0 }}
                animate={isInView ? { pathLength: 1 } : {}}
                transition={{ duration: 1, delay: 0.5 + i * 0.2, ease: [0.32, 0.72, 0, 1] }}
              />
            );
          })}
        </svg>
      </div>
    </Section>
  );
}
