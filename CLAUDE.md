# JEE Main PYQ Practice Platform — Complete Project Handover & Context for Claude

> **Target Audience:** Claude (Claude Code / Anthropic LLM sessions) & Developer (Darsh)  
> **Repository:** `C:\My Stuff\Darsh\Darsh School\JEE\PYQ Practice HTML Site\practiceJEEpyqs-main`  
> **Remote Origin:** `https://github.com/DarshG-bit/practiceJEEpyqs.git` (branch: `main`)  
> **Platform Stack:** Pure Offline Client-Side HTML5, Vanilla CSS3, Vanilla ES6 JavaScript (Zero dependencies, zero build tools, zero npm runtimes; hosted directly via GitHub Pages or opened as local files).

---

## 1. Executive Summary & Project Purpose

This repository houses a high-performance, distraction-free **JEE Main Previous Year Question (PYQ) Practice & CBT Simulation Platform** built for serious aspirants targeting 99+ percentile in JEE Main.

The platform provides access to hundreds of real JEE Main previous year questions across **27 chapters** (5 Mathematics, 14 Physics, 8 Chemistry), complete with:
- **Real NTA Computer-Based Test (CBT) Exam Simulation**: Authentic full-screen interface, official NTA 5-color palette, +4 / -1 scoring, keyboard shortcuts, and verified submission workflows.
- **Practice & Learn Mode**: Instant answer verification, detailed solutions, and error logs.
- **Adaptive Practice Controls**: Configurable question counts (15, 25, 30, 50, or full chapter) and timed/untimed options.
- **Centralized Aspirant Dashboard**: Real-time aggregated statistics, active test recovery banner, subject progress meters, and priority mistake banks.
- **True AMOLED Black Mode**: A pure `#000000` dark theme with 0% OLED diode power draw, designed for 6+ hour study sessions.
- **Zero Data Loss**: All attempt histories, bookmark states, and mistake reviews persist strictly in browser `localStorage`.

---

## 2. Chronological Conversation History & Key Pivots

### Step 1: Mobile App Exploration & Clean Pivot
- **Initial Request**: Exploring whether to wrap or rewrite the platform as an Android application.
- **Decision & Pivot**: The user decided against native mobile rewriting (`"ok changed mind bout app remove all the app files leave web files"`). All Android wrapper files/scaffolding were purged to keep the codebase 100% focused on an ultra-fast, offline-capable static web stack.

### Step 2: Practice Configuration & Question Count Selector
- **User Feedback**: In the random test generator and chapter practice launcher screens, students needed granular control over question counts (e.g., 15, 25, 30, 50, or all questions) alongside practice timer settings.
- **Implementation**:
  - Added question count pill selectors to every practice launcher across all chapters.
  - Dynamically recalculates estimated test duration based on selected question count and difficulty distribution.

### Step 3: Eliminating Navy Blue — The AMOLED Black Mandate
- **User Feedback**: *"The dark mode right now is more like navy blue doesn't look too good on amoleds..."*
- **The Problem**: Prior dark themes used Tailwind-like slate/navy tones (`#1e293b`, `#0f172a`, `#172554`, `#1e3a8a`, `#0c1929`), causing OLED screens to keep pixels lit, creating eye strain in dark rooms and draining battery.
- **Implementation**:
  - Replaced all dark mode backgrounds with **True AMOLED Black (`#000000`)**.
  - Surface elevations styled in neutral dark charcoals (`#121214`, `#18181b`, `#222224`, `#27272a`).
  - Created an automated verification script (`verify_amoled.py`) that strictly scans all 83 HTML files. Current status: **0 navy blue occurrences across the entire repository**.

### Step 4: De-AI-ifying the UI & Professional Aesthetic
- **User Feedback**: *"the ui is too ai looking make it little professional pls reduce the neonish colors and de ai the ui a little professional lookin"*
- **The Problem**: Generic AI designs often overuse saturated neon gradients, fuzzy glow drop-shadows, unnecessary decorative emojis, and decorative kicker tags.
- **Implementation**:
  - Eliminated gradient text, decorative emojis, zero-blur drop shadows, and ornamental eyebrows/kickers.
  - Adopted an **"Operate / Read"** design language: clean borders (`1px solid var(--border)`), functional color tokens (subdued blues, amber warning, emerald success), sharp typography hierarchy, and `font-variant-numeric: tabular-nums` for timers and counters.

### Step 5: Real CBT Exam Mode (NTA JEE Main Simulation)
- **User Request**: Implement a true-to-life CBT exam simulator replicating the National Testing Agency (NTA) JEE Main test interface.
- **Features Implemented**:
  1. **Official NTA 5-Color Question Palette**:
     - *Not Visited*: `#e2e8f0` (Gray/White)
     - *Not Answered*: `#dc2626` (Red)
     - *Answered*: `#16a34a` (Green)
     - *Marked for Review*: `#7c3aed` (Purple)
     - *Answered & Marked for Review*: `#7c3aed` with green indicator
  2. **Official NTA Scoring**: `+4` for correct, `-1` for incorrect, `0` for unattempted.
  3. **Full Keyboard Hotkey Navigation**:
     - `1` / `2` / `3` / `4`: Select Options A / B / C / D
     - `S`: Save & Next
     - `M`: Mark for Review & Next
     - `C`: Clear Response
     - `P`: Previous Question
     - `N`: Next Question
  4. **Submission Confirmation Modal**: Complete summary matrix showing counts across all 5 states before final exam submission.
  5. **Auto-Submit on Timer Expiry**: Automatically collects and grades responses when time reaches `00:00`.

### Step 6: Centralized Aspirant Dashboard on Home Portal (`index.html`)
- **User Request**: Transform the root landing page into a centralized mission-control dashboard.
- **Features Implemented**:
  1. **4 Core Aggregated Metrics**: Total Questions Attempted, Overall Accuracy %, Total Study Time Logged, and Starred / Marked Questions.
  2. **Active Test Recovery Banner**: Detects incomplete test sessions from `localStorage` and provides a 1-click "Resume Incomplete Test" launcher.
  3. **Subject Progress Meters**: Visual progress bars showing syllabus coverage and accuracy across Mathematics, Physics, and Chemistry.
  4. **Priority Revision List**: Fast access to chapters with unreviewed mistakes or bookmarked questions.

### Step 7: Creation of the Maintenance Skill (`pyq-sheet-manager`)
- **Directory**: `.agents/skills/pyq-sheet-manager/`
- **Living Document Rule**: `SKILL.md` must be updated in the same commit whenever customizations, scoring logic, or themes are altered.
- **Verification Scripts**: Includes `verify_amoled.py` to safeguard against theme regression.

### Step 8: Integration of Impeccable Design Engine
- **Skill Added**: Located in `.agents/skills/impeccable/`.
- **Artifacts Established**:
  - `PRODUCT.md`: Canonical product specification (vision, user personas, positioning, operating context, principles).
  - `DESIGN.md`: Token schema following Google Labs Design standards (colors, typography, rounded scale, spacing).
- **Interactive Syllabus Explorer**: Built into `index.html` with real-time fuzzy chapter search, subject tabs (`All 27`, `Maths 5`, `Physics 14`, `Chemistry 8`), priority tags (`Class A/B/C`), and dynamic attempt badges.
- **Impeccable Doctor & Hooks**: Ran `/impeccable doctor` (0 errors, 0 warnings) and enabled automated design hooks via `.impeccable/config.json` and `.codex/hooks.json` to review UI changes on save.

---

### Step 9: UI/UX Modernization, Elevated AMOLED & Complete Exam Architecture Overhaul
- **User Feedback & Attached Proofs (8 Screenshots & 20 Action Items)**:
  - **Pic 1**: Removed duplicate dark mode toggle buttons and fixed raw `&middot;` in Revision Bank.
  - **Pic 2**: Added Custom Time duration input (`[ 45 ] minutes`) alongside 30/60/90/180m and Untimed in Simulate Exam modal.
  - **Pic 3**: Eliminated wasted desktop screen margins by widening chapter practice panels to `1040px` with generous padding.
  - **Pic 4 & Pic 8**: Overhauled previous attempts table into modern structured cards (`.att-card`) with dedicated action buttons and full list JSON export.
  - **Pic 5**: Replaced plain hyperlinks `Question Types ->` and `Type Notes ->` with sleek modern action chips (`.btn-mat`).
  - **Pic 6**: Fixed invisible dark mode typing boxes (`.ed`, `textarea`, `input`) with elevated `#121215` background and `#2e2e34` borders.
  - **Pic 7**: Fixed blue-on-blue text visibility on primary buttons (`color: #ffffff !important`).
  - **Pic 7**: Re-introduced Subject-First Chapter Navigation tabs (`All 27`, `Maths 5`, `Physics 14`, `Chemistry 8`) with instant search filter.
  - **CBT vs Practice Rules (Items 7, 8, 9)**:
    - *CBT Exam*: Strict non-continuable mode. After submission, attempts are ONLY reviewable ('Review Marks & Mistakes'). Immediate question-level answer checking is completely blocked. Leaving/reloading during an active exam forfeits the session to prevent cheating.
    - *Practice Mode*: Continuable anytime even after submission ('Continue Practice'). Per-question instant checking is allowed. Students can leave and resume anytime.
  - **Theme Toggle Icon**: Replaced emojis (`🌙`/`☀️`) with clean Apple-style SVG stroke outlines.
  - **Test History Drawer**: Added slide-out history drawer on `index.html` with aggregated stats across all 27 chapters, CBT vs Practice filters, and global JSON export/clear.
  - **Upstream Sync**: Documented manual upstream sync runbook against `rupinderiitb/practicemakesperfect.git`.

---

## 3. Repository Architecture & File Layout

```text
practiceJEEpyqs-main/
├── CLAUDE.md                       # This handover & instructions file for Claude
├── PRODUCT.md                      # Canonical product specification
├── DESIGN.md                       # Canonical design system tokens & guidelines
├── index.html                      # Redesigned Home Portal, Dashboard & Chapter Explorer
├── patch_all.py                    # Multi-file automated updater script with GC
├── .gitignore                      # Git ignore rules for cache & local settings
├── .codex/
│   └── hooks.json                  # Automated Impeccable design hook configuration
├── .impeccable/
│   └── config.json                 # Project design detector settings
├── .agents/
│   └── skills/
│       ├── pyq-sheet-manager/      # Maintenance skill & runbook
│       │   ├── SKILL.md            # Living operational manual
│       │   └── scripts/
│       │       └── verify_amoled.py# Automated AMOLED black verification utility
│       └── impeccable/             # Impeccable design engine & reference docs
├── Maths/                          # Mathematics (5 Chapters)
│   ├── <Chapter> PYQ Practice.html # Interactive practice & CBT sheet
│   ├── index.html                  # Mathematics subject index
│   └── materials/                  # Subtopic Question Types and Type Notes
├── Physics/                        # Physics (14 Chapters)
│   ├── <Chapter> PYQ Practice.html
│   ├── index.html                  # Physics subject index
│   └── materials/
└── Chemistry/                      # Chemistry (8 Chapters)
    ├── <Chapter> PYQ Practice.html
    ├── index.html                  # Chemistry subject index
    └── materials/
```

### Critical File Size & Memory Note
Each `<Chapter> PYQ Practice.html` contains hundreds of high-resolution scientific and mathematical diagrams embedded directly as **base64 encoded strings** (`data:image/png;base64,...`).
- Files like `Amines PYQ Practice.html` (13 MB), `General Organic Chemistry PYQ Practice.html` (11.2 MB), `Current Electricity PYQ Practice.html` (8.3 MB), and `Semiconductors PYQ Practice.html` (8 MB) are very large.
- **Rule for Python Scripts**: When reading/writing multiple practice files in a script, always release file references and call `import gc; gc.collect()` at the end of each iteration to prevent Python `MemoryError` heap exhaustion.
- **Never strip or truncate base64 images**: Aspirants cannot solve organic chemistry or physics questions without these diagrams.

---

## 4. LocalStorage Schema (Zero-Data-Loss Invariant)

The application maintains state entirely in the client browser across several key namespaces. **Never rename, break, or delete these keys**:

| Key Pattern | Description | Structure / Values |
|---|---|---|
| `pyq_dark` | Global dark mode toggle | `"true"` or `"false"` |
| `pyq_cbt_mode` | Global CBT mode toggle | `"true"` or `"false"` |
| `pyq_qcount_<id>` | User-selected question count | Number string (e.g. `"25"`, `"50"`, `"all"`) |
| `pyqh_<chapter_id>` | Historical test attempts | JSON array of attempt records (`score`, `maxScore`, `accuracy`, `date`, `timeTakenSec`) |
| `pyqs_<chapter_id>` | Bookmarked / Starred questions | JSON array of question IDs (`["q1", "q14", ...]`) |
| `pyqw_<chapter_id>` | Mistake bank (questions answered wrongly) | JSON array of question IDs |
| `pyq_active_session` | In-progress test recovery session | JSON object (`chapterId`, `chapterTitle`, `mode`, `answers`, `visited`, `marked`, `timeRemainingSec`) |

---

## 5. Upstream Sync Runbook (Original Repo: rupinderiitb/practicemakesperfect)

The repository originates from `https://github.com/rupinderiitb/practicemakesperfect.git` (`upstream`).  
Because local enhancements (CBT mode, AMOLED styles, dashboard, custom timers) modify all HTML files, a standard git merge would cause hundreds of merge conflicts. Instead, use the following clean sync workflows:

### Method A: One-Click GitHub Actions (Recommended)
1. Go to your GitHub repository: `https://github.com/DarshG-bit/practiceJEEpyqs/actions`.
2. Click **Sync Upstream & Auto-Patch** in the left sidebar.
3. Click **Run workflow** -> Select `main` branch -> Click green **Run workflow** button.
4. The workflow fetches upstream changes, merges new questions, re-applies `patch_all.py`, runs tests, and pushes cleanly.

### Method B: Manual Sync via Terminal (Powershell)
Run the following commands in the repository root:
```powershell
# 1. Fetch latest upstream questions & assets
git fetch upstream main

# 2. Check out upstream subject files (preserves git history while pulling content)
git checkout upstream/main -- Chemistry Maths Physics

# 3. Re-run the automated patcher to re-inject AMOLED, CBT engine & UI modernizations
python patch_all.py

# 4. Verify 0 AMOLED violations & 0 Impeccable regressions
python .agents/skills/pyq-sheet-manager/scripts/verify_amoled.py
.\.agents\skills\impeccable\scripts\impeccable.cmd detect index.html

# 5. Commit and push
git add -A
git commit -m "chore: sync with upstream and re-patch all chapters"
git push origin main
```

---

## 6. Invariants & Rules for Claude

When editing, adding features, or maintaining this codebase, you **MUST** adhere strictly to the following rules:

### Rule 1: True AMOLED Black (`#000000`) Only
- Dark mode background is strictly `#000000`.
- Dark mode elevated surfaces: `#121214` (cards), `#18181b` (popovers/dropdowns), `#222224` (borders/active states).
- **Zero tolerance for navy blue**: Never introduce `#1e293b`, `#0f172a`, `#172554`, `#1e3a8a`, or `#0c1929` into dark mode blocks. Always run `python .agents/skills/pyq-sheet-manager/scripts/verify_amoled.py` after editing styles.

### Rule 2: NTA CBT Simulation Accuracy
- Keep the official NTA +4 / -1 scoring model.
- Keep the 5 official question status colors and badges.
- Keep keyboard hotkeys operational (`1`-`4`, `S`, `M`, `C`, `P`, `N`).
- Always show the submission confirmation review modal before recording final marks.

### Rule 3: Living Document Rule for `SKILL.md`
- Whenever customizations, UI patterns, or scoring logic are updated, update [.agents/skills/pyq-sheet-manager/SKILL.md](file:///C:/My%20Stuff/Darsh/Darsh%20School/JEE/PYQ%20Practice%20HTML%20Site/practiceJEEpyqs-main/.agents/skills/pyq-sheet-manager/SKILL.md) in the same commit.

### Rule 4: Impeccable Design Standards
- Follow `PRODUCT.md` and `DESIGN.md`.
- Mode is **Operate / Read**: Prioritize readability, scanability, and distraction-free learning.
- Ensure all text-to-background contrast ratios satisfy WCAG AA (≥ 4.5:1).
- Use `tabular-nums` for all countdown timers, scores, question indices, and metrics.
- Before committing UI changes, run:
  ```powershell
  .\.agents\skills\impeccable\scripts\impeccable.cmd detect --json index.html
  ```

### Rule 5: Pure Static Offline Guarantee
- Do not introduce server-side scripts, external runtime npm packages, or bundlers (Vite/Webpack).
- The site must continue to run flawlessly offline when opened directly from disk (`file:///...`) or hosted on GitHub Pages.

---

## 7. Verification Commands & Runbook

### 1. Verify AMOLED Theme (0 Navy Blue Violations)
```powershell
python .\.agents\skills\pyq-sheet-manager\scripts\verify_amoled.py
```

### 2. Verify Impeccable Design Quality
```powershell
.\.agents\skills\impeccable\scripts\impeccable.cmd doctor --json
.\.agents\skills\impeccable\scripts\impeccable.cmd detect index.html
```

### 3. Propagating Global Changes Across All 83 Files
Use `patch_all.py` (which includes garbage collection). Always test on 1 file first before batching across the entire repository.
