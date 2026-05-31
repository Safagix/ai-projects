"use client";

import { motion } from "framer-motion";
import { Section } from "./Section";
import { useI18n } from "@/lib/i18n";

export function AboutSection() {
  const { t } = useI18n();

  return (
    <Section id="about" eyebrow={t("about.eyebrow")} headline={t("about.headline")}>
      <div className="grid grid-cols-1 gap-8 md:grid-cols-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
          className="md:col-span-7 space-y-5"
        >
          <p className="max-w-[65ch] text-base leading-relaxed text-slate-400">{t("about.p1")}</p>
          <p className="max-w-[65ch] text-base leading-relaxed text-slate-400">{t("about.p2")}</p>
          <p className="max-w-[65ch] text-base leading-relaxed text-slate-400">{t("about.p3")}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.15, ease: [0.32, 0.72, 0, 1] }}
          className="md:col-span-5"
        >
          <div className="rounded-[2rem] bg-white/[0.03] p-1.5 ring-1 ring-white/[0.06]">
            <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.02] backdrop-blur-2xl shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)] p-8">
              <div className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-400" />
                <p className="text-sm leading-relaxed text-slate-300">
                  &ldquo;{t("about.diff")}&rdquo;
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </Section>
  );
}
