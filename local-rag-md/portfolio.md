<!--
╔══════════════════════════════════════════════════════════════════════════╗
║  PORTFOLIO SPEC — Digital Lab Ecosystem                                  ║
║  Target: Static site generator / site builder (paste-ready)              ║
║  Primary lang: ES   Secondary: EN · JP  (toggle top-right)               ║
║  Design system: Ethereal Glass + Asymmetrical Bento + Z-Cascade          ║
║  Motion engine: Framer Motion springs + Three.js 3D particle field       ║
║  Stack hint: Next.js 14 + Tailwind v4 + Framer Motion + Three.js         ║
║  Dev handoff: read HTML comments for component specs, motion specs,      ║
║               3D scene architecture, and accessibility requirements.      ║
╚══════════════════════════════════════════════════════════════════════════╝
-->

<!--
═══════════════════════════════════════════════════════════════════════════
DESIGN SYSTEM — GLOBAL TOKENS
═══════════════════════════════════════════════════════════════════════════

VIBE ARCHETYPE: Ethereal Glass (SaaS / AI / Tech)
  ─ Background:            #050505 (deepest OLED black)
  ─ Card surface:          rgba(255,255,255,0.03) with backdrop-blur-2xl
  ─ Card border:           rgba(255,255,255,0.08) 1px
  ─ Card inner highlight:  shadow-[inset_0_1px_1px_rgba(255,255,255,0.08)]
  ─ Accent (sole):         #10B981 (electric emerald) — no purple/blue ever
  ─ Accent muted:          #065F46
  ─ Text primary:          #F1F5F9 (slate-100)
  ─ Text secondary:        #64748B (slate-500)
  ─ Text tertiary:         #334155 (slate-700)
  ─ Gradient orb 1:        radial emerald glow at 20vw 30vh, opacity 0.06
  ─ Gradient orb 2:        radial warm amber glow at 80vw 70vh, opacity 0.04
  ─ Noise overlay:         fixed inset-0 z-50 pointer-events-none, opacity 0.025

LAYOUT ARCHETYPE: Asymmetrical Bento + Z-Axis Cascade
  ─ Hero:                  Split 50/50 (left content / right 3D canvas)
  ─ Cards:                 Bento grid with col-span-8 row-span-2 + col-span-4 pairs
  ─ Stack section:         Bento grid, non-uniform cell sizes
  ─ Projects section:      Z-axis cascade with staggered rotation (±1.5deg)
  ─ Mobile (<768px):       EVERYTHING collapses to single column, w-full, px-4, py-8
  ─ No edge-to-edge sticky navbars. No h-screen. Use min-h-[100dvh].
  ─ No 3-column equal card rows. Banned.

TYPOGRAPHY
  ─ Display:    Cabinet Grotesk (h1–h3) or Clash Display
  ─ Body:       Geist or Satoshi (p, li, small)
  ─ Mono:       JetBrains Mono (code snippets, prompt diffs)
  ─ Scale:      h1: text-4xl md:text-6xl tracking-tighter leading-[0.9]
                h2: text-3xl md:text-5xl tracking-tight leading-[0.95]
                h3: text-2xl md:text-3xl tracking-tight leading-tight
                body: text-base text-gray-400 leading-relaxed max-w-[65ch]
                eyebrow: text-[10px] uppercase tracking-[0.2em] font-medium
  ─ BANNED: Inter, Roboto, Arial, Open Sans, Helvetica

SPACING
  ─ Section padding:       py-24 min. Move up to py-32 / py-40 for hero.
  ─ Section gap:           gap-24 between sections
  ─ Card inner padding:    p-8 or p-10
  ─ Double-bezel gap:      p-1.5 outer → rounded-[2rem] outer, rounded-[calc(2rem-0.375rem)] inner

MOTION TOKENS
  ─ Enter/exit:            ease-out cubic-bezier(0.32,0.72,0,1) 700ms
  ─ On-screen movement:    ease-in-out cubic-bezier(0.77,0,0.175,1)
  ─ Hover transitions:     ease 150ms
  ─ Spring physics:        type: spring, stiffness: 100, damping: 20
  ─ Scroll reveals:        translate-y-16 blur-md opacity-0 → translate-y-0 blur-0 opacity-1
                            via Framer Motion whileInView, no scroll listeners
  ─ Button active:         scale-[0.98] translate-y-[1px]
  ─ prefers-reduced-motion: must disable all animations

CARDS — DOUBLE-BEZEL ARCHITECTURE
  Every card uses nested containers:
  Outer: <div class="p-1.5 rounded-[2rem] bg-white/[0.03] ring-1 ring-white/[0.06]">
  Inner: <div class="rounded-[calc(2rem-0.375rem)] bg-white/[0.02] backdrop-blur-2xl
                      shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)] p-8">

CTA — BUTTON-IN-BUTTON PATTERN
  <button class="rounded-full px-6 py-3 bg-emerald-500 text-black font-semibold
                 hover:scale-[0.98] active:scale-[0.97] transition-all duration-150 ease
                 group">
    <span>View project</span>
    <span class="inline-flex items-center justify-center w-7 h-7 rounded-full
                 bg-black/15 ml-2 group-hover:translate-x-0.5 group-hover:-translate-y-px
                 transition-transform duration-300 ease-out">
      <!-- arrow icon -->
    </span>
  </button>

ICONS
  Set: Phosphor Light (weight: regular, strokeWidth: 1.5)
  Size: w-5 h-5 for UI, w-4 h-4 for inline
  BANNED: Lucide thick strokes, FontAwesome, Material Icons, emojis as icons

FORM COMPONENTS (contact section)
  Label above input. gap-2 input blocks. Error text below.
  Input: rounded-2xl bg-white/[0.04] border border-white/[0.08] px-5 py-3
         focus:border-emerald-400/40 focus:ring-1 focus:ring-emerald-400/20
  Helper: text-xs text-slate-600 mt-1

ACCESSIBILITY — from ui-ux-pro-max & web-design-guidelines
  ─ Color contrast: 4.5:1 minimum
  ─ Focus states: visible 2px ring on interactive elements
  ─ Touch targets: 44×44px minimum
  ─ prefers-reduced-motion: media query for ALL animated elements
  ─ Keyboard nav: tab order matches visual order
  ─ Form labels: <label for="..."> above every input
  ─ Alt text: descriptive for all meaningful images
  ─ Touch: @media (hover: hover) and (pointer: fine) for hover effects

3D SCENE — HERO BACKGROUND (Three.js)
  ─ Architecture: isolated <canvas> in right 50% of hero
  ─ Geometry: THREE.IcosahedronGeometry(2, 4) wireframe + particle cloud
  ─ Material: ShaderMaterial with custom vertex/fragment GLSL
    ─ Vertex: wave displacement via sin(time + position.x * 3)
    ─ Fragment: fresnel rim + emerald → transparent gradient
  ─ Post-processing: UnrealBloomPass (strength 0.4, threshold 0.6)
  ─ Interaction: mouse.x drives rotationY; mouse.y drives rotationX
  ─ Clock: THREE.Clock.getDelta() for frame-rate-independent animation
  ─ Cleanup: geometry.dispose(), material.dispose(), renderer.dispose() on unmount
  ─ Mobile: reduce particle count 80%, disable bloom, drop to 30fps
  ─ NEVER animate top/left/width/height. Transform + opacity only.
  ─ Noise overlay: fixed pseudo-element with pointer-events-none (not on canvas)

TRILINGUAL TOGGLE
  ─ Position: top-right, floating glass pill
  ─ Structure: <nav class="fixed top-4 right-4 z-40 flex gap-1 rounded-full
                            bg-white/[0.04] backdrop-blur-xl border border-white/[0.08]
                            p-1 text-xs font-medium">
  ─ Items: ES (default) | EN | JP — tab-style indicator slides via layoutId
  ─ Data: All copy stored in i18n object { es: {...}, en: {...}, jp: {...} }
  ─ Component: isolated Client Component with useMotionValue for tab indicator
-->


<!--
╔══════════════════════════════════════════════════════════════════════════╗
║  SECTION 0 — I18N CONTENT DICTIONARY (dev-only, not rendered)            ║
║  All visible copy defined here. ES default. EN/JP toggled in UI.         ║
║  Dev: embed as {i18n[lang].hero.name} etc.                               ║
╚══════════════════════════════════════════════════════════════════════════╝
-->

<!--
  i18n structure (conceptual — implement as JSON or TS const):

{
  es: {
    langLabel: "ES",
    nav: { about: "Sobre", stack: "Stack", projects: "Proyectos", process: "Proceso", proof: "Pruebas", notes: "Notas", contact: "Contacto" },
    hero: {
      role: "AI Agent Builder · Vibe-Coding Native",
      edge: "Construyo agentes, apps y automatizaciones que pasan a producción en días, no en meses.",
      cta: "Ver proyectos"
    },
    about: {
      eyebrow: "Que construyo",
      headline: "Agentes. Apps. Automatizaciones.",
      p1: "Diseño y despliego agentes de IA que ejecutan tareas reales — desde scraping inteligente hasta pipelines multi-agente con n8n. Cada proyecto empieza con un prompt y termina en producción.",
      p2: "Trabajo con founders que necesitan velocidad sin sacrificar calidad. Mi diferencial: entiendo el stack técnico y el producto al mismo nivel. No soy solo el que escribe código — soy el que pregunta por qué.",
      p3: "Trilingue. Remoto. Enfocado en resultados, no en horas."
    },
    stack: {
      eyebrow: "Stack",
      headline: "Tecnologia que uso para construir",
      languages: { label: "Lenguajes", items: ["TypeScript", "Python", "SQL", "Bash"] },
      frameworks: { label: "Frameworks", items: ["Next.js", "React", "FastAPI", "LangChain"] },
      ai: { label: "AI / Agentes", items: ["Claude API", "GPT-4o", "Ollama (local)", "LangGraph", "CrewAI"] },
      design: { label: "Diseno", items: ["Figma", "Tailwind CSS", "Framer Motion", "Three.js", "Sleek.design"] },
      automation: { label: "Automatizacion", items: ["n8n", "Railway", "Supabase", "Docker", "GitHub Actions"] }
    },
    projects: {
      eyebrow: "Proyectos",
      headline: "Prompt + resultado. Sin relleno.",
      items: [
        {
          title: "Eira Brain — Asistente IA con RAG local",
          problem: "Equipos gastan 6h/semana buscando informacion en documentacion dispersa.",
          prompt: "Construime un sistema RAG que indexe mi vault de Obsidian, responda desde el contexto local, y corra completamente offline con Ollama.",
          result: "Asistente funcional en 72h. Responde con citas a documentos. 0 latencia de red. Privacidad total.",
          stack: ["Python", "FastAPI", "Ollama", "ChromaDB", "Obsidian API"],
          role: "Arquitectura + implementacion completa",
          metrics: ["-93% tiempo de busqueda", "800+ docs indexados", "0 dependencia cloud"]
        },
        {
          title: "Local RAG MD — Ingesta de GitHub a Obsidian",
          problem: "Leer codigo de repositorios open-source requiere cambiar de ventana constantemente. El contexto se pierde.",
          prompt: "Haceme un pipeline que tome cualquier repo publico de GitHub, lo convierta en notas de Obsidian limpias, y lo indexe para busqueda semantica local.",
          result: "Pipeline con soporte para 150+ lenguajes. Importa repos en <30s. Markdown limpio con frontmatter YAML. Busqueda semantica integrada.",
          stack: ["Python", "FastAPI", "LangChain", "ChromaDB", "Obsidian"],
          role: "Diseno + implementacion end-to-end",
          metrics: ["150+ lenguajes", "<30s por repo", "Busqueda semantica local"]
        },
        {
          title: "UI/UX Catalog Collector — Catalogo de componentes inteligente",
          problem: "Cada nuevo proyecto empieza desde cero. Sin reuso de componentes, sin consistencia visual.",
          prompt: "Creame un sistema que clasifique automaticamente componentes UI, los guarde en un catalogo JSON, y los exponga en Obsidian como notas editables.",
          result: "Catalogo con 7 componentes iniciales. Clasificador LLM que asigna categorias, tags y quality score. API REST para ingesta.",
          stack: ["Python", "FastAPI", "Ollama (Llama 3.2)", "JSON catalog", "Obsidian"],
          role: "Arquitectura full-stack",
          metrics: ["7 componentes", "Clasificacion automatica", "API REST lista"]
        }
      ]
    },
    process: {
      eyebrow: "Proceso",
      headline: "Idea → prompt → iterar → ship",
      steps: [
        { label: "Idea", desc: "Definimos el problema real. Nada de construir por construir." },
        { label: "Prompt", desc: "Transformo la idea en prompts precisos. El vibe-coding es real cuando sabes que pedir." },
        { label: "Iterar", desc: "Testeo, ajusto, refino. Cada iteracion acerca el output a produccion." },
        { label: "Ship", desc: "Deploy. El codigo que no esta en produccion no existe." }
      ]
    },
    proof: {
      eyebrow: "Pruebas",
      headline: "Lo que ya esta en produccion",
      items: [
        { label: "Repositorios activos", value: "12+" },
        { label: "Agentes en produccion", value: "4" },
        { label: "Componentes en catalogo", value: "7" },
        { label: "Pipeline n8n activas", value: "8" },
        { label: "Dias hasta primer MVP", value: "3-7" }
      ]
    },
    notes: {
      eyebrow: "Notas",
      headline: "Micro-ensayos. Voz de zine digital.",
      items: [
        { title: "El prompt es el nuevo IDE", body: "Escribir prompts no es preguntar. Es programar con lenguaje natural. La diferencia entre un prompt que funciona y uno que no es la misma que entre codigo limpio y espagueti. Claridad, contexto, constraints." },
        { title: "Velocidad > perfeccion", body: "Un MVP en 3 dias con fallas le gana a una app perfecta que nunca sale. El mercado no espera. Tus usuarios tampoco. Itera en publico." },
        { title: "Agentes, no chatbots", body: "El 90% de 'IA en produccion' son wrappers de ChatGPT. Un agente real ejecuta tareas, consulta APIs, escribe archivos, toma decisiones. Si solo responde texto, no es un agente." },
        { title: "Offline-first es el verdadero lujo", body: "Correr modelos localmente cambia todo. Privacidad real. Latencia cero. Sin quotas. Sin facturas sorpresa. Ollama + ChromaDB en una laptop compiten con servicios cloud de $500/mes." }
      ]
    },
    contact: {
      eyebrow: "Contacto",
      headline: "Hablemos de lo que queres construir",
      email: "Correo",
      github: "GitHub",
      linkedin: "LinkedIn",
      cta: "Enviar mensaje"
    }
  },
  en: {
    langLabel: "EN",
    nav: { about: "About", stack: "Stack", projects: "Projects", process: "Process", proof: "Proof", notes: "Notes", contact: "Contact" },
    hero: {
      role: "AI Agent Builder · Vibe-Coding Native",
      edge: "I build agents, apps, and automations that ship to production in days, not months.",
      cta: "View projects"
    },
    about: {
      eyebrow: "What I Build",
      headline: "Agents. Apps. Automations.",
      p1: "I design and deploy AI agents that execute real tasks — from intelligent scraping to multi-agent pipelines with n8n. Every project starts with a prompt and ends in production.",
      p2: "I work with founders who need speed without sacrificing quality. My edge: I understand the tech stack and the product at the same depth. I'm not just the person writing code — I'm the person asking why.",
      p3: "Trilingual. Remote. Focused on outcomes, not hours."
    },
    stack: {
      eyebrow: "Stack",
      headline: "Tech I build with",
      languages: { label: "Languages", items: ["TypeScript", "Python", "SQL", "Bash"] },
      frameworks: { label: "Frameworks", items: ["Next.js", "React", "FastAPI", "LangChain"] },
      ai: { label: "AI / Agents", items: ["Claude API", "GPT-4o", "Ollama (local)", "LangGraph", "CrewAI"] },
      design: { label: "Design", items: ["Figma", "Tailwind CSS", "Framer Motion", "Three.js", "Sleek.design"] },
      automation: { label: "Automation", items: ["n8n", "Railway", "Supabase", "Docker", "GitHub Actions"] }
    },
    projects: {
      eyebrow: "Projects",
      headline: "Prompt + outcome. Zero filler.",
      items: [
        {
          title: "Eira Brain — RAG-powered AI Assistant",
          problem: "Teams spend 6h/week hunting for information across scattered documentation.",
          prompt: "Build me a RAG system that indexes my Obsidian vault, answers from local context, and runs completely offline with Ollama.",
          result: "Functional assistant in 72h. Responds with document citations. Zero network latency. Full privacy.",
          stack: ["Python", "FastAPI", "Ollama", "ChromaDB", "Obsidian API"],
          role: "Architecture + full implementation",
          metrics: ["-93% search time", "800+ indexed docs", "0 cloud dependency"]
        },
        {
          title: "Local RAG MD — GitHub-to-Obsidian Ingestion",
          problem: "Reading open-source code requires constant window switching. Context gets lost.",
          prompt: "Build me a pipeline that takes any public GitHub repo, converts it to clean Obsidian notes, and indexes it for local semantic search.",
          result: "Pipeline supporting 150+ languages. Imports repos in <30s. Clean markdown with YAML frontmatter. Integrated semantic search.",
          stack: ["Python", "FastAPI", "LangChain", "ChromaDB", "Obsidian"],
          role: "Design + end-to-end implementation",
          metrics: ["150+ languages", "<30s per repo", "Local semantic search"]
        },
        {
          title: "UI/UX Catalog Collector — Smart Component Catalog",
          problem: "Every new project starts from scratch. No component reuse, no visual consistency.",
          prompt: "Create a system that auto-classifies UI components, stores them in a JSON catalog, and exposes them in Obsidian as editable notes.",
          result: "Catalog with 7 initial components. LLM classifier that assigns categories, tags, and quality scores. REST API for ingestion.",
          stack: ["Python", "FastAPI", "Ollama (Llama 3.2)", "JSON catalog", "Obsidian"],
          role: "Full-stack architecture",
          metrics: ["7 components", "Auto-classification", "REST API ready"]
        }
      ]
    },
    process: {
      eyebrow: "Process",
      headline: "Idea → prompt → iterate → ship",
      steps: [
        { label: "Idea", desc: "We define the real problem. No building for the sake of building." },
        { label: "Prompt", desc: "I transform the idea into precise prompts. Vibe-coding works when you know what to ask for." },
        { label: "Iterate", desc: "Test, adjust, refine. Each iteration pushes output closer to production." },
        { label: "Ship", desc: "Deploy. Code that isn't in production doesn't exist." }
      ]
    },
    proof: {
      eyebrow: "Proof",
      headline: "Already in production",
      items: [
        { label: "Active repositories", value: "12+" },
        { label: "Agents in production", value: "4" },
        { label: "Catalog components", value: "7" },
        { label: "Active n8n pipelines", value: "8" },
        { label: "Days to first MVP", value: "3-7" }
      ]
    },
    notes: {
      eyebrow: "Notes",
      headline: "Micro-essays. Digital zine voice.",
      items: [
        { title: "The prompt is the new IDE", body: "Writing prompts isn't asking. It's programming with natural language. The gap between a prompt that works and one that doesn't mirrors the gap between clean code and spaghetti. Clarity, context, constraints." },
        { title: "Speed > perfection", body: "A flawed MVP in 3 days beats a perfect app that never ships. The market won't wait. Neither will your users. Iterate in public." },
        { title: "Agents, not chatbots", body: "90% of 'AI in production' are ChatGPT wrappers. A real agent executes tasks, calls APIs, writes files, makes decisions. If it only responds with text, it's not an agent." },
        { title: "Offline-first is the real luxury", body: "Running models locally changes everything. Real privacy. Zero latency. No quotas. No surprise bills. Ollama + ChromaDB on a laptop compete with $500/month cloud services." }
      ]
    },
    contact: {
      eyebrow: "Contact",
      headline: "Let's talk about what you want to build",
      email: "Email",
      github: "GitHub",
      linkedin: "LinkedIn",
      cta: "Send message"
    }
  },
  jp: {
    langLabel: "JP",
    nav: { about: "概要", stack: "技術", projects: "実績", process: "工程", proof: "証明", notes: "記録", contact: "連絡" },
    hero: {
      role: "AIエージェント開発者 · Vibeコーディング実践者",
      edge: "数ヶ月ではなく数日で本番環境に届く、エージェント、アプリ、自動化を構築します。",
      cta: "プロジェクトを見る"
    },
    about: {
      eyebrow: "構築するもの",
      headline: "エージェント。アプリ。自動化。",
      p1: "インテリジェントなスクレイピングからn8nを使用したマルチエージェントパイプラインまで、実際のタスクを実行するAIエージェントを設計・展開します。すべてのプロジェクトはプロンプトから始まり、本番環境で終わります。",
      p2: "品質を犠牲にすることなくスピードを必要とするファウンダーと協働しています。私の強みは、技術スタックとプロダクトを同じ深さで理解していることです。コードを書くだけの人ではなく、なぜを問う人です。",
      p3: "トリリンガル。リモート。時間ではなく成果に焦点。"
    },
    stack: {
      eyebrow: "技術",
      headline: "使用技術",
      languages: { label: "言語", items: ["TypeScript", "Python", "SQL", "Bash"] },
      frameworks: { label: "フレームワーク", items: ["Next.js", "React", "FastAPI", "LangChain"] },
      ai: { label: "AI / エージェント", items: ["Claude API", "GPT-4o", "Ollama (ローカル)", "LangGraph", "CrewAI"] },
      design: { label: "デザイン", items: ["Figma", "Tailwind CSS", "Framer Motion", "Three.js", "Sleek.design"] },
      automation: { label: "自動化", items: ["n8n", "Railway", "Supabase", "Docker", "GitHub Actions"] }
    },
    projects: {
      eyebrow: "実績",
      headline: "プロンプト + 結果。無駄なし。",
      items: [
        {
          title: "Eira Brain — RAG搭載AIアシスタント",
          problem: "チームは散在するドキュメントから情報を探すのに週6時間を費やしています。",
          prompt: "Obsidian保管庫をインデックス化し、ローカルコンテキストから回答し、Ollamaで完全オフライン動作するRAGシステムを構築してください。",
          result: "72時間で機能するアシスタント。ドキュメント引用付きで回答。ネットワーク遅延ゼロ。完全なプライバシー。",
          stack: ["Python", "FastAPI", "Ollama", "ChromaDB", "Obsidian API"],
          role: "アーキテクチャ + 全実装",
          metrics: ["検索時間-93%", "800以上のドキュメント", "クラウド依存ゼロ"]
        },
        {
          title: "Local RAG MD — GitHubからObsidianへの取り込み",
          problem: "オープンソースコードの閲覧には常にウィンドウ切り替えが必要で、コンテキストが失われます。",
          prompt: "公開GitHubリポジトリを取得し、クリーンなObsidianノートに変換し、ローカルセマンティック検索用にインデックス化するパイプラインを構築してください。",
          result: "150以上の言語をサポートするパイプライン。30秒未満でリポジトリをインポート。YAMLフロントマター付きのクリーンなMarkdown。統合セマンティック検索。",
          stack: ["Python", "FastAPI", "LangChain", "ChromaDB", "Obsidian"],
          role: "設計 + エンドツーエンド実装",
          metrics: ["150以上の言語", "リポジトリあたり30秒未満", "ローカルセマンティック検索"]
        }
      ]
    },
    process: {
      eyebrow: "工程",
      headline: "アイデア → プロンプト → 反復 → 出荷",
      steps: [
        { label: "アイデア", desc: "実際の問題を定義します。作るためだけに作ることはありません。" },
        { label: "プロンプト", desc: "アイデアを正確なプロンプトに変換します。何を求めるかを知っていれば、Vibeコーディングは機能します。" },
        { label: "反復", desc: "テスト、調整、改良。各反復で出力が本番環境に近づきます。" },
        { label: "出荷", desc: "デプロイ。本番環境にないコードは存在しません。" }
      ]
    },
    proof: {
      eyebrow: "証明",
      headline: "すでに本番環境で稼働中",
      items: [
        { label: "アクティブなリポジトリ", value: "12+" },
        { label: "本番稼働中のエージェント", value: "4" },
        { label: "カタログコンポーネント数", value: "7" },
        { label: "アクティブなn8nパイプライン", value: "8" },
        { label: "初回MVPまでの日数", value: "3-7" }
      ]
    },
    notes: {
      eyebrow: "記録",
      headline: "マイクロエッセイ。デジタルジンの声。",
      items: [
        { title: "プロンプトは新しいIDE", body: "プロンプトを書くことは質問ではない。自然言語でのプログラミングだ。機能するプロンプトと機能しないプロンプトの差は、クリーンコードとスパゲッティコードの差と同じだ。明瞭さ、コンテキスト、制約。" }
      ]
    },
    contact: {
      eyebrow: "連絡",
      headline: "構築したいものについて話しましょう",
      email: "メール",
      github: "GitHub",
      linkedin: "LinkedIn",
      cta: "メッセージを送る"
    }
  }
}
-->


<!--
╔══════════════════════════════════════════════════════════════════════════╗
║  PAGE STRUCTURE                                                          ║
║  ┌──────────────────────────────────────────────────────────────────┐    ║
║  │  [Lang Toggle]                                                    │    ║
║  │  ┌─ HERO ─────────────────────────┬──────────────────────────┐   │    ║
║  │  │  Name · Role · Edge · CTA      │  3D Particle Canvas      │   │    ║
║  │  │  Avatar (SVG placeholder)       │  (Three.js scene)        │   │    ║
║  │  └────────────────────────────────┴──────────────────────────┘   │    ║
║  │  ┌─ ABOUT ─────────────────────────────────────────────────────┐   │    ║
║  │  │  Bento grid: p1 | p2+p3 stack | differentiator highlight     │   │    ║
║  │  └──────────────────────────────────────────────────────────────┘   │    ║
║  │  ┌─ STACK ─────────────────────────────────────────────────────┐   │    ║
║  │  │  5 bento cards: Languages | Frameworks | AI | Design | Auto  │   │    ║
║  │  │  Bento: col-span-4 | col-span-3 | col-span-5 | col-span-3 |..│   │    ║
║  │  └──────────────────────────────────────────────────────────────┘   │    ║
║  │  ┌─ PROJECTS ───────────────────────────────────────────────────┐   │    ║
║  │  │  Z-axis cascade: 3 cards with staggered rotation ±1.5deg     │   │    ║
║  │  │  Each: problem · prompt snippet (code block) · result · stack│   │    ║
║  │  └──────────────────────────────────────────────────────────────┘   │    ║
║  │  ┌─ PROCESS ────────────────────────────────────────────────────┐   │    ║
║  │  │  Pipeline visual: 4 connected steps with animated connectors  │   │    ║
║  │  └──────────────────────────────────────────────────────────────┘   │    ║
║  │  ┌─ PROOF ──────────────────────────────────────────────────────┐   │    ║
║  │  │  Horizontal counters with animated number reveal on scroll    │   │    ║
║  │  └──────────────────────────────────────────────────────────────┘   │    ║
║  │  ┌─ NOTES ──────────────────────────────────────────────────────┐   │    ║
║  │  │  Bento grid: 2×2 micro-essay cards, sub-100 words each       │   │    ║
║  │  └──────────────────────────────────────────────────────────────┘   │    ║
║  │  ┌─ CONTACT ────────────────────────────────────────────────────┐   │    ║
║  │  │  Split: form (left) | social links (right)                    │   │    ║
║  │  └──────────────────────────────────────────────────────────────┘   │    ║
║  └──────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════╝
-->

---

<!--
=================================================================
COMPONENT: Language Toggle
Type: Fixed pill, top-right, z-40
Motion: layoutId tab indicator (Framer Motion)
Spec: 3 tabs — ES (default) | EN | JP
      Active tab: bg-white/[0.08] text-white
      Inactive tab: text-slate-500 hover:text-slate-300
      Container: rounded-full bg-white/[0.04] backdrop-blur-xl
                 border border-white/[0.08] p-1 text-xs font-medium
State: selectedLang = 'es' | 'en' | 'jp'
       onSelect → setLang → re-render all i18n content
       Persist to localStorage
=================================================================
-->

<!--
=================================================================
SECTION 1: HERO
Layout: Split 50/50 — Left (text) | Right (3D canvas)
Motion:
  - Name: translate-y-8 blur-sm opacity-0 → translate-y-0 blur-0 opacity-1
    (800ms, cubic-bezier(0.32,0.72,0,1), delay: 0ms)
  - Role tag: same as above, delay: 150ms
  - Edge line: same as above, delay: 300ms
  - CTA: same as above, delay: 450ms
  - 3D scene: fades in (opacity 0→1, 1200ms, delay: 200ms)
  - Avatar: SVG placeholder circle with initials, glass border
Mobile: Stack vertically. 3D scene reduces particle count 80%.
        Height: min-h-[90dvh] (not h-screen)
=================================================================
-->

### Hero

<!--
DEV: This section is a Client Component ('use client').
     3D scene is in a separate isolated Client Component mounted
     only on non-touch devices (or reduced on mobile via particle cap).
     i18n: all text comes from i18n[lang].hero
     Avatar: use initials SVG with double-bezel glass container
-->

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   [Avatar SVG — 88×88px rounded-full glass double-bezel]            │
│                                                                     │
│   text-4xl md:text-6xl tracking-tighter leading-[0.9] font-display  │
│   Saf Ag                                                             │
│                                                                     │
│   Eyebrow pill:                                                      │
│   text-[10px] uppercase tracking-[0.2em] text-emerald-400           │
│   AI Agent Builder · Vibe-Coding Native                              │
│                                                                     │
│   text-lg text-slate-400 max-w-[42ch] leading-relaxed                │
│   Construyo agentes, apps y automatizaciones que pasan               │
│   a produccion en dias, no en meses.                                 │
│                                                                     │
│   [CTA Button — Nested icon pattern]                                │
│   rounded-full px-6 py-3 bg-emerald-500 text-black                   │
│   Ver proyectos  [→ icon circle]                                     │
│                                                                     │
│   ───────────────────────────┬──────────────────────────────────    │
│                              │  Three.js canvas                     │
│                              │  Icosahedron wireframe + particles   │
│                              │  ShaderMaterial: fresnel rim +       │
│                              │  emerald gradient, wave displacement │
│                              │  Mouse-driven rotation               │
│                              │  UnrealBloomPass (strength 0.4)      │
│                              │                                      │
│   LEFT (50%)                 │  RIGHT (50%)                         │
└─────────────────────────────────────────────────────────────────────┘
```

<!--
THREE.JS SCENE SPEC:
┌─────────────────────────────────────────────────────────────────┐
│ import * as THREE from 'three'                                    │
│ import { EffectComposer, RenderPass, UnrealBloomPass }           │
│   from 'three/addons/postprocessing/*.js'                         │
│                                                                   │
│ // Scene setup (isolated Client Component)                        │
│ const scene = new THREE.Scene()                                   │
│ scene.background = new THREE.Color('#050505')                     │
│                                                                   │
│ // Camera                                                        │
│ const camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100) │
│ camera.position.set(0, 0, 8)                                     │
│                                                                   │
│ // Icosahedron wireframe                                         │
│ const geo = new THREE.IcosahedronGeometry(2, 4)                   │
│ // ShaderMaterial with:                                          │
│ //   - vertex: wave displacement sin(time + pos.x * 3)           │
│ //   - fragment: fresnel rim + emerald gradient                  │
│ //   - uniforms: time, resolution, mousePos                      │
│ const mat = new THREE.ShaderMaterial({...})                       │
│ const mesh = new THREE.Mesh(geo, mat)                             │
│ scene.add(mesh)                                                   │
│                                                                   │
│ // Particle cloud                                                │
│ const particleGeo = new THREE.BufferGeometry()                    │
│ const particleCount = 400 // desktop; reduce to 80 on mobile     │
│ const positions = new Float32Array(particleCount * 3)             │
│ // Random sphere distribution                                    │
│ // PointsMaterial with emerald color + opacity                   │
│                                                                   │
│ // Post-processing                                               │
│ const composer = new EffectComposer(renderer)                     │
│ composer.addPass(new RenderPass(scene, camera))                   │
│ const bloom = new UnrealBloomPass(res, 0.4, 0.6, 0.85)           │
│ composer.addPass(bloom)                                           │
│                                                                   │
│ // Mouse interaction — drives rotation                            │
│ // useMotionValue (Framer) or direct ref on mouse move            │
│ // mesh.rotation.y = lerp(mesh.rotation.y, mouse.x * PI, 0.05)   │
│ // mesh.rotation.x = lerp(mesh.rotation.x, mouse.y * PI/4, 0.05) │
│                                                                   │
│ // Animation loop with THREE.Clock.getDelta()                     │
│ // Update shader uniforms: time, mousePos                         │
│ // composer.render() each frame                                   │
│                                                                   │
│ // Cleanup on unmount:                                            │
│ //   scene.traverse(child => {                                    │
│ //     if (child.geometry) child.geometry.dispose()                │
│ //     if (child.material) {                                      │
│ //       if (Array.isArray(child.material))                       │
│ //         child.material.forEach(m => m.dispose())                │
│ //       else child.material.dispose()                            │
│ //     }                                                          │
│ //   })                                                           │
│ //   renderer.dispose()                                           │
│ //   composer.dispose()                                           │
│                                                                   │
│ // Mobile: disable bloom, count=80, renderer.setPixelRatio(1)    │
│ // Touch: skip mouse tracking, use slow auto-rotation             │
└─────────────────────────────────────────────────────────────────┘
-->

---

<!--
=================================================================
SECTION 2: ABOUT
Layout: Asymmetrical bento grid
  Row: col-span-7 (headline+p1) | col-span-5 (differentiator highlight card)
  Below p1: p2 (full width or 2/3 width)
Motion: Staggered fade-up on scroll
        Each child: translate-y-12 opacity-0 → translate-y-0 opacity-1
        staggerChildren: 0.1
=================================================================
-->

### Sobre / About / 概要

<!-- DEV: 'use client' wrapper for motion. i18n[lang].about -->

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Eyebrow: Qu� construyo]                                            │
│  [H2: Agentes. Apps. Automatizaciones.]                              │
│                                                                     │
│  ┌──────────────────────────────────┬──────────────────────────────┐│
│  │                                  │  [Differentiator Card]       ││
│  │  Diseno y despliego agentes de   │  rounded-[2rem] double-bezel ││
│  │  IA que ejecutan tareas reales — │                               ││
│  │  desde scraping inteligente      │  "Entiendo el stack tecnico   ││
│  │  hasta pipelines multi-agente    │   y el producto al mismo      ││
│  │  con n8n. Cada proyecto empieza  │   nivel. No soy solo el que   ││
│  │  con un prompt y termina en      │   escribe codigo — soy el     ││
│  │  produccion.                     │   que pregunta por que."      ││
│  │                                  │                               ││
│  │  Trabajo con founders que        │  bg-emerald-500/[0.04]       ││
│  │  necesitan velocidad sin         │  border-emerald-400/20        ││
│  │  sacrificar calidad.             │                               ││
│  │                                  │                               ││
│  │  Trilingue. Remoto. Enfocado     │                               ││
│  │  en resultados, no en horas.     │                               ││
│  └──────────────────────────────────┴──────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

<!--
=================================================================
SECTION 3: STACK
Layout: Bento grid, 5 cards with varying spans
  Row 1: Languages (col-span-5) | Frameworks (col-span-3) | AI (col-span-4)
  Row 2: Design (col-span-4) | Automation (col-span-8)
Motion: Staggered scroll reveal, each card delays 80ms
Cards: Double-bezel. Each card has eyebrow + list of pills.
Pills: rounded-full px-3 py-1 text-xs bg-white/[0.06] border border-white/[0.08]
=================================================================
-->

### Stack

<!-- DEV: i18n[lang].stack for labels + items. 5 Client Component cards. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Eyebrow: Stack]                                                    │
│  [H2: Tecnologia que uso para construir]                             │
│                                                                     │
│  ┌─col-span-5──────────┐ ┌─col-span-3──┐ ┌─col-span-4───────────┐  │
│  │ LENGUAJES            │ │ FRAMEWORKS   │ │ AI / AGENTES          │  │
│  │ TypeScript           │ │ Next.js      │ │ Claude API            │  │
│  │ Python               │ │ React        │ │ GPT-4o                │  │
│  │ SQL                  │ │ FastAPI      │ │ Ollama (local)        │  │
│  │ Bash                 │ │ LangChain    │ │ LangGraph             │  │
│  │                      │ │              │ │ CrewAI                │  │
│  └──────────────────────┘ └──────────────┘ └───────────────────────┘  │
│                                                                     │
│  ┌─col-span-4──────────┐ ┌─col-span-8────────────────────────────┐  │
│  │ DISENO               │ │ AUTOMATIZACION                         │  │
│  │ Figma                │ │ n8n                                   │  │
│  │ Tailwind CSS         │ │ Railway                               │  │
│  │ Framer Motion        │ │ Supabase                              │  │
│  │ Three.js             │ │ Docker                                │  │
│  │ Sleek.design         │ │ GitHub Actions                        │  │
│  └──────────────────────┘ └───────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

<!--
=================================================================
SECTION 4: PROJECTS
Layout: Z-axis cascade — 3 cards with staggered rotation
  Card 1: rotate(-0.8deg), z-30
  Card 2: rotate(1.2deg), z-20
  Card 3: rotate(-0.4deg), z-10
  Each card slightly overlaps the next (margin-top: -2rem)
  Mobile: all rotation removed, stack vertically with standard spacing

Card structure (each):
  ┌──── Eyebrow: project name
  ├──── Problem (1 sentence, text-slate-300)
  ├──── Prompt snippet (code block, JetBrains Mono, bg-black/40, rounded-xl p-5)
  ├──── Result (1 sentence, text-emerald-400)
  ├──── Stack pills (horizontal)
  ├──── Role (1 line)
  ├──── Metrics (3 counters, horizontal, animated on scroll)
  └──── [Screenshot placeholder]

Motion: Scroll-triggered reveal via Framer Motion whileInView.
        Cards stagger with delay. Prompt block has subtle glow pulse.
=================================================================
-->

### Proyectos / Projects / 実績

<!-- DEV: i18n[lang].projects. Array of 3. Client Component for motion. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Eyebrow: Proyectos]                                                │
│  [H2: Prompt + resultado. Sin relleno.]                              │
│                                                                     │
│  ╔══════════════════════════════════════════════════════════════╗    │
│  ║  Eira Brain — Asistente IA con RAG local         ← rotate(-0.8deg)│
│  ║  ────────────────────────────────────────────────────────────    │
│  ║  PROBLEM                                                         │
│  ║  Equipos gastan 6h/semana buscando informacion en                │
│  ║  documentacion dispersa.                                         │
│  ║                                                                  │
│  ║  PROMPT                                                         │
│  ║  ┌─────────────────────────────────────────────────────────┐    │
│  ║  │ > Construime un sistema RAG que indexe mi vault de      │    │
│  ║  │ > Obsidian, responda desde el contexto local, y corra   │    │
│  ║  │ > completamente offline con Ollama.                     │    │
│  ║  └─────────────────────────────────────────────────────────┘    │
│  ║                                                   JetBrains Mono │
│  ║  RESULT: Asistente funcional en 72h. Responde con citas a        │
│  ║  documentos. 0 latencia. Privacidad total.                       │
│  ║                                                                  │
│  ║  [Python] [FastAPI] [Ollama] [ChromaDB] [Obsidian]              │
│  ║                                                                  │
│  ║  Rol: Arquitectura + implementacion completa                     │
│  ║  ───────────────────────────────────────────────                 │
│  ║  │  -93%     │  │  800+      │  │  0 cloud   │                  │
│  ║  │  busqueda │  │  docs      │  │  depend.   │                  │
│  ║  ───────────────────────────────────────────────                 │
│  ║                                                                  │
│  ║  [Screenshot placeholder — 16:9 rounded-xl glass border]        │
│  ╚══════════════════════════════════════════════════════════════╝    │
│                                                                     │
│      ╔══════════════════════════════════════════════════════╗        │
│      ║  Local RAG MD — GitHub-to-Obsidian Ingestion  ← rotate(1.2deg)│
│      ║  ... (same card structure)                            ║        │
│      ╚══════════════════════════════════════════════════════╝        │
│                                                                     │
│            ╔════════════════════════════════════════════════╗        │
│            ║  UI/UX Catalog Collector  ← rotate(-0.4deg)     ║        │
│            ║  ... (same card structure)                      ║        │
│            ╚════════════════════════════════════════════════╝        │
└─────────────────────────────────────────────────────────────────────┘
```

---

<!--
=================================================================
SECTION 5: PROCESS
Layout: 4 connected steps, horizontal on desktop, vertical on mobile
  Step pills connected by animated dashed/glowing lines
  Each step: numbered circle + label + description
Motion: Sequential reveal on scroll.
        Steps appear one at a time (staggerChildren: 0.2).
        Connector lines draw via SVG path animation (dashoffset → 0).
        Active/current step: glow pulse on numbered circle.
=================================================================
-->

### Proceso / Process / 工程

<!-- DEV: i18n[lang].process. Client Component for SVG connector animation. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Eyebrow: Proceso]                                                  │
│  [H2: Idea → prompt → iterar → ship]                                 │
│                                                                     │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌─────────┐ │
│  │           │     │           │     │           │     │         │ │
│  │  (1) Idea │────▶│(2) Prompt │────▶│(3) Iterar│────▶│(4) Ship │ │
│  │           │     │           │     │           │     │         │ │
│  │ Definimos │     │ Transformo│     │ Testeo,   │     │ Deploy. │ │
│  │ el        │     │ la idea   │     │ ajusto,   │     │ Codigo  │ │
│  │ problema  │     │ en prompts│     │ refino.   │     │ que no  │ │
│  │ real.     │     │ precisos. │     │           │     │ esta en │ │
│  │           │     │           │     │           │     │ prod no │ │
│  │           │     │           │     │           │     │ existe. │ │
│  └───────────┘     └───────────┘     └───────────┘     └─────────┘ │
│                                                                     │
│  Connector: SVG line with stroke-dasharray animation on scroll      │
│  Circle: bg-emerald-500/20 text-emerald-400 w-10 h-10 rounded-full  │
│  Active pulse: shadow-[0_0_20px_rgba(16,185,129,0.3)]              │
└─────────────────────────────────────────────────────────────────────┘
```

---

<!--
=================================================================
SECTION 6: PROOF
Layout: Horizontal stat counters, bento-style
  Desktop: 5 cards in a single row with varying widths (bento grid)
  Mobile: 2×3 or 3×2 grid
Motion: Numbers animate from 0 to final value on scroll entry
        (useMotionValue + useTransform + useSpring for smooth counting)
        Counters reveal staggered with 100ms delays
Cards: Minimal. No shadows — use border-t emerald-500/30 for visual
        separation (VISUAL_DENSITY=4, airy). Large numbers in display font.
=================================================================
-->

### Pruebas / Proof / 証明

<!-- DEV: i18n[lang].proof. Client Component for animated counters. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Eyebrow: Pruebas]                                                  │
│  [H2: Lo que ya esta en produccion]                                  │
│                                                                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────┐ │
│  │           │ │           │ │           │ │           │ │       │ │
│  │   12+     │ │    4      │ │    7      │ │    8      │ │ 3-7   │ │
│  │ Repos     │ │ Agentes   │ │ Component │ │ Pipeline  │ │ Dias  │ │
│  │ activos   │ │ en prod   │ │ catalogo  │ │ n8n       │ │ a MVP │ │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────┘ │
│                                                                     │
│  Number animation: transform: scale(1.05) on enter, spring settle   │
│  Font: display font, text-5xl, text-white tracking-tighter          │
│  Label: text-xs text-slate-500 uppercase tracking-[0.15em] mt-2     │
│  Divider: border-t border-emerald-500/20 w-8 mt-4                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

<!--
=================================================================
SECTION 7: NOTES
Layout: 2×2 bento grid of micro-essay cards
  Each card: sub-100 words, editorial tone, digital zine voice
  Card top-left: col-span-5 row-span-2 (featured)
  Card top-right: col-span-7
  Card bottom-left: col-span-6
  Card bottom-right: col-span-6
Motion: Staggered fade-in on scroll. Each card has subtle hover
        effect (border brightens, inner shadow intensifies).
Cards: Double-bezel. bg-white/[0.02]. border-white/[0.06].
       Hover: border-white/[0.12], translate-y-[-2px], duration-500 ease-out.
=================================================================
-->

### Notas / Notes / 記録

<!-- DEV: i18n[lang].notes. Client Component for hover effects. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Eyebrow: Notas]                                                    │
│  [H2: Micro-ensayos. Voz de zine digital.]                           │
│                                                                     │
│  ┌─col-span-5 row-span-2────────────────┐ ┌─col-span-7───────────┐  │
│  │                                       │ │ Offline-first es el    │  │
│  │  El prompt es el nuevo IDE            │ │ verdadero lujo         │  │
│  │                                       │ │                       │  │
│  │  Escribir prompts no es preguntar. Es │ │ Correr modelos         │  │
│  │  programar con lenguaje natural. La   │ │ localmente cambia      │  │
│  │  diferencia entre un prompt que       │ │ todo. Privacidad real. │  │
│  │  funciona y uno que no es la misma    │ │ Latencia cero. Sin     │  │
│  │  que entre codigo limpio y espagueti. │ │ quotas. Sin facturas   │  │
│  │  Claridad, contexto, constraints.     │ │ sorpresa.              │  │
│  │                                       │ │                       │  │
│  └───────────────────────────────────────┘ └───────────────────────┘  │
│                                                                     │
│  ┌─col-span-6──────────────────────────┐ ┌─col-span-6─────────────┐ │
│  │ Velocidad > perfeccion               │ │ Agentes, no chatbots    │ │
│  │                                      │ │                        │ │
│  │ Un MVP en 3 dias con fallas le gana  │ │ El 90% de 'IA en       │ │
│  │ a una app perfecta que nunca sale.   │ │ produccion' son         │ │
│  │ El mercado no espera. Tus usuarios   │ │ wrappers de ChatGPT.    │ │
│  │ tampoco. Itera en publico.           │ │ Un agente real ejecuta  │ │
│  │                                      │ │ tareas, consulta APIs,  │ │
│  │                                      │ │ escribe archivos.       │ │
│  └──────────────────────────────────────┘ └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

<!--
=================================================================
SECTION 8: CONTACT
Layout: Split 60/40 — Form (left) | Social links + text (right)
Motion: Form elements fade in staggered. Submit button has
        loading → success particle burst on completion.
Form Specs:
  - Label above input, gap-2
  - Input: rounded-2xl bg-white/[0.04] border border-white/[0.08]
           px-5 py-3 text-white placeholder:text-slate-600
           focus:border-emerald-400/40 focus:ring-1 focus:ring-emerald-400/20
  - Textarea: same, min-h-[120px] resize-y
  - Helper: text-xs text-slate-600 mt-1
  - Error: text-xs text-red-400 mt-1 (only when validation fails)
  - Submit state machine: idle → loading (skeleton/shimmer) → success (brief checkmark)
    → error (inline message)
Social links: GitHub, LinkedIn, Email as large touch-friendly pills
              with Phosphor icons, double-bezel glass containers
=================================================================
-->

### Contacto / Contact / 連絡

<!-- DEV: i18n[lang].contact. Client Component for form state management. -->

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Eyebrow: Contacto]                                                 │
│  [H2: Hablemos de lo que queres construir]                           │
│                                                                     │
│  ┌─FORM (60%)─────────────────────┬─ LINKS (40%) ────────────────┐  │
│  │                                │                               │  │
│  │  [label] Nombre                │   ┌─────────────────────────┐ │  │
│  │  [input____________________]   │   │  [icon] Email            │ │  │
│  │                                │   │  [REDACTED]          │ │  │
│  │  [label] Correo                │   └─────────────────────────┘ │  │
│  │  [input____________________]   │                               │  │
│  │                                │   ┌─────────────────────────┐ │  │
│  │  [label] Mensaje               │   │  [icon] GitHub           │ │  │
│  │  [textarea_________________]   │   │  github.com/safag        │ │  │
│  │  [textarea_________________]   │   └─────────────────────────┘ │  │
│  │                                │                               │  │
│  │  [CTA Button] Enviar mensaje   │   ┌─────────────────────────┐ │  │
│  │  ─ Submit state machine ─      │   │  [icon] LinkedIn         │ │  │
│  │  idle → loading → success      │   │  linkedin.com/in/safag   │ │  │
│  │  (brief checkmark + particle   │   └─────────────────────────┘ │  │
│  │   burst)                       │                               │  │
│  │  error → inline red message    │                               │  │
│  └────────────────────────────────┴───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```


<!--
╔══════════════════════════════════════════════════════════════════════════╗
║  COMPONENT MANIFEST — for catalog ingestion                              ║
║  These new components should be saved to uiux_catalog.json:              ║
║                                                                            ║
║  1. Portfolio Hero Split (layout)                                        ║
║  2. Ethereal Glass Double-Bezel Card (card)                              ║
║  3. Nested CTA Button (button)                                           ║
║  4. Bento Stack Grid (layout)                                            ║
║  5. Z-Cascade Project Card (card)                                        ║
║  6. Process Pipeline Connector (animation)                               ║
║  7. Animated Proof Counter (animation)                                   ║
║  8. Micro-Essay Note Card (card)                                         ║
║  9. Glass Contact Form (form)                                            ║
║  10. Three.js Particle Hero Scene (animation)                           ║
║  11. Trilingual Toggle Pill (navbar)                                     ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝
-->


<!--
╔══════════════════════════════════════════════════════════════════════════╗
║  DEV H A N D O F F   C H E C K L I S T                                   ║
║                                                                            ║
║  BEFORE BUILD:                                                            ║
║  [ ] Install deps: next, react, tailwindcss, framer-motion, three,         ║
║      @phosphor-icons/react, clsx, tailwind-merge                          ║
║  [ ] Fonts: self-host Cabinet Grotesk + Geist + JetBrains Mono             ║
║      (or load from fontsource)                                            ║
║  [ ] Tailwind config: extend theme with emerald accent, custom             ║
║      borderRadius (2rem, calc), custom easing CSS vars                    ║
║  [ ] Global CSS: noise overlay pseudo-element, ::selection styling,        ║
║      scrollbar styling, background radial gradient orbs                    ║
║  [ ] i18n: create i18n.ts with ES/EN/JP dictionary, lang state in          ║
║      localStorage, SSR-safe default to ES                                 ║
║  [ ] Three.js: verify WebGL support, fallback to static gradient           ║
║      on devices without WebGL                                              ║
║                                                                            ║
║  DURING BUILD:                                                            ║
║  [ ] Every animated element has prefers-reduced-motion support             ║
║  [ ] Hero uses min-h-[100dvh] NOT h-screen                                ║
║  [ ] Three.js scene is isolated Client Component with full cleanup         ║
║  [ ] Mobile: collapse all to single column below 768px                     ║
║  [ ] All touch targets >= 44×44px                                         ║
║  [ ] Focus rings visible on all interactive elements                       ║
║  [ ] aria-label on icon-only buttons                                       ║
║  [ ] alt text on all images and screenshot placeholders                    ║
║  [ ] Form labels use <label for="..."> pattern                            ║
║  [ ] Hover effects wrapped in @media (hover: hover) and (pointer: fine)   ║
║  [ ] No emojis anywhere in code, text, or alt                              ║
║  [ ] No Inter, Roboto, Arial fonts                                         ║
║  [ ] No purple/blue gradients or AI aesthetic                              ║
║  [ ] No 3-column equal card layouts                                        ║
║  [ ] No h-screen for full-height sections                                  ║
║  [ ] All animations use transform + opacity only                           ║
║  [ ] Backdrop-blur only on fixed/sticky elements                           ║
║  [ ] Noise overlay is fixed + pointer-events-none                          ║
║                                                                            ║
║  BEFORE SHIPPING:                                                         ║
║  [ ] Lighthouse audit: >90 perf, 100 a11y, 100 best practices              ║
║  [ ] Test at: 375px, 768px, 1024px, 1440px, 2560px                        ║
║  [ ] Test: Chrome, Firefox, Safari, iOS Safari                             ║
║  [ ] Test: keyboard navigation through all sections                        ║
║  [ ] Test: screen reader (VoiceOver / NVDA)                                ║
║  [ ] Test: prefers-reduced-motion: reduce                                  ║
║  [ ] Test: slow 3G throttling (Three.js lazy load)                         ║
║  [ ] Bundle analysis: code-split Three.js into separate chunk              ║
║  [ ] Meta tags: OG image, description, twitter card                        ║
║  [ ] robots.txt + sitemap.xml                                              ║
╚══════════════════════════════════════════════════════════════════════════╝
-->
