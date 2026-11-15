import json
"""
Automated 1-Step Patcher for JEE PYQ Practice
Applies all custom improvements:
  1. Automated Pre-Patch Backup
  2. Question Option Alignment & Image Redistribution
  3. Type Notes 'Save as PDF' & Optimized Print Pagination (No wasted space, row breaks, per-type page breaks)
  4. Comprehensive Dark Mode (Pills, Filter Boxes, MathML, Diagrams, Question Palette, Navigation)
  5. Subject & Chapter Index Styling (Search box, Legend, Dark Strip Cards with Class Accents)
"""

import os
import re
import sys
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------
# 1. BACKUP HELPER
# -------------------------------------------------------------
def make_backup(file_path):
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    backup_path = os.path.join(ROOT_DIR, "backup", rel_path)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)

# -------------------------------------------------------------
# 2. OPTION IMAGE REDISTRIBUTION
# -------------------------------------------------------------
def fix_option_images_in_file(content):
    modified = False
    
    def redist_opts(match):
        nonlocal modified
        q_text = match.group(0)
        
        opts_match = re.search(r'(<div class="opts"[^>]*>)(.*?)(</div>\s*</div>)', q_text, re.DOTALL)
        if not opts_match:
            return q_text
        
        opts_inner = opts_match.group(2)
        opt_divs = list(re.finditer(r'<div class="o" data-o="([A-D])"[^>]*>(.*?)</div>', opts_inner, re.DOTALL))
        if len(opt_divs) != 4:
            return q_text
            
        opt_imgs = []
        for d in opt_divs:
            imgs = re.findall(r'<img[^>]+>', d.group(2))
            opt_imgs.append(imgs)
            
        total_imgs = sum(len(imgs) for imgs in opt_imgs)
        # Bug: 4 images dumped into D, or 0 in A/B and stacked in C/D
        if total_imgs == 4 and (len(opt_imgs[0]) == 0 or len(opt_imgs[1]) == 0):
            all_found_imgs = []
            for imgs in opt_imgs:
                all_found_imgs.extend(imgs)
            if len(all_found_imgs) == 4:
                new_opts = ""
                for i, label in enumerate(['A', 'B', 'C', 'D']):
                    raw_text = re.sub(r'<img[^>]+>', '', opt_divs[i].group(2)).strip()
                    lbl_span = f'<span class="ol">{label}</span>'
                    if '<span class="ol">' in raw_text:
                        clean_text = re.sub(r'<span class="ol">.*?</span>', '', raw_text).strip()
                    else:
                        clean_text = raw_text
                    
                    inner = f'{lbl_span} {all_found_imgs[i]}' if not clean_text else f'{lbl_span} {clean_text} {all_found_imgs[i]}'
                    new_opts += f'<div class="o" data-o="{label}">{inner}</div>'
                
                new_q = q_text[:opts_match.start(2)] + new_opts + q_text[opts_match.end(2):]
                modified = True
                return new_q
        return q_text

    new_content = re.sub(r'<div class="q" id="q\d+"[^>]*>.*?</div>\s*</div>', redist_opts, content, flags=re.DOTALL)
    return new_content, modified

# -------------------------------------------------------------
# 3. TYPE NOTES: 'SAVE AS PDF' & PRINT PAGINATION
# -------------------------------------------------------------
PERFECT_PRINT_CSS = """
/* --- Clean Print & Save as PDF Styling (Workbook layout) --- */
@media print {
  @page {
    margin: 8mm 10mm;
    size: A4 portrait;
  }
  body {
    background: #fff !important;
    color: #000 !important;
    font-size: 13.5pt !important;
    line-height: 1.55 !important;
    padding-bottom: 0 !important;
  }
  .page {
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    box-shadow: none !important;
  }
  
  /* HIDE ALL NAVIGATION, BUTTONS, INSTRUCTIONS */
  .top, #back, .btn, button, .noprint, .how, details, #types, #types+ul, #sym,
  .theme-btn, .top-links, a[href="#top"], .tpdf, .rev, .sm, .back, header {
    display: none !important;
  }

  /* HEADINGS */
  h1.t { font-size: 20pt !important; margin: 0 0 10px !important; color: #1f4e8c !important; }
  h2 { font-size: 15.5pt !important; margin: 14px 0 6px !important; color: #1f4e8c !important; break-after: avoid !important; page-break-after: avoid !important; }
  h3 { font-size: 13.5pt !important; margin: 10px 0 4px !important; break-after: avoid !important; page-break-after: avoid !important; }
  p { font-size: 12.5pt !important; margin: 4px 0 !important; }

  /* SPECIFIC TYPE PRINTING: HIDE UNSELECTED TYPES WHEN BODY HAS .one */
  body.one section.typ:not(.pick) {
    display: none !important;
  }
  
  /* CREATOR SKIP CLASS FOR MAIN PDF */
  section.typ.pr-skip {
    display: none !important;
  }

  /* EACH TYPE STARTS ON A NEW PAGE */
  section.typ {
    border-top: 2.5px solid #1f4e8c !important;
    padding-top: 10px !important;
    margin-top: 14px !important;
    break-inside: auto !important;
    page-break-inside: auto !important;
  }
  section.typ ~ section.typ {
    break-before: page !important;
    page-break-before: page !important;
  }

  /* TABLES: ROW-LEVEL BREAKING SO NO SPACE IS WASTED ON PREVIOUS PAGE */
  .gt, table {
    width: 100% !important;
    border-collapse: collapse !important;
    break-inside: auto !important;
    page-break-inside: auto !important;
    margin: 8px 0 !important;
    font-size: 12.5pt !important;
  }
  .gt tr, tr {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }
  .gt td, td, th {
    border: 1.5px solid #64748b !important;
    padding: 8px 10px !important;
    font-size: 12.5pt !important;
    color: #000 !important;
    background: #fff !important;
  }
  .gt tr:first-child td, .gt td:first-child {
    background: #f1f5fb !important;
    font-weight: 700 !important;
    color: #000 !important;
  }

  /* EDITABLE BOXES / USER WRITTEN NOTES: SPACIOUS WORKBOOK FEEL */
  .ed {
    border: 1.5px solid #64748b !important;
    background: #fff !important;
    color: #000 !important;
    min-height: 85px !important;
    font-size: 13pt !important;
    line-height: 1.6 !important;
    padding: 10px 12px !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
    white-space: pre-wrap !important;
    border-radius: 6px !important;
  }
}
"""
UNBLOCK_PDF_SCRIPT = """
<script>
// Unblock both 'Save my notes as PDF' and individual 'Save this type as PDF'
(function(){
  function setupPdfBtns() {
    // 1. Main PDF button (Save all notes)
    var btn = document.getElementById('pdf') || document.getElementById('savepdf');
    if (btn) {
      btn.onclick = function(e) {
        if (e) e.preventDefault();
        document.body.classList.remove('one');
        var secs = [].slice.call(document.querySelectorAll('section.typ'));
        secs.forEach(function(s) {
          s.classList.remove('pick', 'pr-skip');
          s.style.display = 'block';
        });
        var h = document.querySelector('h1.t');
        document.title = (h ? h.innerText : 'Type Notes');
        window.print();
      };
    }

    // 2. Individual type PDF buttons (.tpdf)
    var typeBtns = document.querySelectorAll('.tpdf');
    typeBtns.forEach(function(tp) {
      tp.onclick = function(e) {
        if (e) e.preventDefault();
        var sec = tp.closest('section.typ');
        if (!sec) return;
        document.body.classList.add('one');
        document.querySelectorAll('section.typ').forEach(function(s) {
          s.classList.remove('pick');
        });
        sec.classList.add('pick');
        var h = document.querySelector('h1.t');
        var k = sec.dataset.k || sec.id || '';
        document.title = (h ? h.innerText : 'Type Notes') + ' - Type ' + k;
        window.print();
      };
    });

    // 3. Reset state after printing
    window.addEventListener('afterprint', function() {
      document.body.classList.remove('one');
      document.querySelectorAll('section.typ').forEach(function(s) {
        s.classList.remove('pick', 'pr-skip');
        s.style.display = 'block';
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupPdfBtns);
  } else {
    setupPdfBtns();
  }
})();
</script>
"""

def patch_type_notes(content):
    modified = False
    
    # 1. Unblock .sh (Show completed notes)
    pattern_sh = r"if\s*\(!any\)\s*\{\s*alert\([^)]+\);\s*return\s*;?\s*\}"
    if re.search(pattern_sh, content):
        content = re.sub(pattern_sh, "/* unblocked show */", content)
        modified = True
        
    # 2. Unblock .tpdf (Save specific type as PDF)
    pattern_tpdf = r"if\s*\(!hasWork\(s\)\)\s*\{\s*alert\([^)]+\);\s*return\s*;?\s*\}"
    if re.search(pattern_tpdf, content):
        content = re.sub(pattern_tpdf, "/* unblocked tpdf */", content)
        modified = True
        
    # 3. Unblock #pdf (Save my notes as PDF)
    pattern_pdf = r"if\s*\(!n\)\s*\{\s*endPrint\(\);\s*alert\([^)]+\);\s*return\s*;?\s*\}"
    if re.search(pattern_pdf, content):
        content = re.sub(pattern_pdf, "/* unblocked pdf */ if(!n){secs.forEach(function(s){s.classList.remove('pr-skip')});}", content)
        modified = True
    
    # 4. Clean and upgrade Print CSS
    if "@media print" in content:
        if "/* --- Clean Print & Save as PDF Styling (Workbook layout) --- */" not in content:
            content = re.sub(r'@media\s*print\s*\{.*?\}\s*\}', PERFECT_PRINT_CSS, content, flags=re.DOTALL)
            modified = True
    else:
        pos_style = content.rfind("</style>")
        if pos_style != -1:
            content = content[:pos_style] + PERFECT_PRINT_CSS + "\n</style>" + content[pos_style+8:]
            modified = True
        
    return content, modified
# -------------------------------------------------------------
# 4. COMPREHENSIVE DARK MODE
# -------------------------------------------------------------
HEAD_PREVENT_FLICKER = """<script>
  (function(){
    var t = localStorage.getItem('jee_theme');
    if (t === 'dark' || (!t && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  })();
</script>"""

MODAL_LIGHT_CSS = """/* Modal Sections & Pills */
.modal-box {
  max-width: 580px !important;
}
.modal-section-title {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  margin: 12px 0 6px;
}
.modal-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-bottom: 4px;
}
.pill-btn {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border: 1.5px solid #cbd5e1;
  border-radius: 10px;
  background: #f8fafc;
  font-size: 13.5px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}
.pill-btn input[type=radio] {
  display: none;
}
.pill-btn:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}
.pill-btn.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 700;
}"""

DARK_MODE_CSS = """
/* =================== ELEVATED TRUE AMOLED BLACK DARK MODE =================== */
:root {
  --bg-base: #f8fafc;
  --surface-card: #ffffff;
  --surface-elevated: #f1f5f9;
  --border-subtle: #e2e8f0;
  --border-input: #cbd5e1;
  --text-main: #0f172a;
  --text-muted: #475569;
  --primary-blue: #2563eb;
  --primary-blue-hover: #1d4ed8;
}

[data-theme="dark"] {
  --ink: #ffffff;
  --mut: #a1a1aa;
  --line: #222224;
  --bg: #000000;
  --surface: #0a0a0c;
  --surface-card: #0a0a0c;
  --surface-elevated: #111114;
  --accl: rgba(37, 99, 235, 0.2);
  --accb: #3b82f6;
  --hdr: #000000;
  --hdrtx: #ffffff;
  --tmbg: rgba(255, 255, 255, 0.08);
  --hdrline: #222224;
  --border-subtle: #222224;
  --border-input: #2e2e34;
  --text-muted: #a1a1aa !important;
  --text-secondary: #e4e4e7 !important;
}

[data-theme="dark"] body {
  background: #000000 !important;
  color: #ffffff !important;
}

[data-theme="dark"] a {
  color: #60a5fa !important;
}

/* Fix primary action buttons so text is ALWAYS crisp white (solves Pic 7 invisible words) */
[data-theme="dark"] a.act-btn.primary,
[data-theme="dark"] .act-btn.primary,
[data-theme="dark"] a.btn.pri,
[data-theme="dark"] .btn.pri,
[data-theme="dark"] .btn-cbt-launch,
[data-theme="dark"] .btn-modal-start,
[data-theme="dark"] .start-exam-btn,
[data-theme="dark"] button.pri {
  color: #ffffff !important;
  background: #2563eb !important;
  border-color: #2563eb !important;
  font-weight: 600 !important;
}
[data-theme="dark"] a.act-btn.primary:hover,
[data-theme="dark"] .act-btn.primary:hover,
[data-theme="dark"] a.btn.pri:hover,
[data-theme="dark"] .btn.pri:hover,
[data-theme="dark"] button.pri:hover {
  background: #1d4ed8 !important;
  color: #ffffff !important;
}

/* Eliminate Wasted Screen Space on Chapter Pages (solves Pic 3) */
.panel {
  max-width: 1040px !important;
  margin: 24px auto !important;
  padding: 28px 36px !important;
  border-radius: 12px !important;
  transition: background 0.2s ease, border-color 0.2s ease;
}
[data-theme="dark"] .panel {
  background: #0a0a0c !important;
  border: 1px solid #222224 !important;
}
.wrap {
  max-width: 1140px !important;
}

/* Question Type Cards, Selectors & Practice Controls in Dark Mode (solves Pic 3 white box error) */
[data-theme="dark"] .tc,
[data-theme="dark"] .gf,
[data-theme="dark"] .sec,
[data-theme="dark"] .kc,
[data-theme="dark"] .tbox,
[data-theme="dark"] #done .sec {
  background: #0a0a0c !important;
  border-color: #222224 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .tc.zero {
  background: #060608 !important;
  border-color: #1a1a1c !important;
  opacity: 0.6;
}
[data-theme="dark"] .selsum {
  background: #081a36 !important;
  border-color: #2563eb !important;
  color: #ffffff !important;
}
[data-theme="dark"] .selsum.warn {
  background: #3b1111 !important;
  border-color: #dc2626 !important;
  color: #fca5a5 !important;
}
[data-theme="dark"] #typelist label.pill input+span {
  background: #111114 !important;
  border: 1.5px solid #2e2e34 !important;
  color: #93c5fd !important;
}
[data-theme="dark"] #typelist label.pill input:checked+span {
  background: #2563eb !important;
  border-color: #2563eb !important;
  color: #ffffff !important;
}
[data-theme="dark"] #typelist .pill .cc {
  color: #a1a1aa !important;
}
[data-theme="dark"] #typelist .pill input:checked+span .cc {
  color: #ffffff !important;
}
[data-theme="dark"] .tc .tcnt,
[data-theme="dark"] .gf .gfn,
[data-theme="dark"] .cnt,
[data-theme="dark"] label.rad,
[data-theme="dark"] #typelist label.rad,
[data-theme="dark"] #typelist .all span,
[data-theme="dark"] .tnote,
[data-theme="dark"] .note {
  color: #a1a1aa !important;
}
[data-theme="dark"] #typelist .all span:hover {
  color: #60a5fa !important;
}
[data-theme="dark"] label {
  color: #ffffff !important;
}
[data-theme="dark"] .banner {
  background: #091a10 !important;
  border-color: #059669 !important;
  color: #d1fae5 !important;
}
[data-theme="dark"] .banner a {
  color: #6ee7b7 !important;
}
[data-theme="dark"] .gp {
  background: #111114 !important;
  border-color: #222224 !important;
  color: #e4e4e7 !important;
}
[data-theme="dark"] .gp b {
  color: #ffffff !important;
}
[data-theme="dark"] .lg {
  background: #0a0a0c !important;
  border-color: #222224 !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .lg b {
  color: #ffffff !important;
}
[data-theme="dark"] .strip {
  background: #0a0a0c !important;
  border-color: #222224 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .strip .no {
  color: #a1a1aa !important;
}
[data-theme="dark"] .strip .mid b {
  color: #60a5fa !important;
}
[data-theme="dark"] .strip .mid span,
[data-theme="dark"] .strip .gl {
  color: #a1a1aa !important;
}
[data-theme="dark"] .strip .gl b {
  color: #e4e4e7 !important;
}
[data-theme="dark"] .tg em {
  background: #111114 !important;
  border-color: #222224 !important;
  color: #d4d4d8 !important;
}

/* Overview Text Readability Fixes (solves Pic 2) */
[data-theme="dark"] .metric-label {
  color: #a1a1aa !important;
}
[data-theme="dark"] .metric-sub {
  color: #d4d4d8 !important;
}
[data-theme="dark"] .subj-meter-header {
  color: #e4e4e7 !important;
}
[data-theme="dark"] .subj-meter-count {
  color: #a1a1aa !important;
}
[data-theme="dark"] .search-input {
  color: #ffffff !important;
  background: #121215 !important;
  border-color: #2e2e34 !important;
}
[data-theme="dark"] .search-input::placeholder {
  color: #71717a !important;
}
[data-theme="dark"] .search-count {
  color: #a1a1aa !important;
}

/* Visible Typing Boxes in Dark Mode (solves Pic 6) */
[data-theme="dark"] .ed,
[data-theme="dark"] div[contenteditable="true"],
[data-theme="dark"] textarea,
[data-theme="dark"] input[type="text"],
[data-theme="dark"] input[type="number"],
[data-theme="dark"] input.num,
[data-theme="dark"] .tin input,
[data-theme="dark"] table.gt td[contenteditable="true"] {
  background: #121215 !important;
  border: 1.5px solid #2e2e34 !important;
  color: #ffffff !important;
  border-radius: 8px !important;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.4) !important;
  padding: 8px 12px !important;
}
[data-theme="dark"] .ed:focus,
[data-theme="dark"] div[contenteditable="true"]:focus,
[data-theme="dark"] textarea:focus,
[data-theme="dark"] input[type="text"]:focus,
[data-theme="dark"] input[type="number"]:focus,
[data-theme="dark"] input.num:focus {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
  outline: none !important;
}

[data-theme="dark"] table,
[data-theme="dark"] th,
[data-theme="dark"] td,
[data-theme="dark"] table.gt,
[data-theme="dark"] table.gt td,
[data-theme="dark"] table.gt th {
  border-color: #222224 !important;
}

[data-theme="dark"] .o {
  background: #0e0e11 !important;
  border-color: #222224 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o:hover {
  border-color: #3b82f6 !important;
}
[data-theme="dark"] .o.sel {
  background: rgba(37, 99, 235, 0.18) !important;
  border-color: #3b82f6 !important;
}

/* Attempt Cards in Dark Mode (solves Pic 4 & Pic 8) */
[data-theme="dark"] .att-card {
  background: #0e0e11 !important;
  border: 1px solid #222224 !important;
}
[data-theme="dark"] .att-card:hover {
  border-color: #2c2c32 !important;
}
[data-theme="dark"] .att-badge.cbt {
  background: rgba(147, 51, 234, 0.15) !important;
  color: #c084fc !important;
  border-color: rgba(147, 51, 234, 0.3) !important;
}
[data-theme="dark"] .att-badge.practice {
  background: rgba(37, 99, 235, 0.15) !important;
  color: #93c5fd !important;
  border-color: rgba(37, 99, 235, 0.3) !important;
}
[data-theme="dark"] .att-date {
  color: #a1a1aa !important;
}
[data-theme="dark"] .att-stats-row {
  color: #d4d4d8 !important;
}
[data-theme="dark"] .att-actions {
  border-top-color: #222224 !important;
}
[data-theme="dark"] .att-btn {
  background: #141418 !important;
  border-color: #24242a !important;
  color: #f4f4f6 !important;
}
[data-theme="dark"] .att-btn:hover {
  background: #1c1c22 !important;
  border-color: #2e2e36 !important;
}
[data-theme="dark"] .att-btn.continue {
  background: #16a34a !important;
  border-color: #16a34a !important;
  color: #ffffff !important;
}
[data-theme="dark"] .att-btn.continue:hover {
  background: #15803d !important;
}
[data-theme="dark"] .att-btn.review {
  background: rgba(37, 99, 235, 0.15) !important;
  border-color: rgba(37, 99, 235, 0.3) !important;
  color: #93c5fd !important;
}
[data-theme="dark"] .att-btn.delete {
  background: rgba(220, 38, 38, 0.1) !important;
  border-color: rgba(220, 38, 38, 0.3) !important;
  color: #f87171 !important;
}
[data-theme="dark"] .btn-export-all {
  background: #141418 !important;
  border-color: #24242a !important;
  color: #f4f4f6 !important;
}
[data-theme="dark"] .btn-export-all:hover {
  background: #1c1c22 !important;
  border-color: #2e2e36 !important;
}
[data-theme="dark"] .sub-pill-btn {
  color: #93c5fd !important;
  background: #0e0e11 !important;
  border: 1px solid #222224 !important;
}
[data-theme="dark"] .sub-pill-btn:hover {
  background: #18181c !important;
  border-color: #3b82f6 !important;
}

/* Theme Toggle Button Outline Styling (solves Pic 17) */
.theme-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #0f172a;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.theme-btn:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  transform: translateY(-1px);
}
.theme-btn:active {
  transform: scale(0.98);
}
[data-theme="dark"] .theme-btn {
  background: #111114 !important;
  border-color: #2e2e34 !important;
  color: #f4f4f6 !important;
}
[data-theme="dark"] .theme-btn:hover {
  background: #18181c !important;
  border-color: #3b82f6 !important;
}

"""

THEME_TOGGLE_JS = """
<script>
function initThemeToggle() {
  var MOON_ICON = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
  var SUN_ICON = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';

  function applyTheme(dark) {
    if (dark) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('jee_theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('jee_theme', 'light');
    }
    var btns = document.querySelectorAll('.theme-btn');
    btns.forEach(function(b) {
      b.innerHTML = dark ? (SUN_ICON + '<span>Light</span>') : (MOON_ICON + '<span>Dark</span>');
      b.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    });
  }
  var isDark = localStorage.getItem('jee_theme') === 'dark' || 
    (!localStorage.getItem('jee_theme') && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  applyTheme(isDark);

  if (!window._themeToggleAttached) {
    window._themeToggleAttached = true;
    document.addEventListener('click', function(e) {
      var btn = e.target.closest('.theme-btn');
      if (btn) {
        var currentlyDark = document.documentElement.getAttribute('data-theme') === 'dark';
        applyTheme(!currentlyDark);
      }
    });
  }
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initThemeToggle);
} else {
  initThemeToggle();
}
</script>
"""

def patch_dark_mode(content, filename=""):
    modified = False
    
    # 1. Anti-flicker script in head
    if "localStorage.getItem('jee_theme')" not in content and "<head>" in content:
        content = content.replace("<head>", "<head>\n" + HEAD_PREVENT_FLICKER, 1)
        modified = True
        
    # 2. Elevated Slate / AMOLED Dark mode CSS
    pattern_legacy_tn = r"""/\* =+ COMPREHENSIVE DARK MODE \(TYPE NOTES\) =+ \*/.*?\[data-theme=['"]dark['"]\] \.theme-btn:hover\s*\{[^}]+\}\s*"""
    if re.search(pattern_legacy_tn, content, re.DOTALL):
        content = re.sub(pattern_legacy_tn, "", content, flags=re.DOTALL)
        modified = True

    markers = [
        "/* =================== ELEVATED TRUE AMOLED BLACK DARK MODE",
        "/* =================== TRUE AMOLED BLACK DARK MODE",
        "/* =================== ELEVATED SLATE DARK THEME",
        "/* =================== COMPREHENSIVE HIGH-CONTRAST DARK MODE",
        "/* =================== COMPREHENSIVE DARK MODE"
    ]
    replaced = False
    for marker in markers:
        if marker in content:
            idx_start = content.find(marker)
            idx_style = content.find("</style>", idx_start)
            if idx_start != -1 and idx_style != -1:
                existing_block = content[idx_start:idx_style].strip()
                if existing_block != DARK_MODE_CSS.strip():
                    content = content[:idx_start] + DARK_MODE_CSS.strip() + "\n" + content[idx_style:]
                    modified = True
                replaced = True
                break
    if not replaced:
        pattern = r"""/\* =+ COMPREHENSIVE DARK MODE =+ \*/.*?\[data-theme=['"]dark['"]\] \.theme-btn:hover\s*\{[^}]+\}"""
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, lambda m: DARK_MODE_CSS.strip(), content, flags=re.DOTALL)
            modified = True
        else:
            if "</style>" in content:
                content = content.replace("</style>", DARK_MODE_CSS + "\n</style>", 1)
                modified = True
        
    # 3. Add or update toggle button with SVG outline icon (NEVER into index.html)
    is_index = ("index.html" in filename.lower()) or ("JEE Main PYQ Practice Portal" in content)
    svg_btn_html = '<button class="theme-btn" type="button" title="Toggle theme"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg><span>Dark</span></button>'
    
    if not is_index:
        pattern_btn = r'<button class="theme-btn"[^>]*>.*?</button>'
        if re.search(pattern_btn, content):
            if ('\U0001f319 Dark' in content or '\u2600\ufe0f Light' in content) or ('viewBox' not in content):
                content = re.sub(pattern_btn, lambda m: svg_btn_html, content)
                modified = True
        elif 'class="theme-btn"' not in content:
            pattern = r'(<div id="start"[^>]*>\s*)(<a href="index\.html"[^>]*>.*?</a>)'
            m = re.search(pattern, content)
            if m:
                replacement = (
                    m.group(1) +
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                    m.group(2) +
                    svg_btn_html + '</div>'
                )
                content = content[:m.start()] + replacement + content[m.end():]
                modified = True
            else:
                m2 = re.search(r'(<h1[^>]*>.*?</h1>)', content)
                if m2:
                    btn = '<div style="display:flex;justify-content:flex-end;margin-bottom:8px;">' + svg_btn_html + '</div>\n'
                    content = content[:m2.start()] + btn + content[m2.start():]
                    modified = True
                
    # 4. Toggle JS listener (if not index.html)
    if not is_index:
        pattern_toggle = r'<script>\s*function initThemeToggle\(\)\s*\{.*?</script>'
        if re.search(pattern_toggle, content, re.DOTALL):
            if 'MOON_ICON' not in content or '_themeToggleAttached' not in content:
                content = re.sub(pattern_toggle, lambda m: THEME_TOGGLE_JS, content, flags=re.DOTALL)
                modified = True
        elif '</body>' in content:
            pos_b = content.rfind("</body>")
            if pos_b != -1:
                content = content[:pos_b] + THEME_TOGGLE_JS + "\n</body>" + content[pos_b+7:]
                modified = True
        
    return content, modified

# -------------------------------------------------------------
# 6. QUESTION COUNT SELECTION & TIMED SAMPLING
# -------------------------------------------------------------
# -------------------------------------------------------------
# 6. CBT EXAM MODE & QUESTION COUNT SELECTION
# -------------------------------------------------------------
TEST_MODE_AND_QCOUNT_HTML = """<label>Test &amp; Practice Mode</label>
<div class="tbox" id="test_mode_box" style="margin-bottom:14px;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;">
    <label class="mode-card active" id="mode_card_cbt" style="display:flex;align-items:flex-start;gap:10px;padding:12px 14px;border:1.5px solid #2563eb;border-radius:10px;background:#eff6ff;cursor:pointer;transition:all 0.15s ease;">
      <input type="radio" name="test_mode" value="cbt" checked style="margin-top:3px;">
      <div>
        <div style="display:flex;align-items:center;gap:6px;font-weight:700;font-size:14px;color:#1e40af;">
          <span>Real CBT Exam Mode</span>
          <span style="font-size:11px;background:#2563eb;color:#ffffff;padding:1px 6px;border-radius:4px;font-weight:600;">NTA Pattern</span>
        </div>
        <div style="font-size:12.5px;color:#475569;margin-top:3px;line-height:1.4;">Official test conditions. No instant answers or solutions. Marking: +4 / &minus;1. Full score breakdown post-submission.</div>
      </div>
    </label>
    <label class="mode-card" id="mode_card_practice" style="display:flex;align-items:flex-start;gap:10px;padding:12px 14px;border:1.5px solid #cbd5e1;border-radius:10px;background:#f8fafc;cursor:pointer;transition:all 0.15s ease;">
      <input type="radio" name="test_mode" value="practice" style="margin-top:3px;">
      <div>
        <div style="display:flex;align-items:center;gap:6px;font-weight:700;font-size:14px;color:#334155;">
          <span>Practice &amp; Learn Mode</span>
          <span style="font-size:11px;background:#64748b;color:#ffffff;padding:1px 6px;border-radius:4px;font-weight:600;">Interactive</span>
        </div>
        <div style="font-size:12.5px;color:#475569;margin-top:3px;line-height:1.4;">Check answers per question instantly, retry wrong options, and inspect solutions anytime during practice.</div>
      </div>
    </label>
  </div>
</div>
<label>Number of questions</label>
<div class="tbox" id="qcount_box">
  <label class="rad"><input type="radio" name="qc_mode" value="all" checked> <span>All selected questions (<span id="total_q_avail">0</span> available)</span></label>
  <label class="rad" style="margin-top:6px;"><input type="radio" name="qc_mode" value="custom"> <span>Random sample of:</span></label>
  <div class="tin" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:4px 0 6px 26px;">
    <input type="number" id="custom_qc" min="1" max="500" value="25" style="width:65px;padding:3px 6px;font-size:14px;border-radius:6px;border:1.5px solid #cbd5e1;text-align:center"> questions randomly picked from your selection
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 4px 26px;">
    <button type="button" class="qpreset" data-q="15">15 qs (~30 min)</button>
    <button type="button" class="qpreset active" data-q="25">25 qs (Exam Sprint)</button>
    <button type="button" class="qpreset" data-q="30">30 qs (~60 min)</button>
    <button type="button" class="qpreset" data-q="50">50 qs</button>
  </div>
  <div class="tnote" id="qc_note" style="margin-left:26px;margin-top:4px;">Questions will be picked uniformly at random from your selected types/filters.</div>
</div>"""

ENHANCED_PRACTICE_SCRIPT = '<script>\n(function(){\n  // 1. Mode and Q-Count Controller\n  var modeCards = document.querySelectorAll(\'.mode-card\');\n  var qcRadios = document.querySelectorAll(\'input[name=qc_mode]\');\n  var customQcIn = document.getElementById(\'custom_qc\');\n  var presets = document.querySelectorAll(\'.qpreset\');\n\n  function updatePresetButtons(val) {\n    presets.forEach(function(btn){\n      if(btn.dataset.q === String(val)) {\n        btn.classList.add(\'active\');\n      } else {\n        btn.classList.remove(\'active\');\n      }\n    });\n  }\n\n  presets.forEach(function(btn){\n    btn.onclick = function(){\n      var q = btn.dataset.q;\n      if (customQcIn) customQcIn.value = q;\n      var rad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n      if (rad) rad.checked = true;\n      updatePresetButtons(q);\n      if (typeof sug === \'function\') sug();\n    };\n  });\n\n  qcRadios.forEach(function(r){\n    r.onchange = function(){\n      if (r.value === \'all\') {\n        presets.forEach(function(b){ b.classList.remove(\'active\'); });\n      } else {\n        if (customQcIn) updatePresetButtons(customQcIn.value);\n      }\n      if (typeof sug === \'function\') sug();\n    };\n  });\n\n  if (customQcIn) {\n    customQcIn.onfocus = function(){\n      var rad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n      if (rad) rad.checked = true;\n      updatePresetButtons(customQcIn.value);\n      if (typeof sug === \'function\') sug();\n    };\n    customQcIn.oninput = function(){\n      var rad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n      if (rad) rad.checked = true;\n      updatePresetButtons(customQcIn.value);\n      if (typeof sug === \'function\') sug();\n    };\n  }\n\n  // Mode Cards Selection\n  modeCards.forEach(function(card){\n    card.onclick = function(){\n      modeCards.forEach(function(c){ c.classList.remove(\'active\'); });\n      card.classList.add(\'active\');\n      var rad = card.querySelector(\'input[type=radio]\');\n      if (rad) rad.checked = true;\n    };\n  });\n\n  // URL Query Parameters Handling (autostart, mode, filter, q, t)\n  function handleUrlParams() {\n    var params = new URLSearchParams(window.location.search);\n    var mode = params.get(\'mode\');\n    if (mode === \'practice\') {\n      var pCard = document.getElementById(\'mode_card_practice\');\n      if (pCard) pCard.click();\n    } else if (mode === \'cbt\') {\n      var cCard = document.getElementById(\'mode_card_cbt\');\n      if (cCard) cCard.click();\n    }\n\n    var filter = params.get(\'filter\');\n    if (filter === \'wrong\') {\n      var wBox = document.getElementById(\'onlywrong\');\n      if (wBox) { wBox.checked = true; if (typeof sug === \'function\') sug(); }\n    } else if (filter === \'star\') {\n      var sBox = document.getElementById(\'onlystar\');\n      if (sBox) { sBox.checked = true; if (typeof sug === \'function\') sug(); }\n    }\n\n    var qParam = params.get(\'q\');\n    if (qParam) {\n      if (qParam === \'all\') {\n        var aRad = document.querySelector(\'input[name=qc_mode][value=all]\');\n        if (aRad) aRad.checked = true;\n        presets.forEach(function(b){ b.classList.remove(\'active\'); });\n      } else {\n        var num = parseInt(qParam);\n        if (num > 0) {\n          if (customQcIn) customQcIn.value = num;\n          var cRad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n          if (cRad) cRad.checked = true;\n          updatePresetButtons(num);\n        }\n      }\n      if (typeof sug === \'function\') sug();\n    }\n\n    var tParam = params.get(\'t\');\n    if (tParam) {\n      if (tParam === \'free\') {\n        var fRad = document.querySelector(\'input[name=tm][value=free]\');\n        if (fRad) fRad.checked = true;\n      } else {\n        var tnum = parseInt(tParam);\n        if (tnum > 0) {\n          var tRad = document.querySelector(\'input[name=tm][value=timed]\');\n          if (tRad) tRad.checked = true;\n          var mIn = document.getElementById(\'mins\');\n          if (mIn) mIn.value = tnum;\n        }\n      }\n    }\n\n    if (params.get(\'autostart\') === \'1\') {\n      setTimeout(function(){\n        var goBtn = document.getElementById(\'go\');\n        if (goBtn && !goBtn.disabled) goBtn.click();\n      }, 200);\n    }\n  }\n\n  handleUrlParams();\n\n  // 2. Fullscreen & Header Controls Setup\n  var examEl = document.getElementById(\'exam\');\n  if (examEl) {\n    // Inject Progress Bar\n    var pBar = document.createElement(\'div\');\n    pBar.id = \'examProgressBar\';\n    examEl.appendChild(pBar);\n\n    var topEl = examEl.querySelector(\'.top\');\n    if (topEl) {\n      topEl.style.position = \'relative\';\n\n      var badge = document.createElement(\'span\');\n      badge.id = \'examModeBadge\';\n      badge.style.cssText = \'font-size:12px;font-weight:700;padding:3px 8px;border-radius:4px;background:#2563eb;color:#ffffff;margin-left:12px;white-space:nowrap;\';\n      badge.textContent = \'CBT Mode\';\n      topEl.insertBefore(badge, topEl.querySelector(\'.tm\'));\n\n      var fsBtn = document.createElement(\'button\');\n      fsBtn.className = \'btn\';\n      fsBtn.id = \'btnFullscreen\';\n      fsBtn.type = \'button\';\n      fsBtn.title = \'Toggle Fullscreen Mode (Hotkey: F)\';\n      fsBtn.style.cssText = \'margin-left:auto;margin-right:8px;font-size:13px;padding:5px 10px;\';\n      fsBtn.textContent = \'Fullscreen\';\n      fsBtn.onclick = function() {\n        if (!document.fullscreenElement) {\n          document.documentElement.requestFullscreen().catch(function(){});\n          fsBtn.textContent = \'Exit Fullscreen\';\n        } else {\n          if (document.exitFullscreen) document.exitFullscreen();\n          fsBtn.textContent = \'Fullscreen\';\n        }\n      };\n      topEl.insertBefore(fsBtn, topEl.querySelector(\'#submit\'));\n\n      var hkBtn = document.createElement(\'button\');\n      hkBtn.className = \'btn\';\n      hkBtn.id = \'btnHotkeys\';\n      hkBtn.type = \'button\';\n      hkBtn.title = \'Keyboard Shortcuts (Hotkey: ?)\';\n      hkBtn.style.cssText = \'font-size:13px;padding:5px 9px;margin-right:8px;\';\n      hkBtn.textContent = \'⌨\';\n      hkBtn.onclick = function() {\n        var modal = document.getElementById(\'hotkeysModal\');\n        if (modal) modal.style.display = modal.style.display === \'flex\' ? \'none\' : \'flex\';\n      };\n      topEl.insertBefore(hkBtn, topEl.querySelector(\'#submit\'));\n    }\n\n    // Inject Hotkeys Dialog\n    var hkModal = document.createElement(\'div\');\n    hkModal.id = \'hotkeysModal\';\n    hkModal.className = \'cbt-modal-backdrop\';\n    hkModal.style.display = \'none\';\n    hkModal.innerHTML = \'<div class="cbt-modal-box">\' +\n      \'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">\' +\n        \'<h3 style="margin:0;font-size:18px;">Keyboard Shortcuts</h3>\' +\n        \'<button type="button" class="btn" onclick="document.getElementById(\\\'hotkeysModal\\\').style.display=\\\'none\\\'" style="padding:2px 8px;font-size:16px;">&times;</button>\' +\n      \'</div>\' +\n      \'<table class="hotkeys-table">\' +\n        \'<tr><td><span class="kbd-key">1</span> &ndash; <span class="kbd-key">4</span> / <span class="kbd-key">A</span> &ndash; <span class="kbd-key">D</span></td><td>Select option A, B, C, or D</td></tr>\' +\n        \'<tr><td><span class="kbd-key">&rarr;</span> / <span class="kbd-key">N</span> / <span class="kbd-key">Enter</span></td><td>Save &amp; Next question</td></tr>\' +\n        \'<tr><td><span class="kbd-key">&larr;</span> / <span class="kbd-key">P</span></td><td>Previous question</td></tr>\' +\n        \'<tr><td><span class="kbd-key">M</span></td><td>Mark for Review &amp; Next</td></tr>\' +\n        \'<tr><td><span class="kbd-key">C</span> / <span class="kbd-key">Backspace</span></td><td>Clear response</td></tr>\' +\n        \'<tr><td><span class="kbd-key">S</span></td><td>Star question for later</td></tr>\' +\n        \'<tr><td><span class="kbd-key">F</span></td><td>Toggle Fullscreen Exam Mode</td></tr>\' +\n        \'<tr><td><span class="kbd-key">?</span></td><td>Open / Close this shortcuts helper</td></tr>\' +\n      \'</table>\' +\n      \'<button type="button" class="btn" onclick="document.getElementById(\\\'hotkeysModal\\\').style.display=\\\'none\\\'" style="margin-top:16px;width:100%;padding:8px;">Close Shortcuts</button>\' +\n    \'</div>\';\n    document.body.appendChild(hkModal);\n\n    // Inject CBT Submit Modal\n    var submitModal = document.createElement(\'div\');\n    submitModal.id = \'cbtSubmitModal\';\n    submitModal.className = \'cbt-modal-backdrop\';\n    submitModal.style.display = \'none\';\n    submitModal.innerHTML = \'<div class="cbt-modal-box">\' +\n      \'<h3 style="margin:0 0 8px;font-size:19px;">Submit Examination</h3>\' +\n      \'<p style="margin:0 0 12px;font-size:13.5px;color:#64748b;">Review your question status summary before final submission:</p>\' +\n      \'<table class="cbt-summary-table">\' +\n        \'<tr><td>Total Questions</td><td><b id="cbtSumTot">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot green"></span> Answered</td><td><b id="cbtSumAns" style="color:#16a34a">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot red"></span> Not Answered</td><td><b id="cbtSumNotAns" style="color:#ef4444">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot purple"></span> Marked for Review</td><td><b id="cbtSumMark" style="color:#9333ea">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot purple-green"></span> Answered &amp; Marked (Evaluated)</td><td><b id="cbtSumAnsMark" style="color:#9333ea">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot gray"></span> Not Visited</td><td><b id="cbtSumNotVis" style="color:#64748b">0</b></td></tr>\' +\n      \'</table>\' +\n      \'<div style="display:flex;gap:10px;">\' +\n        \'<button type="button" class="btn" id="cbtConfirmSubmit" style="flex:1;background:#2563eb;color:#fff;font-weight:700;padding:10px;">Confirm &amp; Submit</button>\' +\n        \'<button type="button" class="btn" id="cbtCancelSubmit" style="padding:10px 14px;">Return to Exam</button>\' +\n      \'</div>\' +\n    \'</div>\';\n    document.body.appendChild(submitModal);\n\n    document.getElementById(\'cbtCancelSubmit\').onclick = function(){\n      submitModal.style.display = \'none\';\n    };\n    document.getElementById(\'cbtConfirmSubmit\').onclick = function(){\n      submitModal.style.display = \'none\';\n      if (typeof origFinish === \'function\') origFinish();\n    };\n  }\n\n  // Option Elimination (Right click / Alt click)\n  document.addEventListener(\'contextmenu\', function(e){\n    var opt = e.target.closest(\'.o\');\n    if (opt && document.body.classList.contains(\'cbt-mode\')) {\n      e.preventDefault();\n      opt.classList.toggle(\'eliminated\');\n    }\n  });\n\n  // Global Keyboard Navigation\n  document.addEventListener(\'keydown\', function(e){\n    if (!examEl || examEl.hidden) return;\n    if (e.target.tagName === \'INPUT\' || e.target.tagName === \'TEXTAREA\') {\n      if (e.key === \'Enter\') {\n        var nxt = document.getElementById(\'svn\');\n        if (nxt) nxt.click();\n      }\n      return;\n    }\n    var k = e.key.toUpperCase();\n    if (k === \'1\' || k === \'A\') { selectOpt(\'A\'); }\n    else if (k === \'2\' || k === \'B\') { selectOpt(\'B\'); }\n    else if (k === \'3\' || k === \'C\') { selectOpt(\'C\'); }\n    else if (k === \'4\' || k === \'D\') { selectOpt(\'D\'); }\n    else if (k === \'ARROWLEFT\' || k === \'P\') {\n      var prev = document.getElementById(\'prev\');\n      if (prev && !prev.disabled) prev.click();\n    }\n    else if (k === \'ARROWRIGHT\' || k === \'N\' || e.key === \'Enter\') {\n      var svn = document.getElementById(\'svn\');\n      if (svn) svn.click();\n    }\n    else if (k === \'M\') {\n      var mkn = document.getElementById(\'mkn\');\n      if (mkn) mkn.click();\n    }\n    else if (k === \'C\' || k === \'BACKSPACE\' || k === \'DELETE\') {\n      var clr = document.getElementById(\'clr\');\n      if (clr) clr.click();\n    }\n    else if (k === \'S\') {\n      var star = document.getElementById(\'star\');\n      if (star) star.click();\n    }\n    else if (k === \'F\') {\n      var fs = document.getElementById(\'btnFullscreen\');\n      if (fs) fs.click();\n    }\n    else if (e.key === \'?\') {\n      var hk = document.getElementById(\'btnHotkeys\');\n      if (hk) hk.click();\n    }\n  });\n\n  function selectOpt(letter) {\n    if (typeof cur === \'undefined\') return;\n    var qv = document.getElementById(\'qv\' + cur);\n    if (!qv) return;\n    var opt = qv.querySelector(\'.o[data-l="\' + letter + \'"]\');\n    if (opt) opt.click();\n  }\n\n  // 3. Progress Bar Tracking\n  setInterval(function(){\n    if (typeof started === \'undefined\' || !started || typeof submitted === \'undefined\' || submitted) return;\n    var pBar = document.getElementById(\'examProgressBar\');\n    if (!pBar) return;\n    if (typeof LIMIT !== \'undefined\' && LIMIT > 0 && typeof total !== \'undefined\') {\n      var pct = Math.min(100, (total / LIMIT) * 100);\n      pBar.style.width = pct + \'%\';\n      var rem = LIMIT - total;\n      if (rem <= 300) {\n        pBar.style.backgroundColor = \'#ef4444\';\n      } else if (rem <= 900) {\n        pBar.style.backgroundColor = \'#f59e0b\';\n      } else {\n        pBar.style.backgroundColor = \'#2563eb\';\n      }\n    } else if (typeof NS !== \'undefined\' && NS.length > 0 && typeof cur !== \'undefined\') {\n      var idx = NS.indexOf(cur);\n      pBar.style.width = (((idx + 1) / NS.length) * 100) + \'%\';\n      pBar.style.backgroundColor = \'#2563eb\';\n    }\n  }, 1000);\n\n  // 4. Override enter() to handle CBT mode class & badge\n  var origEnter = window.enter;\n  window.enter = function() {\n    var modeRad = document.querySelector(\'input[name=test_mode]:checked\');\n    window.isCBT = !modeRad || modeRad.value === \'cbt\';\n    document.body.classList.toggle(\'cbt-mode\', window.isCBT);\n\n    var badge = document.getElementById(\'examModeBadge\');\n    if (badge) {\n      badge.textContent = window.isCBT ? \'CBT Exam Mode\' : \'Practice Mode\';\n      badge.style.background = window.isCBT ? \'#2563eb\' : \'#059669\';\n    }\n\n    if (typeof origEnter === \'function\') origEnter();\n  };\n\n  // 5. Override Submit Click for CBT Modal\n  var subBtn = document.getElementById(\'submit\');\n  if (subBtn) {\n    subBtn.onclick = function() {\n      if (!window.isCBT) {\n        var an = 0, mk = 0;\n        NS.forEach(function(n){ if (S[n]) an++; if (M[n]) mk++; });\n        if (confirm(\'Answered: \' + an + \'\\nNot answered: \' + (NS.length - an) + \'\\nMarked for review: \' + mk + \'\\n\\nSubmit?\')) {\n          if (typeof origFinish === \'function\') origFinish();\n        }\n        return;\n      }\n\n      var counts = { nv: 0, na: 0, an: 0, mk: 0, am: 0 };\n      NS.forEach(function(n){ counts[stat(n)]++; });\n\n      document.getElementById(\'cbtSumTot\').textContent = NS.length;\n      document.getElementById(\'cbtSumAns\').textContent = counts.an;\n      document.getElementById(\'cbtSumNotAns\').textContent = counts.na;\n      document.getElementById(\'cbtSumMark\').textContent = counts.mk;\n      document.getElementById(\'cbtSumAnsMark\').textContent = counts.am;\n      document.getElementById(\'cbtSumNotVis\').textContent = counts.nv;\n\n      var sm = document.getElementById(\'cbtSubmitModal\');\n      if (sm) sm.style.display = \'flex\';\n    };\n  }\n\n  // 6. Override finish() to compute NTA Marking Scheme (+4 / -1)\n  window.origFinish = window.finish;\n  window.finish = function() {\n    if (submitted) return;\n    submitted = true;\n\n    // Grade exam\n    var correctCount = 0;\n    var wrongCount = 0;\n    var unattemptedCount = 0;\n\n    NS.forEach(function(n){\n      var ans = S[n];\n      if (ans) {\n        var isOk = (typeof same === \'function\') ? same(n, ans) : false;\n        if (isOk) {\n          correctCount++;\n          C[n] = \'r\';\n          delete WR[n];\n        } else {\n          wrongCount++;\n          C[n] = \'w\';\n          WR[n] = 1;\n        }\n      } else {\n        unattemptedCount++;\n      }\n    });\n\n    if (typeof sv === \'function\' && typeof KW !== \'undefined\') sv(KW, WR);\n\n    var totalMarks = (correctCount * 4) - (wrongCount * 1);\n    var maxMarks = NS.length * 4;\n    var acc = (correctCount + wrongCount > 0) ? Math.round((correctCount / (correctCount + wrongCount)) * 100) : 0;\n\n    var A = {\n      t: Date.now(),\n      label: label,\n      NS: NS,\n      S: S,\n      M: M,\n      V: V,\n      T: T,\n      C: C,\n      X: X,\n      cur: cur,\n      total: total,\n      LIMIT: LIMIT,\n      isCBT: !!window.isCBT,\n      score: totalMarks,\n      maxScore: maxMarks,\n      correct: correctCount,\n      wrong: wrongCount,\n      unattempted: unattemptedCount,\n      accuracy: acc\n    };\n\n    HIST.unshift(A);\n    HIST = HIST.slice(0, 25);\n    if (typeof sv === \'function\' && typeof KH !== \'undefined\') sv(KH, HIST);\n    try { localStorage.removeItem(KS); } catch(e) {}\n\n    renderEnhancedSummary(A);\n  };\n\n  // Override summary() to also use modern scorecard for historical view\n  window.origSummary = window.summary;\n  window.summary = function(A, old) {\n    if (A) A.isEarlier = !!old;\n    renderEnhancedSummary(A);\n  };\n\n  // 7. Render Enhanced Summary & Question Review with Options and Solutions\n  window.renderEnhancedSummary = function(A) {\n    var examDiv = document.getElementById(\'exam\');\n    var startDiv = document.getElementById(\'start\');\n    var doneDiv = document.getElementById(\'done\');\n    if (examDiv) examDiv.hidden = true;\n    if (startDiv) startDiv.hidden = true;\n    if (!doneDiv) return;\n    doneDiv.hidden = false;\n\n    var ns = A.NS || [];\n    var corr = A.correct || 0;\n    var wrong = A.wrong || 0;\n    var unatt = A.unattempted || 0;\n    var totalQ = ns.length;\n    var score = typeof A.score === \'number\' ? A.score : ((corr * 4) - wrong);\n    var maxScore = A.maxScore || (totalQ * 4);\n    var acc = A.accuracy || (corr + wrong > 0 ? Math.round((corr / (corr + wrong)) * 100) : 0);\n\n    // SVG Donut calculation\n    var R = 44;\n    var C_circ = 2 * Math.PI * R;\n    var fCorr = totalQ > 0 ? (corr / totalQ) : 0;\n    var fWrong = totalQ > 0 ? (wrong / totalQ) : 0;\n    var fUnatt = totalQ > 0 ? (unatt / totalQ) : 0;\n\n    var lCorr = fCorr * C_circ;\n    var lWrong = fWrong * C_circ;\n    var lUnatt = fUnatt * C_circ;\n\n    var oCorr = 0;\n    var oWrong = -lCorr;\n    var oUnatt = -(lCorr + lWrong);\n\n    var tt = 0;\n    ns.forEach(function(n){ tt += (A.T && A.T[n]) || 0; });\n    var avgSec = totalQ > 0 ? Math.round(tt / totalQ) : 0;\n\n    var chName = (typeof META !== \'undefined\' && META.chapter) ? META.chapter : \'Chapter PYQ Examination\';\n    var isNeg = score < 0;\n\n    var tagTitle = A.isEarlier ? \'Past Attempt Review\' : (A.isCBT ? \'NTA CBT Simulation Scorecard\' : \'Practice Set Completed\');\n\n    var h = \'<div class="cbt-scorecard">\' +\n      \'<div class="cbt-score-hero">\' +\n        \'<div class="cbt-score-left">\' +\n          \'<span class="cbt-score-tag">\' + tagTitle + \'</span>\' +\n          \'<h2 class="cbt-score-title">\' + chName + \'</h2>\' +\n          \'<p class="cbt-score-meta">\' + (A.label || \'\') + \' &middot; \' + new Date(A.t).toLocaleString() + \'</p>\' +\n          \'<div style="display:flex;align-items:baseline;gap:8px;margin-top:14px;">\' +\n            \'<div class="cbt-big-score\' + (isNeg ? \' neg\' : \'\') + \'">\' + (score > 0 ? \'+\' : \'\') + score + \' <small>/ \' + maxScore + \'</small></div>\' +\n            \'<span style="font-size:13px;font-weight:700;padding:3px 9px;border-radius:4px;background:#e0f2fe;color:#0369a1;">\' + acc + \'% Accuracy</span>\' +\n          \'</div>\' +\n        \'</div>\' +\n        \'<div class="cbt-donut-wrap">\' +\n          \'<svg class="cbt-donut-svg" viewBox="0 0 100 100">\' +\n            \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#222224" stroke-width="12"/>\' +\n            (lCorr > 0 ? \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#16a34a" stroke-width="12" stroke-dasharray="\' + lCorr + \' \' + C_circ + \'" stroke-dashoffset="\' + oCorr + \'"/>\' : \'\') +\n            (lWrong > 0 ? \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#ef4444" stroke-width="12" stroke-dasharray="\' + lWrong + \' \' + C_circ + \'" stroke-dashoffset="\' + oWrong + \'"/>\' : \'\') +\n            (lUnatt > 0 ? \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#94a3b8" stroke-width="12" stroke-dasharray="\' + lUnatt + \' \' + C_circ + \'" stroke-dashoffset="\' + oUnatt + \'"/>\' : \'\') +\n          \'</svg>\' +\n          \'<div class="cbt-donut-legend">\' +\n            \'<div class="cbt-donut-legend-item"><span class="cbt-donut-dot" style="background:#16a34a"></span> Correct: \' + corr + \'</div>\' +\n            \'<div class="cbt-donut-legend-item"><span class="cbt-donut-dot" style="background:#ef4444"></span> Incorrect: \' + wrong + \'</div>\' +\n            \'<div class="cbt-donut-legend-item"><span class="cbt-donut-dot" style="background:#94a3b8"></span> Unattempted: \' + unatt + \'</div>\' +\n          \'</div>\' +\n        \'</div>\' +\n      \'</div>\' +\n\n      \'<div class="cbt-metrics-grid">\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Total Questions</span><span class="cbt-metric-num">\' + totalQ + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Correct (+4)</span><span class="cbt-metric-num" style="color:#16a34a">+\' + (corr * 4) + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Negative (-1)</span><span class="cbt-metric-num" style="color:#ef4444">-\' + wrong + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Net Marks</span><span class="cbt-metric-num" style="color:\' + (score >= 0 ? \'#16a34a\' : \'#ef4444\') + \'">\' + score + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Time Taken</span><span class="cbt-metric-num">\' + (typeof fmt === \'function\' ? fmt(tt) : tt + \'s\') + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Avg / Question</span><span class="cbt-metric-num">\' + avgSec + \'s</span></div>\' +\n      \'</div>\' +\n\n      \'<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;">\' +\n        \'<button type="button" class="btn" onclick="location.reload()" style="padding:9px 16px;background:#2563eb;color:#fff;font-weight:700;">Retake Chapter Practice</button>\' +\n        \'<a href="index.html" class="btn" style="padding:9px 16px;text-decoration:none;display:inline-flex;align-items:center;">&lsaquo; Subject Chapters</a>\' +\n        \'<a href="../index.html" class="btn" style="padding:9px 16px;text-decoration:none;display:inline-flex;align-items:center;">Home Portal</a>\' +\n      \'</div>\' +\n\n      \'<h3 style="margin:24px 0 12px;font-size:18px;">Detailed Solutions &amp; Question Review</h3>\' +\n      \'<div class="review-filter-pills" id="reviewFilterPills">\' +\n        \'<button type="button" class="rf-pill active" data-f="all">All Questions (\' + totalQ + \')</button>\' +\n        \'<button type="button" class="rf-pill" data-f="inc">Incorrect Only (\' + wrong + \')</button>\' +\n        \'<button type="button" class="rf-pill" data-f="corr">Correct Only (\' + corr + \')</button>\' +\n        \'<button type="button" class="rf-pill" data-f="unatt">Unattempted (\' + unatt + \')</button>\' +\n      \'</div>\' +\n      \'<div id="reviewQuestionsList"></div>\' +\n    \'</div>\';\n\n    doneDiv.innerHTML = h;\n\n    // Render Question Review Cards\n    var qListEl = document.getElementById(\'reviewQuestionsList\');\n    var cardsHtml = \'\';\n\n    ns.forEach(function(n, idx){\n      var qv = document.getElementById(\'qv\' + n);\n      if (!qv) return;\n\n      var userAns = (A.S && A.S[n]) || \'\';\n      var correctAns = (typeof META !== \'undefined\' && META.ans) ? String(META.ans[n]) : \'\';\n      var isOk = userAns && ((typeof same === \'function\') ? same(n, userAns) : (userAns === correctAns));\n      var isUnatt = !userAns;\n\n      var tag = isOk ? \'corr\' : (isUnatt ? \'unatt\' : \'inc\');\n      var pillText = isOk ? \'+4 Correct\' : (isUnatt ? \'0 Unattempted\' : \'-1 Incorrect\');\n\n      var stemEl = qv.querySelector(\'.stem\');\n      var stemHtml = stemEl ? stemEl.innerHTML : \'\';\n      var srcEl = qv.querySelector(\'.src\');\n      var srcText = srcEl ? srcEl.textContent : \'\';\n\n      // Find Type Name from META\n      var typeName = \'\';\n      var typeId = qv.dataset.type;\n      if (typeof META !== \'undefined\' && META.types) {\n        META.types.forEach(function(t){\n          if (String(t.id) === String(typeId)) typeName = t.name;\n        });\n      }\n\n      // Format Options for Review\n      var optsHtml = \'\';\n      var optsEl = qv.querySelector(\'.opts\');\n      if (optsEl) {\n        optsHtml = \'<div class="review-opts" style="display:flex;flex-direction:column;gap:6px;margin:10px 0;">\';\n        var oDivs = optsEl.querySelectorAll(\'.o\');\n        oDivs.forEach(function(o){\n          var letCode = o.dataset.l || \'\';\n          var isThisCorrect = (letCode.toUpperCase() === correctAns.toUpperCase());\n          var isThisUser = (letCode.toUpperCase() === String(userAns).toUpperCase());\n          var border = \'1px solid #cbd5e1\';\n          var bg = \'#f8fafc\';\n          var badge = \'\';\n\n          if (isThisCorrect) {\n            border = \'2px solid #16a34a\';\n            bg = \'#dcfce7\';\n            badge = \'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#15803d;background:#bbf7d0;padding:1px 6px;border-radius:3px;">Correct Key</span>\';\n          }\n          if (isThisUser && !isThisCorrect) {\n            border = \'2px solid #ef4444\';\n            bg = \'#fee2e2\';\n            badge = \'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#b91c1c;background:#fecaca;padding:1px 6px;border-radius:3px;">Your Choice</span>\';\n          } else if (isThisUser && isThisCorrect) {\n            badge = \'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#15803d;background:#bbf7d0;padding:1px 6px;border-radius:3px;">Your Choice (Correct)</span>\';\n          }\n\n          var oc = o.querySelector(\'.oc\');\n          var ocHtml = oc ? oc.innerHTML : \'\';\n\n          optsHtml += \'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:6px;border:\' + border + \';background:\' + bg + \';">\' +\n            \'<span style="font-weight:800;font-size:13px;width:20px;">\' + letCode + \'</span>\' +\n            \'<div style="flex:1;font-size:13.5px;">\' + ocHtml + \'</div>\' +\n            badge +\n          \'</div>\';\n        });\n        optsHtml += \'</div>\';\n      }\n\n      cardsHtml += \'<div class="review-card" data-tag="\' + tag + \'">\' +\n        \'<div class="review-header">\' +\n          \'<div style="font-weight:700;font-size:14.5px;">Q.\' + (idx + 1) + \' <span style="color:#64748b;font-size:12.5px;font-weight:400;margin-left:6px;">\' + srcText + \'</span></div>\' +\n          \'<span class="review-pill \' + tag + \'">\' + pillText + \'</span>\' +\n        \'</div>\' +\n        (typeName ? \'<div style="font-size:12px;color:#2563eb;font-weight:600;margin-bottom:8px;">Type: \' + typeName + \'</div>\' : \'\') +\n        \'<div class="stem-content" style="margin-bottom:12px;">\' + stemHtml + \'</div>\' +\n        optsHtml +\n        \'<div class="review-answers-box" style="margin-top:12px;padding:10px 12px;background:#f1f5f9;border-radius:6px;font-size:13.5px;">\' +\n          \'<div><b>Your Response:</b> \' + (userAns ? \'<span style="color:\' + (isOk ? \'#16a34a\' : \'#ef4444\') + \';font-weight:700">\' + userAns + \'</span>\' : \'<span style="color:#64748b;font-style:italic">Not Attempted</span>\') + \'</div>\' +\n          \'<div style="margin-top:4px;"><b>Official Key / Correct Answer:</b> <span style="color:#16a34a;font-weight:700">\' + correctAns + \'</span></div>\' +\n        \'</div>\' +\n      \'</div>\';\n    });\n\n    if (qListEl) qListEl.innerHTML = cardsHtml;\n\n    // Filter pills click handling\n    var rfPills = document.querySelectorAll(\'.rf-pill\');\n    rfPills.forEach(function(pill){\n      pill.onclick = function(){\n        rfPills.forEach(function(p){ p.classList.remove(\'active\'); });\n        pill.classList.add(\'active\');\n        var f = pill.dataset.f;\n        var rCards = document.querySelectorAll(\'.review-card\');\n        rCards.forEach(function(card){\n          if (f === \'all\' || card.dataset.tag === f) {\n            card.style.display = \'block\';\n          } else {\n            card.style.display = \'none\';\n          }\n        });\n      };\n    });\n\n    window.scrollTo({ top: 0, behavior: \'smooth\' });\n  };\n\n  // 6. Modern Attempt Cards & History Controller (solves Pic 4 & Pic 8)\n  var origRenderStart = window.renderStart;\n  window.renderStart = function() {\n    if (typeof origRenderStart === \'function\') {\n      try { origRenderStart(); } catch(e){}\n    }\n    var h = document.getElementById(\'hist\');\n    if (!h || !window.HIST || !window.HIST.length) return;\n\n    var html = \'<h3 style="margin-top:24px;margin-bottom:12px;font-size:18px;font-weight:700;">Your earlier attempts</h3>\';\n    html += \'<div class="attempts-container">\';\n\n    window.HIST.forEach(function(A, i) {\n      var isCBT = !!(A.isCBT || (A.mode === \'cbt\') || (A.label && A.label.indexOf(\'CBT\') !== -1));\n      var answeredCount = (A.NS || []).filter(function(n) { return A.S && A.S[n]; }).length;\n      var totalQ = (A.NS || []).length;\n      var dateStr = A.t ? new Date(A.t).toLocaleString() : \'Unknown date\';\n      var timeFormatted = typeof fmt === \'function\' ? fmt(A.total || 0) : (A.total || 0) + \'s\';\n\n      var badgeClass = isCBT ? \'cbt\' : \'practice\';\n      var badgeLabel = isCBT ? \'🏛️ CBT Exam\' : \'📚 Practice Test\';\n\n      var scoreText = \'\';\n      if (A.score !== undefined) {\n        var maxS = A.maxScore !== undefined ? A.maxScore : (totalQ * 4);\n        var acc = A.accuracy !== undefined ? A.accuracy : Math.round((A.correct || 0) / Math.max(1, answeredCount) * 100);\n        scoreText = \'<span class="att-score" style="font-weight:700;color:\' + (A.score >= 0 ? \'#16a34a\' : \'#dc2626\') + \';">Marks: \' + A.score + \' / \' + maxS + \' (\' + acc + \'% Acc)</span>\';\n      }\n\n      html += \'<div class="att-card" data-idx="\' + i + \'">\' +\n        \'<div class="att-header">\' +\n          \'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">\' +\n            \'<span class="att-badge \' + badgeClass + \'">\' + badgeLabel + \'</span>\' +\n            \'<span class="att-date">\' + dateStr + \'</span>\' +\n          \'</div>\' +\n          scoreText +\n        \'</div>\' +\n        \'<div class="att-stats-row">\' +\n          \'<span><b>Questions:</b> \' + (typeof esc === \'function\' ? esc(A.label || totalQ + \' questions\') : (A.label || totalQ)) + \'</span>\' +\n          \'<span><b>Answered:</b> \' + answeredCount + \' / \' + totalQ + \'</span>\' +\n          \'<span><b>Time:</b> \' + timeFormatted + \'</span>\' +\n        \'</div>\' +\n        \'<div class="att-actions">\';\n\n      if (isCBT) {\n        // CBT: Only Review Marks & Mistakes, Save File, Delete (NO Continue!)\n        html += \'<button type="button" class="att-btn review" data-a="v" data-i="\' + i + \'">📊 Review Marks &amp; Mistakes</button>\' +\n          \'<button type="button" class="att-btn" data-a="s" data-i="\' + i + \'">💾 Save File</button>\' +\n          \'<button type="button" class="att-btn delete" data-a="d" data-i="\' + i + \'">🗑️ Delete</button>\';\n      } else {\n        // Practice: Can Continue anytime!\n        html += \'<button type="button" class="att-btn continue" data-a="c" data-i="\' + i + \'">▶️ Continue Practice</button>\' +\n          \'<button type="button" class="att-btn review" data-a="v" data-i="\' + i + \'">🔍 Review Solutions</button>\' +\n          \'<button type="button" class="att-btn" data-a="s" data-i="\' + i + \'">💾 Save File</button>\' +\n          \'<button type="button" class="att-btn delete" data-a="d" data-i="\' + i + \'">🗑️ Delete</button>\';\n      }\n\n      html += \'</div></div>\';\n    });\n\n    html += \'</div>\';\n    html += \'<div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;">\' +\n      \'<button type="button" id="btnExportAllChapterAttempts" class="btn-export-all">📥 Export All Attempts (.json)</button>\' +\n      \'</div>\';\n\n    h.innerHTML = html;\n\n    // Attach button click events\n    h.querySelectorAll(\'.att-btn\').forEach(function(btn) {\n      btn.onclick = function() {\n        var idx = parseInt(btn.dataset.i, 10);\n        var act = btn.dataset.a;\n        var att = window.HIST[idx];\n        if (!att) return;\n\n        if (act === \'v\') {\n          if (typeof summary === \'function\') summary(att, true);\n        } else if (act === \'c\') {\n          if (typeof cont === \'function\') cont(att);\n        } else if (act === \'s\') {\n          if (typeof saveHist === \'function\') saveHist(att);\n        } else if (act === \'d\') {\n          if (confirm(\'Delete this attempt from your history?\\n\\nThis cannot be undone.\')) {\n            window.HIST.splice(idx, 1);\n            if (typeof sv === \'function\' && typeof KH !== \'undefined\') sv(KH, window.HIST);\n            window.renderStart();\n          }\n        }\n      };\n    });\n\n    var expBtn = document.getElementById(\'btnExportAllChapterAttempts\');\n    if (expBtn) {\n      expBtn.onclick = function() {\n        var pageTitle = (document.querySelector(\'h1\') ? document.querySelector(\'h1\').textContent.trim() : \'JEE_Practice\');\n        var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(window.HIST, null, 2));\n        var dlAnchor = document.createElement(\'a\');\n        dlAnchor.setAttribute("href", dataStr);\n        dlAnchor.setAttribute("download", pageTitle.replace(/[^a-zA-Z0-9_-]/g, \'_\') + "_Attempts.json");\n        document.body.appendChild(dlAnchor);\n        dlAnchor.click();\n        dlAnchor.remove();\n      };\n    }\n  };\n\n  // 7. CBT Session Exit & Continuation Prevention (User Item 9)\n  window.addEventListener(\'beforeunload\', function(e) {\n    if (window.started && window.isCBT && !window.examFinished) {\n      try { if (typeof KS !== \'undefined\') localStorage.removeItem(KS); } catch(err){}\n      e.preventDefault();\n      e.returnValue = \'You have an active CBT Exam in progress. Leaving will forfeit your exam session!\';\n      return e.returnValue;\n    }\n  });\n\n  // Run renderStart to immediately format existing history cards\n  if (typeof window.renderStart === \'function\') {\n    setTimeout(window.renderStart, 80);\n  }\n\n})();\n</script>'

def patch_practice_sheet(content):
    modified = False
    
    # 1. Inject or update TEST_MODE_AND_QCOUNT_HTML before <label>Practice time</label>
    if 'id="test_mode_box"' not in content:
        pattern_qc = r'<label>Number of questions</label>\s*<div class="tbox" id="qcount_box">.*?</div>\s*(?=<label>Practice time</label>)'
        if re.search(pattern_qc, content, re.DOTALL):
            content = re.sub(pattern_qc, TEST_MODE_AND_QCOUNT_HTML + '\n', content, flags=re.DOTALL)
            modified = True
        elif '<label>Practice time</label>' in content:
            content = content.replace('<label>Practice time</label>', TEST_MODE_AND_QCOUNT_HTML + '\n<label>Practice time</label>', 1)
            modified = True
            
    # 2. Inject or update ENHANCED_PRACTICE_SCRIPT before </body>
    pattern_script = r'<script>\s*\(function\(\)\{\s*// 1\. Mode and Q-Count Controller.*?</script>'
    if re.search(pattern_script, content, re.DOTALL):
        # Always ensure it is up to date with latest ENHANCED_PRACTICE_SCRIPT
        old_m = re.search(pattern_script, content, re.DOTALL).group(0)
        if old_m.strip() != ENHANCED_PRACTICE_SCRIPT.strip():
            content = re.sub(pattern_script, lambda m: ENHANCED_PRACTICE_SCRIPT, content, flags=re.DOTALL)
            modified = True
    elif 'cbtSubmitModal' not in content:
        pattern_script2 = r'<script>\s*\(function\(\)\{\s*function initQCount\(\)\{.*?</script>'
        if re.search(pattern_script2, content, re.DOTALL):
            content = re.sub(pattern_script2, lambda m: ENHANCED_PRACTICE_SCRIPT, content, flags=re.DOTALL)
            modified = True
        elif '</body>' in content:
            pos_b = content.rfind('</body>')
            content = content[:pos_b] + ENHANCED_PRACTICE_SCRIPT + '\n</body>' + content[pos_b+7:]
            modified = True
            
    return content, modified

def update_index_portal():
    index_path = os.path.join(ROOT_DIR, "index.html")
    if not os.path.exists(index_path):
        return
        
    with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
        
    subjects = ["Maths", "Physics", "Chemistry"]
    counts = {}
    all_chapters = []
    
    for s in subjects:
        s_dir = os.path.join(ROOT_DIR, s)
        if os.path.exists(s_dir):
            files = [f for f in os.listdir(s_dir) if f.endswith("PYQ Practice.html")]
            counts[s] = len(files)
            for file in sorted(files):
                name = file.replace(" PYQ Practice.html", "")
                all_chapters.append({
                    "name": name,
                    "subject": s,
                    "url": f"{s}/{file}".replace("\\", "/")
                })
        else:
            counts[s] = 0
            
    # Update badges on subject cards
    html = re.sub(r'(<a class="subject-card maths".*?<div class="subject-badge">)\d+ Chapters Ready', rf'\g<1>{counts.get("Maths", 0)} Chapters Ready', html, flags=re.DOTALL)
    html = re.sub(r'(<a class="subject-card physics".*?<div class="subject-badge">)\d+ Chapters Ready', rf'\g<1>{counts.get("Physics", 0)} Chapters Ready', html, flags=re.DOTALL)
    html = re.sub(r'(<a class="subject-card chemistry".*?<div class="subject-badge">)\d+ Chapters Ready', rf'\g<1>{counts.get("Chemistry", 0)} Chapters Ready', html, flags=re.DOTALL)
    
    # Update modal pill counts
    html = re.sub(r'All Subjects \(\d+\)', f'All Subjects ({len(all_chapters)})', html)
    html = re.sub(r'Physics \(\d+\)', f'Physics ({counts.get("Physics", 0)})', html)
    html = re.sub(r'Chemistry \(\d+\)', f'Chemistry ({counts.get("Chemistry", 0)})', html)
    html = re.sub(r'Maths \(\d+\)', f'Maths ({counts.get("Maths", 0)})', html)
    
    # Update CHAPTER_POOL array
    pool_json = json.dumps(all_chapters, indent=2)
    html = re.sub(r'var CHAPTER_POOL = \[.*?\];', f'var CHAPTER_POOL = {pool_json};', html, flags=re.DOTALL)
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"  [Portal Updated]  index.html (Maths: {counts.get('Maths',0)}, Physics: {counts.get('Physics',0)}, Chemistry: {counts.get('Chemistry',0)}, Total: {len(all_chapters)})")

def run_all_patches():
    print("=" * 60)
    print("JEE PYQ Practice - 1-Step Automated Patcher")
    print("=" * 60)
    
    total_scanned = 0
    total_modified = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if "backup" in root or ".git" in root or "node_modules" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            file_path = os.path.join(root, file)
            total_scanned += 1
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                original_content = f.read()
                
            content = original_content
            file_changed = False
            
            # 1. Option Fixes & Question Count Sampling for PYQ practice files
            if "PYQ Practice.html" in file:
                content, opt_mod = fix_option_images_in_file(content)
                if opt_mod:
                    file_changed = True
                    print(f"  [Options Fixed]   {os.path.relpath(file_path, ROOT_DIR)}")
                    
                content, qc_mod = patch_practice_sheet(content)
                if qc_mod:
                    file_changed = True
                    print(f"  [Q-Count Added]   {os.path.relpath(file_path, ROOT_DIR)}")
                    
            # 2. Type Notes PDF & Pagination
            if "Type Notes.html" in file:
                content, pdf_mod = patch_type_notes(content)
                if pdf_mod:
                    file_changed = True
                    print(f"  [PDF Added]       {os.path.relpath(file_path, ROOT_DIR)}")
                    
            # 3. Dark Mode Engine across all HTML files
            content, dark_mod = patch_dark_mode(content, file)
            if dark_mod:
                file_changed = True
                print(f"  [Dark Mode]       {os.path.relpath(file_path, ROOT_DIR)}")
                
            if file_changed:
                make_backup(file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                total_modified += 1
            original_content = None
            content = None
            import gc
            gc.collect()
                
    print("=" * 60)
    update_index_portal()
    print(f"Patching complete! Scanned: {total_scanned} files | Updated: {total_modified} files")
    print("Pristine copies are safely archived in the 'backup/' directory.")
    print("=" * 60)

if __name__ == "__main__":
    run_all_patches()
