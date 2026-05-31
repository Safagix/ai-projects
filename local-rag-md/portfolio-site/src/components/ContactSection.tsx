"use client";

import { useState, type FormEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Section } from "./Section";
import { useI18n } from "@/lib/i18n";

type FormState = "idle" | "loading" | "success" | "error";

export function ContactSection() {
  const { t } = useI18n();
  const [formState, setFormState] = useState<FormState>("idle");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormState("loading");
    try {
      await new Promise((r) => setTimeout(r, 1200));
      setFormState("success");
      setTimeout(() => setFormState("idle"), 4000);
    } catch {
      setFormState("error");
      setTimeout(() => setFormState("idle"), 3000);
    }
  };

  const inputClass = "w-full rounded-2xl bg-white/[0.04] border border-white/[0.08] px-5 py-3 text-sm text-white placeholder:text-slate-600 focus:border-emerald-400/40 focus:ring-1 focus:ring-emerald-400/20 focus:outline-none transition-colors duration-200";

  const linkClass = "flex items-center gap-3 rounded-2xl bg-white/[0.02] border border-white/[0.06] px-5 py-4 text-sm text-slate-300 transition-all duration-300 ease-out hover:border-white/[0.12] hover:bg-white/[0.04] focus-visible:ring-2 focus-visible:ring-emerald-400/50 focus-visible:outline-none";

  return (
    <Section id="contact" eyebrow={t("contact.eyebrow")} headline={t("contact.headline")}>
      <div className="flex flex-col gap-12 md:flex-row">
        <form onSubmit={handleSubmit} className="flex w-full flex-col gap-5 md:w-3/5" noValidate>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="contact-name" className="text-xs font-medium text-slate-400">{t("contact.nameLabel")}</label>
            <input id="contact-name" type="text" required className={inputClass} placeholder="Tu nombre" />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="contact-email" className="text-xs font-medium text-slate-400">{t("contact.emailLabel")}</label>
            <input id="contact-email" type="email" required className={inputClass} placeholder="[REDACTED]" />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="contact-message" className="text-xs font-medium text-slate-400">{t("contact.msgLabel")}</label>
            <textarea id="contact-message" required rows={4} className={`${inputClass} min-h-[120px] resize-y`} placeholder={t("contact.placeholder")} />
          </div>

          <AnimatePresence mode="wait">
            {formState === "error" && (
              <motion.p initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-xs text-red-400">
                Algo salio mal. Intenta de nuevo.
              </motion.p>
            )}
            {formState === "success" && (
              <motion.p initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-xs text-emerald-400">
                Mensaje enviado. Gracias.
              </motion.p>
            )}
          </AnimatePresence>

          <button
            type="submit"
            disabled={formState === "loading" || formState === "success"}
            className="group inline-flex items-center gap-2 self-start rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-black transition-all duration-150 ease hover:scale-[0.98] active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050505]"
          >
            {formState === "loading" ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-black border-t-transparent" />
                Enviando...
              </span>
            ) : formState === "success" ? (
              "Enviado"
            ) : (
              <>
                {t("contact.cta")}
                <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-black/15 transition-transform duration-300 ease-out group-hover:translate-x-0.5 group-hover:-translate-y-px">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 17L17 7"/><path d="M7 7h10v10"/></svg>
                </span>
              </>
            )}
          </button>
        </form>

        <div className="flex w-full flex-col gap-3 md:w-2/5">
          <a href="mailto:[REDACTED]" className={linkClass} style={{ minHeight: "48px" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            {t("contact.emailLink")}
          </a>
          <a href="https://github.com/safagix" target="_blank" rel="noopener noreferrer" className={linkClass} style={{ minHeight: "48px" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
            {t("contact.github")}
          </a>
          <a href="https://linkedin.com/in/safag" target="_blank" rel="noopener noreferrer" className={linkClass} style={{ minHeight: "48px" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/></svg>
            {t("contact.linkedin")}
          </a>
        </div>
      </div>
    </Section>
  );
}
