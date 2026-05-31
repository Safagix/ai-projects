"use client";

import { I18nProvider } from "@/lib/i18n";
import { LangToggle } from "@/components/LangToggle";
import { HeroSection } from "@/components/HeroSection";
import { AboutSection } from "@/components/AboutSection";
import { StackSection } from "@/components/StackSection";
import { ProjectsSection } from "@/components/ProjectsSection";
import { ProcessSection } from "@/components/ProcessSection";
import { ProofSection } from "@/components/ProofSection";
import { NotesSection } from "@/components/NotesSection";
import { ContactSection } from "@/components/ContactSection";

export default function Home() {
  return (
    <I18nProvider>
      <LangToggle />
      <main>
        <HeroSection />
        <AboutSection />
        <StackSection />
        <ProjectsSection />
        <ProcessSection />
        <ProofSection />
        <NotesSection />
        <ContactSection />
      </main>
      <footer className="relative z-10 border-t border-white/[0.04] py-8 text-center">
        <p className="text-xs text-slate-600">Hecho en el Digital Lab &middot; 2026</p>
      </footer>
    </I18nProvider>
  );
}
