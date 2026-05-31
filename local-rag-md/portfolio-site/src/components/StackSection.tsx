"use client";

import { motion } from "framer-motion";
import { Section } from "./Section";
import { useI18n } from "@/lib/i18n";

const SPANS = [5, 3, 4, 4, 8];

interface StackCategoryProps {
  label: string;
  items: string;
  span: number;
  index: number;
}

function StackCategory({ label, items, span, index }: StackCategoryProps) {
  const itemList = items.split(",").filter(Boolean);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
      whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.08, ease: [0.32, 0.72, 0, 1] }}
      className={`md:col-span-${span} rounded-[2rem] bg-white/[0.03] p-1.5 ring-1 ring-white/[0.06]`}
      whileHover={{ boxShadow: "0 0 30px -8px rgba(16,185,129,0.06)" }}
    >
      <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.02] px-8 py-6">
        <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-emerald-400">{label}</span>
        <div className="mt-4 flex flex-wrap gap-2">
          {itemList.map((item) => (
            <span key={item} className="rounded-full border border-white/[0.08] bg-white/[0.04] px-3 py-1 text-xs text-slate-300">
              {item}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

export function StackSection() {
  const { t } = useI18n();

  const categories = [
    { label: t("stack.langLabel"), items: t("stackItems.languages"), span: SPANS[0], index: 0 },
    { label: t("stack.fwLabel"), items: t("stackItems.frameworks"), span: SPANS[1], index: 1 },
    { label: t("stack.aiLabel"), items: t("stackItems.ai"), span: SPANS[2], index: 2 },
    { label: t("stack.dsLabel"), items: t("stackItems.design"), span: SPANS[3], index: 3 },
    { label: t("stack.autoLabel"), items: t("stackItems.automation"), span: SPANS[4], index: 4 },
  ];

  return (
    <Section id="stack" eyebrow={t("stack.eyebrow")} headline={t("stack.headline")}>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
        {categories.map((cat) => (
          <StackCategory key={cat.label} {...cat} />
        ))}
      </div>
    </Section>
  );
}
