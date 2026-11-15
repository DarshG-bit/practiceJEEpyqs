---
name: JEE PYQ Practice Design System
description: High-performance, distraction-free preparation and CBT testing system for JEE Main aspirants
colors:
  bg-amoled: "#000000"
  surface-dark: "#0a0a0c"
  surface-dark-subtle: "#111114"
  border-dark: "#222224"
  border-dark-subtle: "#27272a"
  text-dark-primary: "#ffffff"
  text-dark-secondary: "#e4e4e7"
  text-dark-muted: "#a1a1aa"
  bg-light: "#f8fafc"
  surface-light: "#ffffff"
  surface-light-subtle: "#f1f5f9"
  border-light: "#e2e8f0"
  border-light-subtle: "#cbd5e1"
  text-light-primary: "#0f172a"
  text-light-secondary: "#334155"
  text-light-muted: "#475569"
  primary: "#2563eb"
  primary-hover: "#1d4ed8"
  primary-dark: "#3b82f6"
  primary-light-bg: "#081a36"
  primary-light-text: "#93c5fd"
  primary-active-text: "#1e40af"
  maths-accent: "#2563eb"
  physics-accent: "#6366f1"
  chem-accent: "#059669"
  success: "#16a34a"
  success-bg-light: "#dcfce7"
  success-bg-dark: "#052e16"
  error: "#dc2626"
  error-dark: "#f87171"
  error-bg-light: "#fee2e2"
  error-bg-dark: "#450a0a"
  review-purple: "#9333ea"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  h1:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.025em"
  h2:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "19px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  h3:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  h4:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "14.5px"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0"
  body-sm:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  caption:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "12.5px"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0"
  caption-sm:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "11.5px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.04em"
  badge:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif"
    fontSize: "11px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.04em"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "14px"
  lg: "20px"
  xl: "28px"
---

## Overview

The JEE PYQ Practice Design System is built for students solving rigorous, high-stakes engineering entrance problems. Designed under Impeccable's **Operate** mode, every component, typography scale, and color role prioritizes scanability, zero visual fatigue, and distraction-free active recall.

## Colors

- **AMOLED Pitch Black (`#000000`)**: Enforced for dark mode to guarantee 100% OLED diode switch-off.
- **Card Surfaces (`#0a0a0c`, `#111114`)**: Subtle elevations with clean contrast against pure black.
- **Borders (`#222224`, `#27272a`)**: 1px single-declaration structure without blurry drop shadows.
- **Subject Identifiers**:
  - Mathematics: Cobalt Blue (`#2563eb` light / `#3b82f6` dark)
  - Physics: Deep Indigo / Violet (`#6366f1` light / `#818cf8` dark)
  - Chemistry: Emerald Green (`#059669` light / `#10b981` dark)
- **Official NTA Examination Palette**:
  - Answered: Green (`#16a34a`)
  - Not Answered: Red (`#ef4444`)
  - Not Visited: Neutral Slate (`#e2e8f0` light / `#1c1c1f` dark)
  - Marked for Review: Violet (`#9333ea`)
  - Answered & Marked for Review: Violet (`#9333ea`) with Green badge

## Typography

- **Font Family**: Workhorse UI stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif`.
- **Numerals & Metrics**: `font-variant-numeric: tabular-nums` applied to timers, scores, question counts, and statistics to prevent layout shifts.
- **Line Length**: Paragraphs and question stems constrained to `65–75ch` for optimal reading comprehension.
- **Letter Spacing**: Subtle `-0.02em` to `-0.025em` for headings; `0` for body and UI labels.

## Layout

- **Container**: Max width 1080px, centered with generous 24px side padding on desktop, 16px on mobile.
- **Rhythm**: Group related controls closely; provide generous vertical breathing room between major sections.
- **Responsive Architecture**: Breakpoint-driven grids (`auto-fit, minmax(...)`) ensuring seamless mobile-to-desktop transitions without horizontal scrolling.

## Elevation & Depth

- Single-layer elevation declaration: crisp 1px border.
- Floating modals use soft ambient blur (`backdrop-filter: blur(4px)`) and a restrained backdrop (`rgba(0, 0, 0, 0.7)`).
- Hard offset shadows and blurry zero-offset halos are strictly banned.

## Shapes

- Small interactive controls (pills, badges): `4px` radius.
- Buttons and inputs: `8px` radius.
- Cards, panels, and modals: `12px` radius.

## Components

- **Header**: Minimalist bar displaying title, subject badge, and high-contrast theme toggle.
- **Dashboard Strip**: Horizontal key metrics (Questions, Accuracy %, Study Time, Revision Bank) with tabular numerals.
- **Subject Cards**: Clear subject headers with syllabus progress bar and chapter count pill.
- **Mode Selector Cards**: Radio cards distinguishing Real CBT Exam Mode (+4/−1) from Practice & Learn Mode.
- **Question Palette**: Circular and rounded square buttons reflecting the official 5 NTA states.

## Do's and Don'ts

### Do
- Always use `#000000` for dark mode background.
- Keep `font-variant-numeric: tabular-nums` for timers, counts, and metrics.
- Ensure all clickable controls have a minimum touch target of 44x44px.
- Use clean, authored SVG icons instead of emojis.

### Don't
- Don't use navy blue (`#1e293b`, `#0f172a`) in dark mode.
- Don't use decorative emojis or AI-style gradient text.
- Don't add decorative drop shadows under borders.
- Don't use kickers or eyebrows above headings.
