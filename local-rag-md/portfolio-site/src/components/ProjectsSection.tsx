"use client";

import { motion } from "framer-motion";
import { Section } from "./Section";
import { useI18n } from "@/lib/i18n";

const ROTATIONS = [-0.8, 1.2, -0.4];

interface ProjectCardProps {
  title: string;
  problem: string;
  prompt: string;
  result: string;
  stack: string;
  role: string;
  m1label: string;
  m1val: string;
  m2label: string;
  m2val: string;
  m3label: string;
  m3val: string;
  index: number;
}

function ProjectCard(props: ProjectCardProps) {
  const stackItems = props.stack.split(",").filter(Boolean);

  return (
    <motion.div
      initial={{ opacity: 0, y: 24, filter: "blur(4px)" }}
      whileInView={{ opacity: 1, y: 0, rotate: ROTATIONS[props.index % ROTATIONS.length], filter: "blur(0px)" }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.7, delay: props.index * 0.15, ease: [0.32, 0.72, 0, 1] }}
      className={`relative z-${30 - props.index * 10} ${props.index > 0 ? "md:-mt-8" : ""} rounded-[2rem] bg-white/[0.03] p-1.5 ring-1 ring-white/[0.06]`}
    >
      <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.02] backdrop-blur-2xl shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)] p-8">
        <h3 className="text-2xl tracking-tight text-white" style={{ fontFamily: "var(--font-display)" }}>
          {props.title}
        </h3>

        <div className="mt-6 space-y-5">
          <div>
            <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-slate-500">Problem</span>
            <p className="mt-1 text-sm leading-relaxed text-slate-300">{props.problem}</p>
          </div>

          <div>
            <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-slate-500">Prompt</span>
            <pre className="mt-1 overflow-x-auto rounded-xl bg-black/40 p-5 text-sm leading-relaxed text-slate-300" style={{ fontFamily: "var(--font-mono)" }}>
              <code>{props.prompt}</code>
            </pre>
          </div>

          <div>
            <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-slate-500">Result</span>
            <p className="mt-1 text-sm leading-relaxed text-emerald-400">{props.result}</p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {stackItems.map((tech) => (
            <span key={tech} className="rounded-full border border-white/[0.08] bg-white/[0.04] px-2.5 py-1 text-xs text-slate-400">
              {tech}
            </span>
          ))}
        </div>

        <p className="mt-4 text-xs text-slate-600">{props.role}</p>

        <div className="mt-6 flex gap-6 border-t border-white/[0.06] pt-6">
          <div className="text-center">
            <span className="block text-2xl font-semibold tracking-tighter text-white">{props.m1val}</span>
            <span className="text-[10px] uppercase tracking-[0.15em] text-slate-500">{props.m1label}</span>
          </div>
          <div className="text-center">
            <span className="block text-2xl font-semibold tracking-tighter text-white">{props.m2val}</span>
            <span className="text-[10px] uppercase tracking-[0.15em] text-slate-500">{props.m2label}</span>
          </div>
          <div className="text-center">
            <span className="block text-2xl font-semibold tracking-tighter text-white">{props.m3val}</span>
            <span className="text-[10px] uppercase tracking-[0.15em] text-slate-500">{props.m3label}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export function ProjectsSection() {
  const { t } = useI18n();

  const projects = [
    { titleKey: "project0.title", problemKey: "project0.problem", promptKey: "project0.prompt", resultKey: "project0.result", stackKey: "project0.stack", roleKey: "project0.role", m1lKey: "project0.m1label", m1vKey: "project0.m1val", m2lKey: "project0.m2label", m2vKey: "project0.m2val", m3lKey: "project0.m3label", m3vKey: "project0.m3val" },
    { titleKey: "project1.title", problemKey: "project1.problem", promptKey: "project1.prompt", resultKey: "project1.result", stackKey: "project1.stack", roleKey: "project1.role", m1lKey: "project1.m1label", m1vKey: "project1.m1val", m2lKey: "project1.m2label", m2vKey: "project1.m2val", m3lKey: "project1.m3label", m3vKey: "project1.m3val" },
    { titleKey: "project2.title", problemKey: "project2.problem", promptKey: "project2.prompt", resultKey: "project2.result", stackKey: "project2.stack", roleKey: "project2.role", m1lKey: "project2.m1label", m1vKey: "project2.m1val", m2lKey: "project2.m2label", m2vKey: "project2.m2val", m3lKey: "project2.m3label", m3vKey: "project2.m3val" },
  ];

  return (
    <Section id="projects" eyebrow={t("projects.eyebrow")} headline={t("projects.headline")}>
      <div className="space-y-0">
        {projects.map((p, i) => (
          <ProjectCard
            key={i}
            index={i}
            title={t(p.titleKey)}
            problem={t(p.problemKey)}
            prompt={t(p.promptKey)}
            result={t(p.resultKey)}
            stack={t(p.stackKey)}
            role={t(p.roleKey)}
            m1label={t(p.m1lKey)}
            m1val={t(p.m1vKey)}
            m2label={t(p.m2lKey)}
            m2val={t(p.m2vKey)}
            m3label={t(p.m3lKey)}
            m3val={t(p.m3vKey)}
          />
        ))}
      </div>
    </Section>
  );
}
