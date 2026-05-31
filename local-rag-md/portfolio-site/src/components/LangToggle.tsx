"use client";

import { motion } from "framer-motion";
import { useI18n, type Lang } from "@/lib/i18n";

const LANGS: { id: Lang; labelKey: string }[] = [
  { id: "es", labelKey: "lang.label" },
  { id: "en", labelKey: "lang.label" },
  { id: "jp", labelKey: "lang.label" },
];

const LABEL_OVERRIDE: Record<Lang, string> = { es: "ES", en: "EN", jp: "JP" };

export function LangToggle() {
  const { lang, setLang } = useI18n();

  return (
    <nav
      className="fixed top-4 right-4 z-40 flex gap-0.5 rounded-full bg-white/[0.04] backdrop-blur-xl border border-white/[0.08] p-1 text-xs font-medium"
      aria-label="Language selector"
    >
      {LANGS.map((l) => (
        <button
          key={l.id}
          onClick={() => setLang(l.id)}
          className="relative rounded-full px-3 py-1.5 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/50"
          style={{ minWidth: "40px", minHeight: "32px" }}
          aria-current={lang === l.id ? "true" : undefined}
          aria-label={`Switch language to ${LABEL_OVERRIDE[l.id]}`}
        >
          {lang === l.id && (
            <motion.div
              layoutId="lang-indicator"
              className="absolute inset-0 rounded-full bg-white/[0.08]"
              transition={{ type: "spring", stiffness: 300, damping: 24 }}
            />
          )}
          <span className={`relative z-10 ${lang === l.id ? "text-white" : "text-slate-500 hover:text-slate-300"}`}>
            {LABEL_OVERRIDE[l.id]}
          </span>
        </button>
      ))}
    </nav>
  );
}
