---
name: pyq-sheet-manager
description: >-
  Operating guide and automated maintenance runbook for the JEE PYQ Practice web portal.
  Use when adding new chapters, modifying dark mode or AMOLED styles, updating CBT exam mode,
  syncing the centralized portal dashboard, or whenever the user updates their customizations.
---

# JEE PYQ Sheet Manager & Maintenance Skill

This skill documents the architecture, maintenance workflows, quality standards, and automated scripts for the JEE Main Previous Year Question (PYQ) Practice platform.

> [!IMPORTANT]
> **Living Document Rule**: Whenever the user requests updates to their customizations (such as theme tweaks, exam features, scoring formulas, or UI layout), you **MUST** update this `SKILL.md` file in the same commit to keep the operational runbook current.

---

## 1. Project Architecture

The application is a pure, zero-dependency client-side web application designed to run 100% offline or hosted on GitHub Pages:

```text
practiceJEEpyqs-main/
├── index.html                      # Centralized Aspirant Dashboard & Mock Test Launcher
├── patch_all.py                    # 1-step automated patcher for all 83 workspace files
├── Maths/                          # Mathematics (5 Chapters)
│   ├── <Chapter> PYQ Practice.html # Interactive practice & CBT sheet with base64 diagrams
│   ├── index.html                  # Subject chapter listing
│   └── materials/                  # Subtopic Question Types and Type Notes
├── Physics/                        # Physics (14 Chapters)
├── Chemistry/                      # Chemistry (8 Chapters)
└── .agents/
    └── skills/
        └── pyq-sheet-manager/
            ├── SKILL.md            # This runbook
            └── scripts/
                └── verify_amoled.py # Quality validation script
```

---

## 2. Design Invariants & Standards

Every file in the repository must strictly follow these rules:

### A. True AMOLED Black (`#000000`)
- **Pitch Black Backgrounds**: The dark mode background must be `#000000` so OLED display diodes turn off 100%.
- **Zero Navy Blue**: Never use navy-blue or slate-blue (`#1e293b`, `#0f172a`, etc.) for dark mode containers or surfaces.
- **Elevated Surfaces**: Modals, cards, and dropdowns use `#0a0a0c` or `#111114`.
- **Borders & Dividers**: Crisp dark borders use `#222224` or `#27272a`.
- **Text & Headings**: Main headings use `#ffffff` (crisp white), body text uses `#e4e4e7`, and muted subtext uses `#94a3b8`.

### B. "De-AI" Professional Aesthetic
- **No Gimmicks**: Avoid AI-style decorative emojis (`🚀`, `💡`, `🎲`).
- **Restrained Accents**: Use focused primary blue (`#2563eb` / dark `#3b82f6`) and green (`#16a34a`). Avoid neon glowing borders, heavy drop shadows, or gradient text.

### C. Official NTA CBT Exam Simulation
- **Two Distinct Modes**:
  1. *Real CBT Exam Mode*: Strict exam simulation (+4 / −1 marking, no instant check buttons, official palette, submission confirmation modal).
  2. *Practice & Learn Mode*: Instant per-question checking, retry mistakes, and view solutions immediately.
- **Official NTA 5-State Color Palette**:
  - `an` (Green `#16a34a`): Answered
  - `na` (Red `#ef4444`): Not Answered
  - `nv` (Gray `#e2e8f0` / dark `#1c1c1f`): Not Visited
  - `mk` (Purple circle `#9333ea`): Marked for Review
  - `am` (Purple circle with green badge): Answered & Marked for Review (evaluated)
- **Scoring Engine**: $+4$ for correct, $-1$ negative marking for wrong options/numericals, $0$ for unattempted.
- **Scorecard**: SVG Donut chart breakdown, accuracy percentage, time per question, and filterable question review cards (`All`, `Incorrect Only`, `Correct Only`, `Unattempted`).

---

## 3. Aspirant Data & Storage Schema

The portal stores student progress in browser `localStorage`. Do not rename or wipe these keys during script or sheet updates:

| Key Pattern | Purpose | Example |
| :--- | :--- | :--- |
| `pyq_<Chapter Name> PYQ Test` | Active session in progress (current question, answers, elapsed seconds) | `pyq_General Organic Chemistry PYQ Test` |
| `pyqh_<Chapter Name> PYQ Test` | Attempt history log (stores last 25 submitted tests with scores & accuracy) | `pyqh_Matrices PYQ Test` |
| `pyqs_<Chapter Name> PYQ Test` | Starred questions bookmark bank | `pyqs_Current Electricity PYQ Test` |
| `pyqw_<Chapter Name> PYQ Test` | Unresolved mistake bank (questions answered incorrectly) | `pyqw_Amines PYQ Test` |
| `jee_theme` | Theme preference (`dark` or `light`) | `jee_theme` = `"dark"` |

---

## 4. Maintenance Workflows

### Workflow 1: Adding a New Chapter Practice Sheet
1. Place the new `<Chapter Name> PYQ Practice.html` in its subject folder (`Maths/`, `Physics/`, or `Chemistry/`).
2. Run the automated patcher:
   ```powershell
   python patch_all.py
   ```
3. The patcher will automatically:
   - Inject the AMOLED dark mode stylesheets and print CSS.
   - Inject the Test Mode selector (Real CBT vs Practice) and Question Count sampler.
   - Inject the CBT Engine, hotkeys, submission modal, and SVG donut scorecard.
   - Discover the new chapter and register it into `CHAPTER_POOL` inside `index.html`.
4. Run the validator:
   ```powershell
   python .agents/skills/pyq-sheet-manager/scripts/verify_amoled.py
   ```

### Workflow 2: Updating Global Styles or Customizations
1. Modify `DARK_MODE_CSS`, `TEST_MODE_AND_QCOUNT_HTML`, or `ENHANCED_PRACTICE_SCRIPT` inside `patch_all.py`.
2. Compile and run:
   ```powershell
   python -m py_compile patch_all.py
   python patch_all.py
   ```
3. Verify changes with `verify_amoled.py`.
4. Update this `SKILL.md` to reflect the updated customization.
5. Commit and push:
   ```powershell
   git add -A
   git commit -m "feat: <customization description>"
   git push origin main
   ```
