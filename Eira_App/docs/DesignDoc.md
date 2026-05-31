# Design Doc: Eira Glass Workspace

## 1. Visual Identity

- **Themes**: Dark Mode (Default), Neural Blue (#4fc3f7), Glass White (#ffffff10).
- **Core Elements**: Liquid Glass buttons, deep blur backgrounds (backdrop-filter: blur(20px)).

## 2. Layout Structure

- **Sidebar**: 60px slim collapsible sidebar with icons for:
  - 💬 Chat (Neural Link)
  - 🗒️ Notes (Archive)
  - 📅 Calendar (Timeline)
  - ⚡ Habits (Starlight)
- **Main View**: Floating glass card (Isolate layer).

## 3. Component Aesthetics

- **Buttons**: `LiquidButton` (existing) for primary actions.
- **Inputs**: Transparent fields with neon border-bottom focus.
- **Cards**: Soft rounded corners (16px), 1px solid border (#ffffff20).

## 4. Animations

- **Spring Transitions**: All module switches use Framer Motion or CSS transitions (Ease-in-out).
- **Micro-interactions**: Hovering over notes gives a subtle "elevation" glow.
