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
/* =================== TRUE AMOLED BLACK DARK MODE =================== */
[data-theme="dark"] {
  --ink: #ffffff;
  --mut: #a1a1aa;
  --line: #222222;
  --bg: #000000;
  --accl: #081a36;
  --accb: #3b82f6;
  --hdr: #000000;
  --hdrtx: #ffffff;
  --tmbg: rgba(255, 255, 255, 0.08);
  --hdrline: #222222;
}

[data-theme="dark"] body {
  background: #000000 !important;
  color: #f4f4f5 !important;
}

[data-theme="dark"] a {
  color: #3b82f6 !important;
}

/* 1. START PANEL & GENERAL PANELS */
[data-theme="dark"] .panel,
[data-theme="dark"] .main,
[data-theme="dark"] #done,
[data-theme="dark"] .sec,
[data-theme="dark"] .card {
  background: #0a0a0a !important;
  border-color: #222222 !important;
  color: #f4f4f5 !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.8) !important;
}

[data-theme="dark"] .panel h2,
[data-theme="dark"] h1, [data-theme="dark"] h2, [data-theme="dark"] h3 {
  color: #ffffff !important;
}

[data-theme="dark"] .banner {
  background: #000000 !important;
  border-color: #262626 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .banner b {
  color: #ffffff !important;
}
[data-theme="dark"] .banner a {
  color: #3b82f6 !important;
  text-decoration: underline !important;
}

[data-theme="dark"] .tbox {
  background: #000000 !important;
  border-color: #262626 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .panel label,
[data-theme="dark"] label.rad {
  color: #f4f4f5 !important;
}
[data-theme="dark"] #typelist .cnt {
  color: #a1a1aa !important;
}
[data-theme="dark"] #typelist .all span,
[data-theme="dark"] .all span {
  color: #3b82f6 !important;
  text-decoration: underline !important;
}
[data-theme="dark"] #typelist hr {
  border-color: #222222 !important;
}
[data-theme="dark"] .tin input,
[data-theme="dark"] .panel input[type=number],
[data-theme="dark"] .num,
[data-theme="dark"] input[type=text],
[data-theme="dark"] textarea {
  background: #000000 !important;
  border-color: #2e2e2e !important;
  color: #ffffff !important;
}

/* 2. TOP HEADER BAR */
[data-theme="dark"] .top {
  background: #000000 !important;
  border-bottom: 1px solid #222222 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .top h1 {
  color: #ffffff !important;
}
[data-theme="dark"] .top .tm {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
}

/* 3. QUESTION HEADER & BLUE SUBHEADER BAR */
[data-theme="dark"] .qhead {
  background: #000000 !important;
  border-color: #222222 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .qhead b,
[data-theme="dark"] #qno {
  color: #ffffff !important;
}
[data-theme="dark"] .qhead small,
[data-theme="dark"] .qt {
  color: #a1a1aa !important;
}
[data-theme="dark"] #qtime {
  color: #ffffff !important;
  font-weight: 700 !important;
}
[data-theme="dark"] .starbtn {
  background: #0a0a0a !important;
  border-color: #2e2e2e !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .starbtn.on {
  background: #2e1a05 !important;
  border-color: #d97706 !important;
  color: #fbbf24 !important;
}

/* #typeln (Subheader Bar) */
[data-theme="dark"] #typeln {
  background: #000000 !important;
  color: #ffffff !important;
  border: 1px solid #222224 !important;
  font-weight: 600 !important;
}

[data-theme="dark"] .src {
  color: #a1a1aa !important;
}
[data-theme="dark"] .stem {
  color: #f4f4f5 !important;
}
[data-theme="dark"] .stem p {
  color: #f4f4f5 !important;
}

/* 4. MATH EQUATIONS - PURE WHITE */
[data-theme="dark"] math,
[data-theme="dark"] math * {
  color: #ffffff !important;
  fill: #ffffff !important;
}

/* 5. DIAGRAMS / IMAGES - WHITE CONTAINER */
[data-theme="dark"] img,
[data-theme="dark"] .fig {
  background: #ffffff !important;
  border-radius: 8px !important;
  padding: 6px !important;
  border: 1px solid #333333 !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.7) !important;
  display: inline-block !important;
}

/* 6. OPTIONS */
[data-theme="dark"] .o {
  background: #0d0d0d !important;
  border: 1.5px solid #262626 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .o:hover {
  background: #171717 !important;
  border-color: #3f3f46 !important;
}
[data-theme="dark"] .o .ol {
  background: #171717 !important;
  color: #a1a1aa !important;
  border: 1px solid #27272a !important;
}
[data-theme="dark"] .o.sel {
  background: #0f1d38 !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.sel .ol {
  background: #2563eb !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.ok {
  background: #042414 !important;
  border-color: #10b981 !important;
  color: #ecfdf5 !important;
}
[data-theme="dark"] .o.ok .ol {
  background: #10b981 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.bad {
  background: #330808 !important;
  border-color: #ef4444 !important;
  color: #fef2f2 !important;
}
[data-theme="dark"] .o.bad .ol {
  background: #ef4444 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.dead {
  opacity: 0.3 !important;
}

/* Feedback & numerical checking */
[data-theme="dark"] .num.ok { background: #042414 !important; border-color: #10b981 !important; color: #ecfdf5 !important; }
[data-theme="dark"] .num.bad { background: #330808 !important; border-color: #ef4444 !important; color: #fef2f2 !important; }
[data-theme="dark"] .chkres.r { background: #042414 !important; color: #a7f3d0 !important; border-color: #059669 !important; }
[data-theme="dark"] .chkres.w { background: #330808 !important; color: #fecaca !important; border-color: #dc2626 !important; }
[data-theme="dark"] .chkres.h { background: #0d0d0d !important; color: #d4d4d8 !important; border-color: #27272a !important; }

/* 7. BOTTOM NAVIGATION BAR */
[data-theme="dark"] .foot {
  background: #000000 !important;
  border-top: 1px solid #222222 !important;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.7) !important;
}
[data-theme="dark"] .foot .btn {
  background: #121212 !important;
  color: #f4f4f5 !important;
  border-color: #27272a !important;
}
[data-theme="dark"] .foot .btn:hover {
  background: #222222 !important;
}
[data-theme="dark"] .foot .btn:disabled {
  opacity: 0.25 !important;
  background: #0a0a0a !important;
  color: #52525b !important;
  border-color: #18181b !important;
}
[data-theme="dark"] .btn.pur {
  background: #7c3aed !important;
  border-color: #8b5cf6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .btn.grn {
  background: #16a34a !important;
  border-color: #22c55e !important;
  color: #ffffff !important;
}

/* 8. RIGHT SIDE QUESTION PALETTE */
[data-theme="dark"] .side {
  background: #0a0a0a !important;
  border: 1px solid #222222 !important;
  color: #f4f4f5 !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.7) !important;
}
[data-theme="dark"] .side::-webkit-scrollbar {
  width: 8px !important;
}
[data-theme="dark"] .side::-webkit-scrollbar-track {
  background: #0a0a0a !important;
}
[data-theme="dark"] .side::-webkit-scrollbar-thumb {
  background: #27272a !important;
  border-radius: 4px !important;
}
[data-theme="dark"] .side h3 {
  color: #a1a1aa !important;
}
[data-theme="dark"] .side .tname {
  color: #ffffff !important;
}
[data-theme="dark"] .pbtn {
  background: #18181b !important;
  border-color: #27272a !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .pbtn:hover {
  background: #27272a !important;
}
[data-theme="dark"] .pbtn.cur {
  outline: 2px solid #38bdf8 !important;
  outline-offset: 1px !important;
}
[data-theme="dark"] .pbtn.ans {
  background: #15803d !important;
  border-color: #22c55e !important;
  color: #ffffff !important;
}
[data-theme="dark"] .pbtn.rev {
  background: #7e22ce !important;
  border-color: #a855f7 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .pbtn.r_ans {
  background: #7e22ce !important;
  border-color: #22c55e !important;
  color: #ffffff !important;
}

/* 9. TABLES & HISTORY */
[data-theme="dark"] table {
  background: #000000 !important;
  color: #f4f4f5 !important;
  border-color: #222222 !important;
}
[data-theme="dark"] th {
  background: #0d0d0d !important;
  color: #93c5fd !important;
  border-color: #222222 !important;
}
[data-theme="dark"] td {
  border-color: #222222 !important;
}
[data-theme="dark"] .actr {
  background: #000000 !important;
}

/* 10. SUMMARY / REVIEW SCREEN */
[data-theme="dark"] .tag.E { background: #042414 !important; color: #a7f3d0 !important; }
[data-theme="dark"] .tag.M { background: #2e1a05 !important; color: #fde68a !important; }
[data-theme="dark"] .tag.D { background: #330808 !important; color: #fecaca !important; }
[data-theme="dark"] .qcard {
  background: #0d0d0d !important;
  border-color: #222222 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .flt select {
  background: #000000 !important;
  color: #f4f4f5 !important;
  border-color: #2e2e2e !important;
}

/* 11. CHAPTER INDEX & SUBJECT INDEX PAGES */
[data-theme="dark"] header {
  background: #000000 !important;
  border-bottom: 1px solid #222222 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] header h1 {
  color: #ffffff !important;
}
[data-theme="dark"] header p {
  color: #a1a1aa !important;
}
[data-theme="dark"] header a {
  color: #93c5fd !important;
}

[data-theme="dark"] #q {
  background: #0a0a0a !important;
  border: 1.5px solid #2e2e2e !important;
  color: #ffffff !important;
}
[data-theme="dark"] #q::placeholder {
  color: #71717a !important;
}

[data-theme="dark"] .lg {
  background: #0d0d0d !important;
  border: 1px solid #222222 !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .lg b {
  color: #ffffff !important;
}
[data-theme="dark"] .lg ul, [data-theme="dark"] .lg li {
  color: #d4d4d8 !important;
}

[data-theme="dark"] .strip,
[data-theme="dark"] .strip.cA,
[data-theme="dark"] .strip.cB,
[data-theme="dark"] .strip.cC,
[data-theme="dark"] .strip.cD {
  background: #0a0a0a !important;
  border: 1px solid #222222 !important;
  color: #f4f4f5 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5) !important;
}
[data-theme="dark"] .strip.cA { border-left: 6px solid #22c55e !important; }
[data-theme="dark"] .strip.cB { border-left: 6px solid #84cc16 !important; }
[data-theme="dark"] .strip.cC { border-left: 6px solid #f97316 !important; }
[data-theme="dark"] .strip.cD { border-left: 6px solid #71717a !important; }

[data-theme="dark"] .strip .no {
  color: #71717a !important;
}
[data-theme="dark"] .strip .mid b {
  color: #ffffff !important;
}
[data-theme="dark"] .strip .mid span {
  color: #a1a1aa !important;
}
[data-theme="dark"] .strip .gl {
  color: #d4d4d8 !important;
}
[data-theme="dark"] .strip .gl b {
  color: #ffffff !important;
}

[data-theme="dark"] .tg em {
  background: #000000 !important;
  border-color: #27272a !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .tg em.pH {
  background: #052e16 !important;
  color: #86efac !important;
  border-color: #16a34a !important;
}
[data-theme="dark"] .tg em.pM {
  background: #422006 !important;
  color: #fde047 !important;
  border-color: #ca8a04 !important;
}
[data-theme="dark"] .tg em.pL {
  background: #18181b !important;
  color: #d4d4d8 !important;
  border-color: #27272a !important;
}

[data-theme="dark"] .lk a {
  background: #000000 !important;
  border: 1px solid #27272a !important;
  color: #93c5fd !important;
}
[data-theme="dark"] .lk a:hover {
  background: #18181b !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .lk a.go {
  background: #2563eb !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .lk a.go:hover {
  background: #1d4ed8 !important;
}

/* 12. FILTER GROUPS & DIFFICULTY PILLS (.gf, .tc, .pill) */
[data-theme="dark"] .selsum {
  background: #0c1929 !important;
  border: 2px solid #2563eb !important;
  color: #ffffff !important;
}
[data-theme="dark"] .gf {
  background: #0a0a0a !important;
  border: 2px solid #2563eb !important;
  color: #ffffff !important;
}
[data-theme="dark"] .gf .gft {
  color: #ffffff !important;
}
[data-theme="dark"] .gf .gfn {
  color: #a1a1aa !important;
}
[data-theme="dark"] .tc {
  background: #0a0a0a !important;
  border: 1px solid #222222 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .tc .th span {
  color: #ffffff !important;
}
[data-theme="dark"] .tc .tcnt {
  color: #a1a1aa !important;
}
[data-theme="dark"] .tc.zero .th span {
  color: #52525b !important;
}
[data-theme="dark"] .grp .gl {
  color: #a1a1aa !important;
}
[data-theme="dark"] #typelist .pill input+span {
  background: #000000 !important;
  border: 2px solid #27272a !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] #typelist .pill input:checked+span {
  background: #1e40af !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] #typelist .pill input:checked+span .cc {
  color: #bfdbfe !important;
}
[data-theme="dark"] #typelist .pill .cc {
  color: #a1a1aa !important;
}

/* 13. TYPE NOTES PAGES (.page, .how, .ed, .gt, details, #sym) */
[data-theme="dark"] .page {
  background: #0a0a0a !important;
  border-color: #222222 !important;
  color: #f4f4f5 !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7) !important;
}

[data-theme="dark"] .how {
  background: #000000 !important;
  border: 1px solid #222222 !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .how h3 {
  color: #ffffff !important;
}
[data-theme="dark"] .how p,
[data-theme="dark"] .how ol,
[data-theme="dark"] .how li {
  color: #d4d4d8 !important;
}

[data-theme="dark"] .ed {
  background: #000000 !important;
  border: 1px solid #2e2e2e !important;
  color: #ffffff !important;
}
[data-theme="dark"] .ed:focus {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4) !important;
}

[data-theme="dark"] .gt {
  border-color: #222222 !important;
}
[data-theme="dark"] .gt td {
  border-color: #222222 !important;
  color: #f4f4f5 !important;
  background: #000000 !important;
}
[data-theme="dark"] .gt tr:first-child td {
  background: #0d0d0d !important;
  color: #93c5fd !important;
}
[data-theme="dark"] .gt td:first-child {
  background: #0d0d0d !important;
  color: #f4f4f5 !important;
}

[data-theme="dark"] .rev {
  background: #042414 !important;
  border-color: #10b981 !important;
  color: #ecfdf5 !important;
}
[data-theme="dark"] .rev h4 {
  color: #6ee7b7 !important;
}

[data-theme="dark"] .top {
  background: #000000 !important;
  border-bottom: 1px solid #222222 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .top h1 {
  color: #ffffff !important;
}
[data-theme="dark"] .top a {
  color: #93c5fd !important;
}

[data-theme="dark"] .btn {
  background: #121212 !important;
  border-color: #27272a !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .btn:hover {
  background: #222222 !important;
}
[data-theme="dark"] .btn.pri {
  background: #2563eb !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .btn.pri:hover {
  background: #1d4ed8 !important;
}

[data-theme="dark"] .sm {
  color: #a1a1aa !important;
}

/* Scientific Symbol Bar (#sym) */
#sym {
  display: flex !important;
  align-items: center;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}
body {
  padding-bottom: 60px !important;
}
[data-theme="dark"] #sym {
  background: #000000 !important;
  border-top: 1px solid #222222 !important;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.7) !important;
}
[data-theme="dark"] #sym > span {
  color: #93c5fd !important;
  font-weight: 700 !important;
}
[data-theme="dark"] #sym button {
  background: #121212 !important;
  color: #f4f4f5 !important;
  border: 1px solid #27272a !important;
}
[data-theme="dark"] #sym button:hover {
  background: #222222 !important;
  border-color: #60a5fa !important;
  color: #60a5fa !important;
}
[data-theme="dark"] #sym button.w {
  background: #18181b !important;
  color: #93c5fd !important;
  border-color: #3b82f6 !important;
}

/* 14. SUBJECT SWITCHER POPUP & SIDEBAR (#sw, #swb, .sj) */
[data-theme="dark"] #sw {
  background: #0a0a0a !important;
  border: 1px solid #222222 !important;
  box-shadow: 0 4px 28px rgba(0, 0, 0, 0.8) !important;
}
[data-theme="dark"] #sw h2 {
  color: #ffffff !important;
  font-weight: 700 !important;
}
[data-theme="dark"] #sw .x {
  color: #d4d4d8 !important;
}
[data-theme="dark"] #sw a.sj {
  background: #000000 !important;
  border-color: #222222 !important;
  color: #f4f4f5 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
}
[data-theme="dark"] #sw a.sj b {
  color: #ffffff !important;
}
[data-theme="dark"] #sw a.sj span {
  color: #d4d4d8 !important;
}
[data-theme="dark"] #sw a.sj:hover {
  background: #18181b !important;
  border-color: #3b82f6 !important;
}
[data-theme="dark"] #sw a.all {
  color: #93c5fd !important;
}
[data-theme="dark"] #sw a.all:hover {
  color: #bfdbfe !important;
}
[data-theme="dark"] #swb {
  background: #0a0a0a !important;
  border: 1px solid #27272a !important;
  color: #f4f4f5 !important;
}

/* 15. HIGH-CONTRAST TEXT ENHANCEMENTS */
[data-theme="dark"] header p,
[data-theme="dark"] .top p {
  color: #e4e4e7 !important;
  opacity: 1 !important;
}
[data-theme="dark"] .note {
  background: #000000 !important;
  border: 1px solid #222222 !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] #q::placeholder {
  color: #a1a1aa !important;
}
[data-theme="dark"] .lg {
  color: #e4e4e7 !important;
}
[data-theme="dark"] .lg ul,
[data-theme="dark"] .lg li {
  color: #d4d4d8 !important;
}
[data-theme="dark"] .strip .mid span,
[data-theme="dark"] .strip .gl {
  color: #d4d4d8 !important;
}

/* 16. QUESTION COUNT SELECTION BOX & PRESETS */
#qcount_box {
  margin-bottom: 14px;
}
.qpreset {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
}
.qpreset:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}
.qpreset.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 700;
}
[data-theme="dark"] #qcount_box {
  background: #000000 !important;
  border-color: #262626 !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .qpreset {
  background: #0a0a0a !important;
  border-color: #27272a !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .qpreset:hover {
  background: #18181b !important;
  border-color: #60a5fa !important;
}
[data-theme="dark"] .qpreset.active {
  background: #2563eb !important; border-color: #2563eb !important; color: #ffffff !important; }
[data-theme="dark"] #custom_qc {
  background: #000000 !important;
  border-color: #2e2e2e !important;
  color: #ffffff !important;
}

/* 17. AMOLED CARDS & MODAL (HOME & PORTALS) */
[data-theme="dark"] .subject-card {
  background: #0a0a0a !important;
  border-color: #222222 !important;
  color: #f4f4f5 !important;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.7) !important;
}
[data-theme="dark"] .subject-card:hover {
  background: #111111 !important;
  border-color: #333333 !important;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.9) !important;
}
[data-theme="dark"] .subject-card.maths { border-top: 5px solid #3b82f6 !important; }
[data-theme="dark"] .subject-card.physics { border-top: 5px solid #a855f7 !important; }
[data-theme="dark"] .subject-card.chemistry { border-top: 5px solid #10b981 !important; }
[data-theme="dark"] .subject-card.maths .subject-badge { background: #18181b !important; color: #93c5fd !important; }
[data-theme="dark"] .subject-card.physics .subject-badge { background: #2e1065 !important; color: #d8b4fe !important; }
[data-theme="dark"] .subject-card.chemistry .subject-badge { background: #022c22 !important; color: #6ee7b7 !important; }
[data-theme="dark"] .subject-card h2 { color: #ffffff !important; }
[data-theme="dark"] .subject-card.maths h2 { color: #ffffff !important; }
[data-theme="dark"] .subject-card.physics h2 { color: #c084fc !important; }
[data-theme="dark"] .subject-card.chemistry h2 { color: #34d399 !important; }
[data-theme="dark"] .subject-desc { color: #d4d4d8 !important; }
[data-theme="dark"] .subject-footer { color: #a1a1aa !important; border-top-color: #222222 !important; }

[data-theme="dark"] .random-btn {
  background: #0a0a0a !important;
  border-color: #2563eb !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.7) !important;
}
[data-theme="dark"] .random-btn:hover {
  background: #111111 !important;
  border-color: #3b82f6 !important;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.9) !important;
}
[data-theme="dark"] .random-badge {
  background: #18181b !important;
  color: #93c5fd !important;
}
[data-theme="dark"] .random-title {
  color: #ffffff !important;
}
[data-theme="dark"] .random-desc {
  color: #d4d4d8 !important;
}

[data-theme="dark"] .modal-overlay {
  background: rgba(0, 0, 0, 0.85) !important;
}
[data-theme="dark"] .modal-box {
  background: #0a0a0a !important;
  border: 1px solid #27272a !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.9) !important;
  color: #f4f4f5 !important;
}
[data-theme="dark"] .modal-header h3 {
  color: #ffffff !important;
}
[data-theme="dark"] .modal-close {
  color: #a1a1aa !important;
}
[data-theme="dark"] .modal-close:hover {
  color: #ffffff !important;
}
[data-theme="dark"] .modal-desc {
  color: #d4d4d8 !important;
}
[data-theme="dark"] .modal-section-title {
  color: #a1a1aa !important;
}
[data-theme="dark"] .pool-opt {
  background: #000000 !important;
  border-color: #27272a !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .pool-opt:hover {
  background: #18181b !important;
  border-color: #3b82f6 !important;
}
[data-theme="dark"] .pool-opt.active {
  background: #2563eb !important; border-color: #2563eb !important; color: #ffffff !important; }
[data-theme="dark"] .pill-btn {
  background: #000000 !important;
  border-color: #27272a !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .pill-btn:hover {
  background: #18181b !important;
  border-color: #3b82f6 !important;
}
[data-theme="dark"] .pill-btn.active {
  background: #2563eb !important; border-color: #2563eb !important; color: #ffffff !important; }
[data-theme="dark"] .pill-btn input[type=number] {
  background: #0a0a0a !important;
  border-color: #2e2e2e !important;
  color: #ffffff !important;
}
[data-theme="dark"] .btn-cancel {
  background: #000000 !important;
  border: 1px solid #27272a !important;
  color: #d4d4d8 !important;
}
[data-theme="dark"] .btn-cancel:hover {
  background: #18181b !important;
  color: #ffffff !important;
}

.theme-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: inherit;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.theme-btn:hover { background: rgba(255, 255, 255, 0.3); }
[data-theme="dark"] .theme-btn {
  background: #121212;
  border: 1px solid #27272a;
  color: #f4f4f5;
}
[data-theme="dark"] .theme-btn:hover {
  background: #222222;
}


/* ==========================================================================
   CBT EXAM MODE & VISUAL MODERNIZATION STYLING
   ========================================================================== */
.mode-card.active {
  border-color: #2563eb !important;
  background: #eff6ff !important;
}
.mode-card {
  user-select: none;
}
[data-theme="dark"] .mode-card {
  background: #0a0a0c !important;
  border-color: #222224 !important;
}
[data-theme="dark"] #mode_card_cbt.active {
  background: #081a36 !important;
  border-color: #3b82f6 !important;
}
[data-theme="dark"] #mode_card_practice.active {
  background: #18181b !important;
  border-color: #3f3f46 !important;
}
[data-theme="dark"] .mode-card div div:first-child span:first-child {
  color: #ffffff !important;
}
[data-theme="dark"] .mode-card div div:last-child {
  color: #94a3b8 !important;
}

/* Exam Progress Bar at Top */
#examProgressBar {
  position: absolute;
  top: 0;
  left: 0;
  height: 3.5px;
  background: #2563eb;
  width: 0%;
  transition: width 0.3s ease, background-color 0.3s ease;
  z-index: 100;
}
[data-theme="dark"] #examProgressBar {
  background: #3b82f6;
}

/* CBT Mode Palette Styling (Official NTA JEE Colors) */
.cbt-mode .chk {
  display: none !important;
}
.cbt-mode #savecur {
  display: none !important;
}
.cbt-mode #nav button.an {
  background: #16a34a !important;
  color: #ffffff !important;
  border-radius: 4px !important;
}
.cbt-mode #nav button.na {
  background: #ef4444 !important;
  color: #ffffff !important;
  border-radius: 4px !important;
}
.cbt-mode #nav button.nv {
  background: #e2e8f0 !important;
  color: #475569 !important;
  border-radius: 4px !important;
}
[data-theme="dark"] .cbt-mode #nav button.nv {
  background: #1c1c1f !important;
  color: #94a3b8 !important;
  border-color: #2a2a2e !important;
}
.cbt-mode #nav button.mk {
  background: #9333ea !important;
  color: #ffffff !important;
  border-radius: 50% !important;
}
.cbt-mode #nav button.am {
  background: #9333ea !important;
  color: #ffffff !important;
  position: relative !important;
  border-radius: 50% !important;
}
.cbt-mode #nav button.am::after {
  content: '';
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 7px;
  height: 7px;
  background: #16a34a;
  border-radius: 50%;
  border: 1.5px solid #ffffff;
}

/* Option Elimination (Right click / Alt click) */
.o.eliminated {
  opacity: 0.35 !important;
  text-decoration: line-through !important;
  pointer-events: auto !important;
  background: rgba(0,0,0,0.04) !important;
}
[data-theme="dark"] .o.eliminated {
  background: rgba(255,255,255,0.04) !important;
}

/* Enhanced Post-Exam Scorecard & Review Cards */
.cbt-scorecard {
  margin: 10px 0 30px;
}
.cbt-score-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
[data-theme="dark"] .cbt-score-hero {
  background: #0a0a0c !important;
  border-color: #222224 !important;
}
.cbt-score-left {
  flex: 1;
  min-width: 260px;
}
.cbt-score-tag {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #2563eb;
  background: #eff6ff;
  padding: 3px 8px;
  border-radius: 4px;
}
[data-theme="dark"] .cbt-score-tag {
  background: #081a36 !important;
  color: #93c5fd !important;
}
.cbt-score-title {
  margin: 10px 0 4px;
  font-size: 24px;
  font-weight: 800;
}
[data-theme="dark"] .cbt-score-title {
  color: #ffffff !important;
}
.cbt-score-meta {
  color: #64748b;
  font-size: 13px;
  margin: 0;
}
[data-theme="dark"] .cbt-score-meta {
  color: #94a3b8 !important;
}
.cbt-big-score {
  font-size: 34px;
  font-weight: 900;
  color: #16a34a;
}
.cbt-big-score.neg {
  color: #ef4444;
}
.cbt-big-score small {
  font-size: 18px;
  font-weight: 500;
  color: #64748b;
}
[data-theme="dark"] .cbt-big-score small {
  color: #94a3b8 !important;
}

/* SVG Donut Chart */
.cbt-donut-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
}
.cbt-donut-svg {
  width: 95px;
  height: 95px;
  transform: rotate(-90deg);
}
.cbt-donut-legend {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12.5px;
  font-weight: 600;
}
[data-theme="dark"] .cbt-donut-legend {
  color: #cbd5e1 !important;
}
.cbt-donut-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.cbt-donut-dot {
  width: 9px;
  height: 9px;
  border-radius: 2px;
}

/* Metrics Grid */
.cbt-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}
.cbt-metric-item {
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
[data-theme="dark"] .cbt-metric-item {
  background: #0a0a0c !important;
  border-color: #222224 !important;
}
.cbt-metric-lbl {
  font-size: 11.5px;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
}
[data-theme="dark"] .cbt-metric-lbl {
  color: #94a3b8 !important;
}
.cbt-metric-num {
  font-size: 20px;
  font-weight: 800;
}
[data-theme="dark"] .cbt-metric-num {
  color: #ffffff !important;
}

/* Question Review Filters */
.review-filter-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.rf-pill {
  border: 1px solid var(--border, #cbd5e1);
  background: var(--surface, #f8fafc);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  color: inherit;
}
[data-theme="dark"] .rf-pill {
  background: #0a0a0c !important;
  border-color: #222224 !important;
  color: #94a3b8 !important;
}
.rf-pill.active {
  border-color: #2563eb !important;
  background: #2563eb !important;
  color: #ffffff !important;
}
.review-card {
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 14px;
}
[data-theme="dark"] .review-card {
  background: #0a0a0c !important;
  border-color: #222224 !important;
}
.review-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.review-pill {
  font-size: 12px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 4px;
}
.review-pill.corr {
  background: #dcfce7;
  color: #15803d;
}
.review-pill.inc {
  background: #fee2e2;
  color: #b91c1c;
}
.review-pill.unatt {
  background: #f1f5f9;
  color: #64748b;
}
[data-theme="dark"] .review-pill.corr {
  background: #052e16;
  color: #4ade80;
}
[data-theme="dark"] .review-pill.inc {
  background: #450a0a;
  color: #f87171;
}
[data-theme="dark"] .review-pill.unatt {
  background: #18181b;
  color: #94a3b8;
}

[data-theme="dark"] .review-answers-box {
  background: #111114 !important;
  color: #e4e4e7 !important;
}

[data-theme="dark"] .review-opts div[style*="background:#f8fafc"] {
  background: #111114 !important;
  border-color: #222224 !important;
  color: #e4e4e7 !important;
}

[data-theme="dark"] .review-opts div[style*="background:#dcfce7"] {
  background: #052e16 !important;
  border-color: #16a34a !important;
  color: #ffffff !important;
}

[data-theme="dark"] .review-opts div[style*="background:#fee2e2"] {
  background: #450a0a !important;
  border-color: #ef4444 !important;
  color: #ffffff !important;
}

/* Modals (CBT Submit & Hotkeys) */
.cbt-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
  backdrop-filter: blur(2px);
}
.cbt-modal-box {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}
[data-theme="dark"] .cbt-modal-box {
  background: #0a0a0c !important;
  border-color: #27272a !important;
  color: #ffffff !important;
}
.cbt-summary-table {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0 20px;
  font-size: 14px;
}
.cbt-summary-table td {
  padding: 8px 6px;
  border-bottom: 1px solid #e2e8f0;
}
[data-theme="dark"] .cbt-summary-table td {
  border-bottom-color: #222224 !important;
}
.cbt-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  margin-right: 6px;
}
.cbt-dot.green { background: #16a34a; }
.cbt-dot.red { background: #ef4444; }
.cbt-dot.purple { background: #9333ea; }
.cbt-dot.purple-green { background: #9333ea; border: 2px solid #16a34a; }
.cbt-dot.gray { background: #94a3b8; }

/* Hotkeys Modal */
.hotkeys-table {
  width: 100%;
  font-size: 13px;
  border-collapse: collapse;
  margin-top: 10px;
}
.hotkeys-table td {
  padding: 6px 4px;
  border-bottom: 1px solid #e2e8f0;
}
[data-theme="dark"] .hotkeys-table td {
  border-bottom-color: #222224 !important;
}
.kbd-key {
  display: inline-block;
  padding: 2px 7px;
  font-family: monospace;
  font-size: 12px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  box-shadow: 0 1px 1px rgba(0,0,0,0.1);
  color: #0f172a;
}
[data-theme="dark"] .kbd-key {
  background: #18181b !important;
  border-color: #3f3f46 !important;
  color: #ffffff !important;
}

/* Impeccable Browser Surface Polish */
[data-theme="dark"] ::selection {
  background: rgba(59, 130, 246, 0.35) !important;
  color: #ffffff !important;
}
::selection {
  background: rgba(37, 99, 235, 0.25);
  color: inherit;
}
* {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}
[data-theme="dark"] * {
  scrollbar-color: #27272a transparent;
}
:focus-visible {
  outline: 2px solid #3b82f6 !important;
  outline-offset: 2px !important;
}
.tm, .btn, .o, .ol, .kbd-key, .cbt-metric-num, .cbt-big-score, .cbt-summary-table td b, .metric-value, .ch-stats-row {
  font-variant-numeric: tabular-nums;
}
"""

THEME_TOGGLE_JS = """
<script>
function initThemeToggle() {
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
      b.innerHTML = dark ? '☀️ Light' : '🌙 Dark';
    });
  }
  var isDark = localStorage.getItem('jee_theme') === 'dark' || 
    (!localStorage.getItem('jee_theme') && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  applyTheme(isDark);
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.theme-btn');
    if (btn) {
      var currentlyDark = document.documentElement.getAttribute('data-theme') === 'dark';
      applyTheme(!currentlyDark);
    }
  });
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initThemeToggle);
} else {
  initThemeToggle();
}
</script>
"""

def patch_dark_mode(content):
    modified = False
    
    # 1. Anti-flicker script in head
    if "localStorage.getItem('jee_theme')" not in content and "<head>" in content:
        content = content.replace("<head>", "<head>\n" + HEAD_PREVENT_FLICKER, 1)
        modified = True
        
    # 2. AMOLED Dark mode CSS (Replace existing dark mode block or inject)
    pattern_legacy_tn = r'/\* =+ COMPREHENSIVE DARK MODE \(TYPE NOTES\) =+ \*/.*?\[data-theme=[\'"]dark[\'"]\] \.theme-btn:hover\s*\{[^}]+\}\s*'
    if re.search(pattern_legacy_tn, content, re.DOTALL):
        content = re.sub(pattern_legacy_tn, "", content, flags=re.DOTALL)
        modified = True

    if "TRUE AMOLED BLACK DARK MODE" in content:
        idx_start = content.find("/* =================== TRUE AMOLED BLACK DARK MODE =================== */")
        idx_style = content.find("</style>", idx_start)
        if idx_start != -1 and idx_style != -1:
            existing_block = content[idx_start:idx_style].strip()
            if existing_block != DARK_MODE_CSS.strip():
                content = content[:idx_start] + DARK_MODE_CSS.strip() + "\n" + content[idx_style:]
                modified = True
    elif "COMPREHENSIVE HIGH-CONTRAST DARK MODE" in content:
        idx_start = content.find("/* =================== COMPREHENSIVE HIGH-CONTRAST DARK MODE =================== */")
        idx_style = content.find("</style>", idx_start)
        if idx_start != -1 and idx_style != -1:
            content = content[:idx_start] + MODAL_LIGHT_CSS + "\n" + DARK_MODE_CSS.strip() + "\n" + content[idx_style:]
            modified = True
    else:
        pattern = r'/\* =+ COMPREHENSIVE DARK MODE =+ \*/.*?\[data-theme=[\'"]dark[\'"]\] \.theme-btn:hover\s*\{[^}]+\}'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, lambda m: DARK_MODE_CSS.strip(), content, flags=re.DOTALL)
            modified = True
        else:
            if "</style>" in content:
                content = content.replace("</style>", DARK_MODE_CSS + "\n</style>", 1)
                modified = True
        
    # 3. Add toggle button in start screen or header if missing
    if 'class="theme-btn"' not in content:
        pattern = r'(<div id="start"[^>]*>\s*)(<a href="index\.html"[^>]*>.*?</a>)'
        m = re.search(pattern, content)
        if m:
            replacement = (
                m.group(1) +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                m.group(2) +
                '<button class="theme-btn" type="button" title="Toggle theme">🌙 Dark</button></div>'
            )
            content = content[:m.start()] + replacement + content[m.end():]
            modified = True
        else:
            m2 = re.search(r'(<h1[^>]*>.*?</h1>)', content)
            if m2:
                btn = '<div style="display:flex;justify-content:flex-end;margin-bottom:8px;"><button class="theme-btn" type="button" title="Toggle theme">🌙 Dark</button></div>\n'
                content = content[:m2.start()] + btn + content[m2.start():]
                modified = True
                
    # 4. Toggle JS listener
    if "initThemeToggle" not in content and "</body>" in content:
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

ENHANCED_PRACTICE_SCRIPT = '<script>\n(function(){\n  // 1. Mode and Q-Count Controller\n  var modeCards = document.querySelectorAll(\'.mode-card\');\n  var qcRadios = document.querySelectorAll(\'input[name=qc_mode]\');\n  var customQcIn = document.getElementById(\'custom_qc\');\n  var presets = document.querySelectorAll(\'.qpreset\');\n\n  function updatePresetButtons(val) {\n    presets.forEach(function(btn){\n      if(btn.dataset.q === String(val)) {\n        btn.classList.add(\'active\');\n      } else {\n        btn.classList.remove(\'active\');\n      }\n    });\n  }\n\n  presets.forEach(function(btn){\n    btn.onclick = function(){\n      var q = btn.dataset.q;\n      if (customQcIn) customQcIn.value = q;\n      var rad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n      if (rad) rad.checked = true;\n      updatePresetButtons(q);\n      if (typeof sug === \'function\') sug();\n    };\n  });\n\n  qcRadios.forEach(function(r){\n    r.onchange = function(){\n      if (r.value === \'all\') {\n        presets.forEach(function(b){ b.classList.remove(\'active\'); });\n      } else {\n        if (customQcIn) updatePresetButtons(customQcIn.value);\n      }\n      if (typeof sug === \'function\') sug();\n    };\n  });\n\n  if (customQcIn) {\n    customQcIn.onfocus = function(){\n      var rad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n      if (rad) rad.checked = true;\n      updatePresetButtons(customQcIn.value);\n      if (typeof sug === \'function\') sug();\n    };\n    customQcIn.oninput = function(){\n      var rad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n      if (rad) rad.checked = true;\n      updatePresetButtons(customQcIn.value);\n      if (typeof sug === \'function\') sug();\n    };\n  }\n\n  // Mode Cards Selection\n  modeCards.forEach(function(card){\n    card.onclick = function(){\n      modeCards.forEach(function(c){ c.classList.remove(\'active\'); });\n      card.classList.add(\'active\');\n      var rad = card.querySelector(\'input[type=radio]\');\n      if (rad) rad.checked = true;\n    };\n  });\n\n  // URL Query Parameters Handling (autostart, mode, filter, q, t)\n  function handleUrlParams() {\n    var params = new URLSearchParams(window.location.search);\n    var mode = params.get(\'mode\');\n    if (mode === \'practice\') {\n      var pCard = document.getElementById(\'mode_card_practice\');\n      if (pCard) pCard.click();\n    } else if (mode === \'cbt\') {\n      var cCard = document.getElementById(\'mode_card_cbt\');\n      if (cCard) cCard.click();\n    }\n\n    var filter = params.get(\'filter\');\n    if (filter === \'wrong\') {\n      var wBox = document.getElementById(\'onlywrong\');\n      if (wBox) { wBox.checked = true; if (typeof sug === \'function\') sug(); }\n    } else if (filter === \'star\') {\n      var sBox = document.getElementById(\'onlystar\');\n      if (sBox) { sBox.checked = true; if (typeof sug === \'function\') sug(); }\n    }\n\n    var qParam = params.get(\'q\');\n    if (qParam) {\n      if (qParam === \'all\') {\n        var aRad = document.querySelector(\'input[name=qc_mode][value=all]\');\n        if (aRad) aRad.checked = true;\n        presets.forEach(function(b){ b.classList.remove(\'active\'); });\n      } else {\n        var num = parseInt(qParam);\n        if (num > 0) {\n          if (customQcIn) customQcIn.value = num;\n          var cRad = document.querySelector(\'input[name=qc_mode][value=custom]\');\n          if (cRad) cRad.checked = true;\n          updatePresetButtons(num);\n        }\n      }\n      if (typeof sug === \'function\') sug();\n    }\n\n    var tParam = params.get(\'t\');\n    if (tParam) {\n      if (tParam === \'free\') {\n        var fRad = document.querySelector(\'input[name=tm][value=free]\');\n        if (fRad) fRad.checked = true;\n      } else {\n        var tnum = parseInt(tParam);\n        if (tnum > 0) {\n          var tRad = document.querySelector(\'input[name=tm][value=timed]\');\n          if (tRad) tRad.checked = true;\n          var mIn = document.getElementById(\'mins\');\n          if (mIn) mIn.value = tnum;\n        }\n      }\n    }\n\n    if (params.get(\'autostart\') === \'1\') {\n      setTimeout(function(){\n        var goBtn = document.getElementById(\'go\');\n        if (goBtn && !goBtn.disabled) goBtn.click();\n      }, 200);\n    }\n  }\n\n  handleUrlParams();\n\n  // 2. Fullscreen & Header Controls Setup\n  var examEl = document.getElementById(\'exam\');\n  if (examEl) {\n    // Inject Progress Bar\n    var pBar = document.createElement(\'div\');\n    pBar.id = \'examProgressBar\';\n    examEl.appendChild(pBar);\n\n    var topEl = examEl.querySelector(\'.top\');\n    if (topEl) {\n      topEl.style.position = \'relative\';\n\n      var badge = document.createElement(\'span\');\n      badge.id = \'examModeBadge\';\n      badge.style.cssText = \'font-size:12px;font-weight:700;padding:3px 8px;border-radius:4px;background:#2563eb;color:#ffffff;margin-left:12px;white-space:nowrap;\';\n      badge.textContent = \'CBT Mode\';\n      topEl.insertBefore(badge, topEl.querySelector(\'.tm\'));\n\n      var fsBtn = document.createElement(\'button\');\n      fsBtn.className = \'btn\';\n      fsBtn.id = \'btnFullscreen\';\n      fsBtn.type = \'button\';\n      fsBtn.title = \'Toggle Fullscreen Mode (Hotkey: F)\';\n      fsBtn.style.cssText = \'margin-left:auto;margin-right:8px;font-size:13px;padding:5px 10px;\';\n      fsBtn.textContent = \'Fullscreen\';\n      fsBtn.onclick = function() {\n        if (!document.fullscreenElement) {\n          document.documentElement.requestFullscreen().catch(function(){});\n          fsBtn.textContent = \'Exit Fullscreen\';\n        } else {\n          if (document.exitFullscreen) document.exitFullscreen();\n          fsBtn.textContent = \'Fullscreen\';\n        }\n      };\n      topEl.insertBefore(fsBtn, topEl.querySelector(\'#submit\'));\n\n      var hkBtn = document.createElement(\'button\');\n      hkBtn.className = \'btn\';\n      hkBtn.id = \'btnHotkeys\';\n      hkBtn.type = \'button\';\n      hkBtn.title = \'Keyboard Shortcuts (Hotkey: ?)\';\n      hkBtn.style.cssText = \'font-size:13px;padding:5px 9px;margin-right:8px;\';\n      hkBtn.textContent = \'⌨\';\n      hkBtn.onclick = function() {\n        var modal = document.getElementById(\'hotkeysModal\');\n        if (modal) modal.style.display = modal.style.display === \'flex\' ? \'none\' : \'flex\';\n      };\n      topEl.insertBefore(hkBtn, topEl.querySelector(\'#submit\'));\n    }\n\n    // Inject Hotkeys Dialog\n    var hkModal = document.createElement(\'div\');\n    hkModal.id = \'hotkeysModal\';\n    hkModal.className = \'cbt-modal-backdrop\';\n    hkModal.style.display = \'none\';\n    hkModal.innerHTML = \'<div class="cbt-modal-box">\' +\n      \'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">\' +\n        \'<h3 style="margin:0;font-size:18px;">Keyboard Shortcuts</h3>\' +\n        \'<button type="button" class="btn" onclick="document.getElementById(\\\'hotkeysModal\\\').style.display=\\\'none\\\'" style="padding:2px 8px;font-size:16px;">&times;</button>\' +\n      \'</div>\' +\n      \'<table class="hotkeys-table">\' +\n        \'<tr><td><span class="kbd-key">1</span> &ndash; <span class="kbd-key">4</span> / <span class="kbd-key">A</span> &ndash; <span class="kbd-key">D</span></td><td>Select option A, B, C, or D</td></tr>\' +\n        \'<tr><td><span class="kbd-key">&rarr;</span> / <span class="kbd-key">N</span> / <span class="kbd-key">Enter</span></td><td>Save &amp; Next question</td></tr>\' +\n        \'<tr><td><span class="kbd-key">&larr;</span> / <span class="kbd-key">P</span></td><td>Previous question</td></tr>\' +\n        \'<tr><td><span class="kbd-key">M</span></td><td>Mark for Review &amp; Next</td></tr>\' +\n        \'<tr><td><span class="kbd-key">C</span> / <span class="kbd-key">Backspace</span></td><td>Clear response</td></tr>\' +\n        \'<tr><td><span class="kbd-key">S</span></td><td>Star question for later</td></tr>\' +\n        \'<tr><td><span class="kbd-key">F</span></td><td>Toggle Fullscreen Exam Mode</td></tr>\' +\n        \'<tr><td><span class="kbd-key">?</span></td><td>Open / Close this shortcuts helper</td></tr>\' +\n      \'</table>\' +\n      \'<button type="button" class="btn" onclick="document.getElementById(\\\'hotkeysModal\\\').style.display=\\\'none\\\'" style="margin-top:16px;width:100%;padding:8px;">Close Shortcuts</button>\' +\n    \'</div>\';\n    document.body.appendChild(hkModal);\n\n    // Inject CBT Submit Modal\n    var submitModal = document.createElement(\'div\');\n    submitModal.id = \'cbtSubmitModal\';\n    submitModal.className = \'cbt-modal-backdrop\';\n    submitModal.style.display = \'none\';\n    submitModal.innerHTML = \'<div class="cbt-modal-box">\' +\n      \'<h3 style="margin:0 0 8px;font-size:19px;">Submit Examination</h3>\' +\n      \'<p style="margin:0 0 12px;font-size:13.5px;color:#64748b;">Review your question status summary before final submission:</p>\' +\n      \'<table class="cbt-summary-table">\' +\n        \'<tr><td>Total Questions</td><td><b id="cbtSumTot">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot green"></span> Answered</td><td><b id="cbtSumAns" style="color:#16a34a">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot red"></span> Not Answered</td><td><b id="cbtSumNotAns" style="color:#ef4444">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot purple"></span> Marked for Review</td><td><b id="cbtSumMark" style="color:#9333ea">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot purple-green"></span> Answered &amp; Marked (Evaluated)</td><td><b id="cbtSumAnsMark" style="color:#9333ea">0</b></td></tr>\' +\n        \'<tr><td><span class="cbt-dot gray"></span> Not Visited</td><td><b id="cbtSumNotVis" style="color:#64748b">0</b></td></tr>\' +\n      \'</table>\' +\n      \'<div style="display:flex;gap:10px;">\' +\n        \'<button type="button" class="btn" id="cbtConfirmSubmit" style="flex:1;background:#2563eb;color:#fff;font-weight:700;padding:10px;">Confirm &amp; Submit</button>\' +\n        \'<button type="button" class="btn" id="cbtCancelSubmit" style="padding:10px 14px;">Return to Exam</button>\' +\n      \'</div>\' +\n    \'</div>\';\n    document.body.appendChild(submitModal);\n\n    document.getElementById(\'cbtCancelSubmit\').onclick = function(){\n      submitModal.style.display = \'none\';\n    };\n    document.getElementById(\'cbtConfirmSubmit\').onclick = function(){\n      submitModal.style.display = \'none\';\n      if (typeof origFinish === \'function\') origFinish();\n    };\n  }\n\n  // Option Elimination (Right click / Alt click)\n  document.addEventListener(\'contextmenu\', function(e){\n    var opt = e.target.closest(\'.o\');\n    if (opt && document.body.classList.contains(\'cbt-mode\')) {\n      e.preventDefault();\n      opt.classList.toggle(\'eliminated\');\n    }\n  });\n\n  // Global Keyboard Navigation\n  document.addEventListener(\'keydown\', function(e){\n    if (!examEl || examEl.hidden) return;\n    if (e.target.tagName === \'INPUT\' || e.target.tagName === \'TEXTAREA\') {\n      if (e.key === \'Enter\') {\n        var nxt = document.getElementById(\'svn\');\n        if (nxt) nxt.click();\n      }\n      return;\n    }\n    var k = e.key.toUpperCase();\n    if (k === \'1\' || k === \'A\') { selectOpt(\'A\'); }\n    else if (k === \'2\' || k === \'B\') { selectOpt(\'B\'); }\n    else if (k === \'3\' || k === \'C\') { selectOpt(\'C\'); }\n    else if (k === \'4\' || k === \'D\') { selectOpt(\'D\'); }\n    else if (k === \'ARROWLEFT\' || k === \'P\') {\n      var prev = document.getElementById(\'prev\');\n      if (prev && !prev.disabled) prev.click();\n    }\n    else if (k === \'ARROWRIGHT\' || k === \'N\' || e.key === \'Enter\') {\n      var svn = document.getElementById(\'svn\');\n      if (svn) svn.click();\n    }\n    else if (k === \'M\') {\n      var mkn = document.getElementById(\'mkn\');\n      if (mkn) mkn.click();\n    }\n    else if (k === \'C\' || k === \'BACKSPACE\' || k === \'DELETE\') {\n      var clr = document.getElementById(\'clr\');\n      if (clr) clr.click();\n    }\n    else if (k === \'S\') {\n      var star = document.getElementById(\'star\');\n      if (star) star.click();\n    }\n    else if (k === \'F\') {\n      var fs = document.getElementById(\'btnFullscreen\');\n      if (fs) fs.click();\n    }\n    else if (e.key === \'?\') {\n      var hk = document.getElementById(\'btnHotkeys\');\n      if (hk) hk.click();\n    }\n  });\n\n  function selectOpt(letter) {\n    if (typeof cur === \'undefined\') return;\n    var qv = document.getElementById(\'qv\' + cur);\n    if (!qv) return;\n    var opt = qv.querySelector(\'.o[data-l="\' + letter + \'"]\');\n    if (opt) opt.click();\n  }\n\n  // 3. Progress Bar Tracking\n  setInterval(function(){\n    if (typeof started === \'undefined\' || !started || typeof submitted === \'undefined\' || submitted) return;\n    var pBar = document.getElementById(\'examProgressBar\');\n    if (!pBar) return;\n    if (typeof LIMIT !== \'undefined\' && LIMIT > 0 && typeof total !== \'undefined\') {\n      var pct = Math.min(100, (total / LIMIT) * 100);\n      pBar.style.width = pct + \'%\';\n      var rem = LIMIT - total;\n      if (rem <= 300) {\n        pBar.style.backgroundColor = \'#ef4444\';\n      } else if (rem <= 900) {\n        pBar.style.backgroundColor = \'#f59e0b\';\n      } else {\n        pBar.style.backgroundColor = \'#2563eb\';\n      }\n    } else if (typeof NS !== \'undefined\' && NS.length > 0 && typeof cur !== \'undefined\') {\n      var idx = NS.indexOf(cur);\n      pBar.style.width = (((idx + 1) / NS.length) * 100) + \'%\';\n      pBar.style.backgroundColor = \'#2563eb\';\n    }\n  }, 1000);\n\n  // 4. Override enter() to handle CBT mode class & badge\n  var origEnter = window.enter;\n  window.enter = function() {\n    var modeRad = document.querySelector(\'input[name=test_mode]:checked\');\n    window.isCBT = !modeRad || modeRad.value === \'cbt\';\n    document.body.classList.toggle(\'cbt-mode\', window.isCBT);\n\n    var badge = document.getElementById(\'examModeBadge\');\n    if (badge) {\n      badge.textContent = window.isCBT ? \'CBT Exam Mode\' : \'Practice Mode\';\n      badge.style.background = window.isCBT ? \'#2563eb\' : \'#059669\';\n    }\n\n    if (typeof origEnter === \'function\') origEnter();\n  };\n\n  // 5. Override Submit Click for CBT Modal\n  var subBtn = document.getElementById(\'submit\');\n  if (subBtn) {\n    subBtn.onclick = function() {\n      if (!window.isCBT) {\n        var an = 0, mk = 0;\n        NS.forEach(function(n){ if (S[n]) an++; if (M[n]) mk++; });\n        if (confirm(\'Answered: \' + an + \'\\nNot answered: \' + (NS.length - an) + \'\\nMarked for review: \' + mk + \'\\n\\nSubmit?\')) {\n          if (typeof origFinish === \'function\') origFinish();\n        }\n        return;\n      }\n\n      var counts = { nv: 0, na: 0, an: 0, mk: 0, am: 0 };\n      NS.forEach(function(n){ counts[stat(n)]++; });\n\n      document.getElementById(\'cbtSumTot\').textContent = NS.length;\n      document.getElementById(\'cbtSumAns\').textContent = counts.an;\n      document.getElementById(\'cbtSumNotAns\').textContent = counts.na;\n      document.getElementById(\'cbtSumMark\').textContent = counts.mk;\n      document.getElementById(\'cbtSumAnsMark\').textContent = counts.am;\n      document.getElementById(\'cbtSumNotVis\').textContent = counts.nv;\n\n      var sm = document.getElementById(\'cbtSubmitModal\');\n      if (sm) sm.style.display = \'flex\';\n    };\n  }\n\n  // 6. Override finish() to compute NTA Marking Scheme (+4 / -1)\n  window.origFinish = window.finish;\n  window.finish = function() {\n    if (submitted) return;\n    submitted = true;\n\n    // Grade exam\n    var correctCount = 0;\n    var wrongCount = 0;\n    var unattemptedCount = 0;\n\n    NS.forEach(function(n){\n      var ans = S[n];\n      if (ans) {\n        var isOk = (typeof same === \'function\') ? same(n, ans) : false;\n        if (isOk) {\n          correctCount++;\n          C[n] = \'r\';\n          delete WR[n];\n        } else {\n          wrongCount++;\n          C[n] = \'w\';\n          WR[n] = 1;\n        }\n      } else {\n        unattemptedCount++;\n      }\n    });\n\n    if (typeof sv === \'function\' && typeof KW !== \'undefined\') sv(KW, WR);\n\n    var totalMarks = (correctCount * 4) - (wrongCount * 1);\n    var maxMarks = NS.length * 4;\n    var acc = (correctCount + wrongCount > 0) ? Math.round((correctCount / (correctCount + wrongCount)) * 100) : 0;\n\n    var A = {\n      t: Date.now(),\n      label: label,\n      NS: NS,\n      S: S,\n      M: M,\n      V: V,\n      T: T,\n      C: C,\n      X: X,\n      cur: cur,\n      total: total,\n      LIMIT: LIMIT,\n      isCBT: !!window.isCBT,\n      score: totalMarks,\n      maxScore: maxMarks,\n      correct: correctCount,\n      wrong: wrongCount,\n      unattempted: unattemptedCount,\n      accuracy: acc\n    };\n\n    HIST.unshift(A);\n    HIST = HIST.slice(0, 25);\n    if (typeof sv === \'function\' && typeof KH !== \'undefined\') sv(KH, HIST);\n    try { localStorage.removeItem(KS); } catch(e) {}\n\n    renderEnhancedSummary(A);\n  };\n\n  // Override summary() to also use modern scorecard for historical view\n  window.origSummary = window.summary;\n  window.summary = function(A, old) {\n    if (A) A.isEarlier = !!old;\n    renderEnhancedSummary(A);\n  };\n\n  // 7. Render Enhanced Summary & Question Review with Options and Solutions\n  window.renderEnhancedSummary = function(A) {\n    var examDiv = document.getElementById(\'exam\');\n    var startDiv = document.getElementById(\'start\');\n    var doneDiv = document.getElementById(\'done\');\n    if (examDiv) examDiv.hidden = true;\n    if (startDiv) startDiv.hidden = true;\n    if (!doneDiv) return;\n    doneDiv.hidden = false;\n\n    var ns = A.NS || [];\n    var corr = A.correct || 0;\n    var wrong = A.wrong || 0;\n    var unatt = A.unattempted || 0;\n    var totalQ = ns.length;\n    var score = typeof A.score === \'number\' ? A.score : ((corr * 4) - wrong);\n    var maxScore = A.maxScore || (totalQ * 4);\n    var acc = A.accuracy || (corr + wrong > 0 ? Math.round((corr / (corr + wrong)) * 100) : 0);\n\n    // SVG Donut calculation\n    var R = 44;\n    var C_circ = 2 * Math.PI * R;\n    var fCorr = totalQ > 0 ? (corr / totalQ) : 0;\n    var fWrong = totalQ > 0 ? (wrong / totalQ) : 0;\n    var fUnatt = totalQ > 0 ? (unatt / totalQ) : 0;\n\n    var lCorr = fCorr * C_circ;\n    var lWrong = fWrong * C_circ;\n    var lUnatt = fUnatt * C_circ;\n\n    var oCorr = 0;\n    var oWrong = -lCorr;\n    var oUnatt = -(lCorr + lWrong);\n\n    var tt = 0;\n    ns.forEach(function(n){ tt += (A.T && A.T[n]) || 0; });\n    var avgSec = totalQ > 0 ? Math.round(tt / totalQ) : 0;\n\n    var chName = (typeof META !== \'undefined\' && META.chapter) ? META.chapter : \'Chapter PYQ Examination\';\n    var isNeg = score < 0;\n\n    var tagTitle = A.isEarlier ? \'Past Attempt Review\' : (A.isCBT ? \'NTA CBT Simulation Scorecard\' : \'Practice Set Completed\');\n\n    var h = \'<div class="cbt-scorecard">\' +\n      \'<div class="cbt-score-hero">\' +\n        \'<div class="cbt-score-left">\' +\n          \'<span class="cbt-score-tag">\' + tagTitle + \'</span>\' +\n          \'<h2 class="cbt-score-title">\' + chName + \'</h2>\' +\n          \'<p class="cbt-score-meta">\' + (A.label || \'\') + \' &middot; \' + new Date(A.t).toLocaleString() + \'</p>\' +\n          \'<div style="display:flex;align-items:baseline;gap:8px;margin-top:14px;">\' +\n            \'<div class="cbt-big-score\' + (isNeg ? \' neg\' : \'\') + \'">\' + (score > 0 ? \'+\' : \'\') + score + \' <small>/ \' + maxScore + \'</small></div>\' +\n            \'<span style="font-size:13px;font-weight:700;padding:3px 9px;border-radius:4px;background:#e0f2fe;color:#0369a1;">\' + acc + \'% Accuracy</span>\' +\n          \'</div>\' +\n        \'</div>\' +\n        \'<div class="cbt-donut-wrap">\' +\n          \'<svg class="cbt-donut-svg" viewBox="0 0 100 100">\' +\n            \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#222224" stroke-width="12"/>\' +\n            (lCorr > 0 ? \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#16a34a" stroke-width="12" stroke-dasharray="\' + lCorr + \' \' + C_circ + \'" stroke-dashoffset="\' + oCorr + \'"/>\' : \'\') +\n            (lWrong > 0 ? \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#ef4444" stroke-width="12" stroke-dasharray="\' + lWrong + \' \' + C_circ + \'" stroke-dashoffset="\' + oWrong + \'"/>\' : \'\') +\n            (lUnatt > 0 ? \'<circle cx="50" cy="50" r="\' + R + \'" fill="none" stroke="#94a3b8" stroke-width="12" stroke-dasharray="\' + lUnatt + \' \' + C_circ + \'" stroke-dashoffset="\' + oUnatt + \'"/>\' : \'\') +\n          \'</svg>\' +\n          \'<div class="cbt-donut-legend">\' +\n            \'<div class="cbt-donut-legend-item"><span class="cbt-donut-dot" style="background:#16a34a"></span> Correct: \' + corr + \'</div>\' +\n            \'<div class="cbt-donut-legend-item"><span class="cbt-donut-dot" style="background:#ef4444"></span> Incorrect: \' + wrong + \'</div>\' +\n            \'<div class="cbt-donut-legend-item"><span class="cbt-donut-dot" style="background:#94a3b8"></span> Unattempted: \' + unatt + \'</div>\' +\n          \'</div>\' +\n        \'</div>\' +\n      \'</div>\' +\n\n      \'<div class="cbt-metrics-grid">\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Total Questions</span><span class="cbt-metric-num">\' + totalQ + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Correct (+4)</span><span class="cbt-metric-num" style="color:#16a34a">+\' + (corr * 4) + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Negative (-1)</span><span class="cbt-metric-num" style="color:#ef4444">-\' + wrong + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Net Marks</span><span class="cbt-metric-num" style="color:\' + (score >= 0 ? \'#16a34a\' : \'#ef4444\') + \'">\' + score + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Time Taken</span><span class="cbt-metric-num">\' + (typeof fmt === \'function\' ? fmt(tt) : tt + \'s\') + \'</span></div>\' +\n        \'<div class="cbt-metric-item"><span class="cbt-metric-lbl">Avg / Question</span><span class="cbt-metric-num">\' + avgSec + \'s</span></div>\' +\n      \'</div>\' +\n\n      \'<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;">\' +\n        \'<button type="button" class="btn" onclick="location.reload()" style="padding:9px 16px;background:#2563eb;color:#fff;font-weight:700;">Retake Chapter Practice</button>\' +\n        \'<a href="index.html" class="btn" style="padding:9px 16px;text-decoration:none;display:inline-flex;align-items:center;">&lsaquo; Subject Chapters</a>\' +\n        \'<a href="../index.html" class="btn" style="padding:9px 16px;text-decoration:none;display:inline-flex;align-items:center;">Home Portal</a>\' +\n      \'</div>\' +\n\n      \'<h3 style="margin:24px 0 12px;font-size:18px;">Detailed Solutions &amp; Question Review</h3>\' +\n      \'<div class="review-filter-pills" id="reviewFilterPills">\' +\n        \'<button type="button" class="rf-pill active" data-f="all">All Questions (\' + totalQ + \')</button>\' +\n        \'<button type="button" class="rf-pill" data-f="inc">Incorrect Only (\' + wrong + \')</button>\' +\n        \'<button type="button" class="rf-pill" data-f="corr">Correct Only (\' + corr + \')</button>\' +\n        \'<button type="button" class="rf-pill" data-f="unatt">Unattempted (\' + unatt + \')</button>\' +\n      \'</div>\' +\n      \'<div id="reviewQuestionsList"></div>\' +\n    \'</div>\';\n\n    doneDiv.innerHTML = h;\n\n    // Render Question Review Cards\n    var qListEl = document.getElementById(\'reviewQuestionsList\');\n    var cardsHtml = \'\';\n\n    ns.forEach(function(n, idx){\n      var qv = document.getElementById(\'qv\' + n);\n      if (!qv) return;\n\n      var userAns = (A.S && A.S[n]) || \'\';\n      var correctAns = (typeof META !== \'undefined\' && META.ans) ? String(META.ans[n]) : \'\';\n      var isOk = userAns && ((typeof same === \'function\') ? same(n, userAns) : (userAns === correctAns));\n      var isUnatt = !userAns;\n\n      var tag = isOk ? \'corr\' : (isUnatt ? \'unatt\' : \'inc\');\n      var pillText = isOk ? \'+4 Correct\' : (isUnatt ? \'0 Unattempted\' : \'-1 Incorrect\');\n\n      var stemEl = qv.querySelector(\'.stem\');\n      var stemHtml = stemEl ? stemEl.innerHTML : \'\';\n      var srcEl = qv.querySelector(\'.src\');\n      var srcText = srcEl ? srcEl.textContent : \'\';\n\n      // Find Type Name from META\n      var typeName = \'\';\n      var typeId = qv.dataset.type;\n      if (typeof META !== \'undefined\' && META.types) {\n        META.types.forEach(function(t){\n          if (String(t.id) === String(typeId)) typeName = t.name;\n        });\n      }\n\n      // Format Options for Review\n      var optsHtml = \'\';\n      var optsEl = qv.querySelector(\'.opts\');\n      if (optsEl) {\n        optsHtml = \'<div class="review-opts" style="display:flex;flex-direction:column;gap:6px;margin:10px 0;">\';\n        var oDivs = optsEl.querySelectorAll(\'.o\');\n        oDivs.forEach(function(o){\n          var letCode = o.dataset.l || \'\';\n          var isThisCorrect = (letCode.toUpperCase() === correctAns.toUpperCase());\n          var isThisUser = (letCode.toUpperCase() === String(userAns).toUpperCase());\n          var border = \'1px solid #cbd5e1\';\n          var bg = \'#f8fafc\';\n          var badge = \'\';\n\n          if (isThisCorrect) {\n            border = \'2px solid #16a34a\';\n            bg = \'#dcfce7\';\n            badge = \'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#15803d;background:#bbf7d0;padding:1px 6px;border-radius:3px;">Correct Key</span>\';\n          }\n          if (isThisUser && !isThisCorrect) {\n            border = \'2px solid #ef4444\';\n            bg = \'#fee2e2\';\n            badge = \'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#b91c1c;background:#fecaca;padding:1px 6px;border-radius:3px;">Your Choice</span>\';\n          } else if (isThisUser && isThisCorrect) {\n            badge = \'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#15803d;background:#bbf7d0;padding:1px 6px;border-radius:3px;">Your Choice (Correct)</span>\';\n          }\n\n          var oc = o.querySelector(\'.oc\');\n          var ocHtml = oc ? oc.innerHTML : \'\';\n\n          optsHtml += \'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:6px;border:\' + border + \';background:\' + bg + \';">\' +\n            \'<span style="font-weight:800;font-size:13px;width:20px;">\' + letCode + \'</span>\' +\n            \'<div style="flex:1;font-size:13.5px;">\' + ocHtml + \'</div>\' +\n            badge +\n          \'</div>\';\n        });\n        optsHtml += \'</div>\';\n      }\n\n      cardsHtml += \'<div class="review-card" data-tag="\' + tag + \'">\' +\n        \'<div class="review-header">\' +\n          \'<div style="font-weight:700;font-size:14.5px;">Q.\' + (idx + 1) + \' <span style="color:#64748b;font-size:12.5px;font-weight:400;margin-left:6px;">\' + srcText + \'</span></div>\' +\n          \'<span class="review-pill \' + tag + \'">\' + pillText + \'</span>\' +\n        \'</div>\' +\n        (typeName ? \'<div style="font-size:12px;color:#2563eb;font-weight:600;margin-bottom:8px;">Type: \' + typeName + \'</div>\' : \'\') +\n        \'<div class="stem-content" style="margin-bottom:12px;">\' + stemHtml + \'</div>\' +\n        optsHtml +\n        \'<div class="review-answers-box" style="margin-top:12px;padding:10px 12px;background:#f1f5f9;border-radius:6px;font-size:13.5px;">\' +\n          \'<div><b>Your Response:</b> \' + (userAns ? \'<span style="color:\' + (isOk ? \'#16a34a\' : \'#ef4444\') + \';font-weight:700">\' + userAns + \'</span>\' : \'<span style="color:#64748b;font-style:italic">Not Attempted</span>\') + \'</div>\' +\n          \'<div style="margin-top:4px;"><b>Official Key / Correct Answer:</b> <span style="color:#16a34a;font-weight:700">\' + correctAns + \'</span></div>\' +\n        \'</div>\' +\n      \'</div>\';\n    });\n\n    if (qListEl) qListEl.innerHTML = cardsHtml;\n\n    // Filter pills click handling\n    var rfPills = document.querySelectorAll(\'.rf-pill\');\n    rfPills.forEach(function(pill){\n      pill.onclick = function(){\n        rfPills.forEach(function(p){ p.classList.remove(\'active\'); });\n        pill.classList.add(\'active\');\n        var f = pill.dataset.f;\n        var rCards = document.querySelectorAll(\'.review-card\');\n        rCards.forEach(function(card){\n          if (f === \'all\' || card.dataset.tag === f) {\n            card.style.display = \'block\';\n          } else {\n            card.style.display = \'none\';\n          }\n        });\n      };\n    });\n\n    window.scrollTo({ top: 0, behavior: \'smooth\' });\n  };\n})();\n</script>'

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
    if 'cbtSubmitModal' not in content:
        pattern_script = r'<script>\s*\(function\(\)\{\s*function initQCount\(\)\{.*?</script>'
        if re.search(pattern_script, content, re.DOTALL):
            content = re.sub(pattern_script, lambda m: ENHANCED_PRACTICE_SCRIPT, content, flags=re.DOTALL)
            modified = True
        elif '</body>' in content:
            pos_b = content.rfind('</body>')
            content = content[:pos_b] + ENHANCED_PRACTICE_SCRIPT + '\n</body>' + content[pos_b+7:]
            modified = True
            
    return content, modified


# 5. DYNAMIC HOME PORTAL & RANDOM TEST POOL SYNC
# -------------------------------------------------------------
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
            content, dark_mod = patch_dark_mode(content)
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
