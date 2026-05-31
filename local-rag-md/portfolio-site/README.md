# safagix — Portfolio

Portfolio personal construido con Next.js 15, Tailwind CSS v4, Framer Motion y Three.js.

## Stack

- **Framework:** Next.js 15 (App Router)
- **Estilos:** Tailwind CSS v4
- **Motion:** Framer Motion (spring physics, scroll reveals, staggered animations)
- **3D:** Three.js (custom ShaderMaterial, particle system, bloom post-processing)
- **i18n:** Trilingue ES / EN / JP con localStorage
- **Deploy:** Vercel

## Estructura

```
src/
├── app/
│   ├── globals.css        # Design tokens, noise overlay, gradient orbs
│   ├── layout.tsx          # Metadata, root layout
│   └── page.tsx            # Main page composer
├── components/
│   ├── Section.tsx         # Reusable section wrapper (Eyebrow + Headline)
│   ├── LangToggle.tsx      # Trilingual pill toggle (ES/EN/JP)
│   ├── HeroSection.tsx     # Split hero with Three.js particle canvas
│   ├── AboutSection.tsx    # Asymmetrical bento about section
│   ├── StackSection.tsx    # Bento grid of tech stack cards
│   ├── ProjectsSection.tsx # Z-axis cascade project cards
│   ├── ProcessSection.tsx  # 4-step pipeline with SVG connectors
│   ├── ProofSection.tsx    # Animated stat counters
│   ├── NotesSection.tsx    # Micro-essay zine cards
│   └── ContactSection.tsx  # Glass form + social link pills
└── lib/
    ├── i18n.tsx            # Complete ES/EN/JP dictionary + provider
    └── utils.ts            # cn() helper (clsx + tailwind-merge)
```

## Desarrollo

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # Production build
```

## Diseño

Sistema de diseño Ethereal Glass sobre OLED black (#050505):
- Acento esmeralda como color unico
- Arquitectura Double-Bezel (Doppelrand) en todas las cards
- Patron Button-in-Button para CTAs
- Animaciones con custom cubic-bezier y spring physics
- Prefers-reduced-motion en todos los elementos animados
- Bento grid asimetrico (sin 3-columnas iguales)

## Deploy

[portfolio-site-vert-one.vercel.app](https://portfolio-site-vert-one.vercel.app)

## Licencia

MIT
