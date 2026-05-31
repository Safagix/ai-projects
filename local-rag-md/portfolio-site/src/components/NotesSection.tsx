"use client";

import { motion } from "framer-motion";
import { Section } from "./Section";
import { useI18n } from "@/lib/i18n";

interface NoteCardProps {
  title: string;
  body: string;
  spanClass: string;
  index: number;
}

function NoteCard({ title, body, spanClass, index }: NoteCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
      whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.6, delay: index * 0.1, ease: [0.32, 0.72, 0, 1] }}
      whileHover={{ y: -2, borderColor: "rgba(255,255,255,0.12)" }}
      className={`${spanClass} rounded-[2rem] bg-white/[0.03] p-1.5 ring-1 ring-white/[0.06] transition-all duration-500 ease-out`}
    >
      <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.02] p-8">
        <h3 className="text-xl font-semibold tracking-tight text-white" style={{ fontFamily: "var(--font-display)" }}>
          {title}
        </h3>
        <p className="mt-3 max-w-[65ch] text-sm leading-relaxed text-slate-400">{body}</p>
      </div>
    </motion.div>
  );
}

export function NotesSection() {
  const { t } = useI18n();

  const notes = [
    { title: t("notes.n1title"), body: t("notes.n1body"), span: "md:col-span-6" },
    { title: t("notes.n2title"), body: t("notes.n2body"), span: "md:col-span-6" },
    { title: t("notes.n3title"), body: t("notes.n3body"), span: "md:col-span-6" },
    { title: t("notes.n4title"), body: t("notes.n4body"), span: "md:col-span-6" },
  ];

  return (
    <Section id="notes" eyebrow={t("notes.eyebrow")} headline={t("notes.headline")}>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
        {notes.map((note, i) => (
          <NoteCard key={i} title={note.title} body={note.body} spanClass={note.span} index={i} />
        ))}
      </div>
    </Section>
  );
}
