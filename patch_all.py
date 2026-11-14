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

DARK_MODE_CSS = """
/* =================== COMPREHENSIVE DARK MODE =================== */
[data-theme="dark"] {
  --ink: #f8fafc;
  --mut: #94a3b8;
  --line: #334155;
  --bg: #0f172a;
  --accl: #1e3a8a;
  --accb: #3b82f6;
  --hdr: #091e3a;
  --hdrtx: #f8fafc;
  --tmbg: rgba(255, 255, 255, 0.1);
  --hdrline: #334155;
}

[data-theme="dark"] body {
  background: #0f172a !important;
  color: #f8fafc !important;
}

[data-theme="dark"] a {
  color: #93c5fd !important;
}

/* 1. START PANEL & GENERAL PANELS */
[data-theme="dark"] .panel,
[data-theme="dark"] .main,
[data-theme="dark"] #done,
[data-theme="dark"] .sec,
[data-theme="dark"] .card {
  background: #1e293b !important;
  border-color: #334155 !important;
  color: #f8fafc !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
}

[data-theme="dark"] .panel h2,
[data-theme="dark"] h1, [data-theme="dark"] h2, [data-theme="dark"] h3 {
  color: #60a5fa !important;
}

[data-theme="dark"] .banner {
  background: #0f172a !important;
  border-color: #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .banner b {
  color: #f8fafc !important;
}
[data-theme="dark"] .banner a {
  color: #60a5fa !important;
  text-decoration: underline !important;
}

[data-theme="dark"] .tbox {
  background: #0f172a !important;
  border-color: #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .panel label,
[data-theme="dark"] label.rad {
  color: #f8fafc !important;
}
[data-theme="dark"] #typelist .cnt {
  color: #94a3b8 !important;
}
[data-theme="dark"] #typelist .all span,
[data-theme="dark"] .all span {
  color: #60a5fa !important;
  text-decoration: underline !important;
}
[data-theme="dark"] #typelist hr {
  border-color: #334155 !important;
}
[data-theme="dark"] .tin input,
[data-theme="dark"] .panel input[type=number],
[data-theme="dark"] .num,
[data-theme="dark"] input[type=text],
[data-theme="dark"] textarea {
  background: #0f172a !important;
  border-color: #475569 !important;
  color: #f8fafc !important;
}

/* 2. TOP HEADER BAR */
[data-theme="dark"] .top {
  background: #091e3a !important;
  border-bottom: 1px solid #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .top h1 {
  color: #f8fafc !important;
}
[data-theme="dark"] .top .tm {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #f8fafc !important;
}

/* 3. QUESTION HEADER & BLUE SUBHEADER BAR */
[data-theme="dark"] .qhead {
  background: #0f172a !important;
  border-color: #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .qhead b,
[data-theme="dark"] #qno {
  color: #f8fafc !important;
}
[data-theme="dark"] .qhead small,
[data-theme="dark"] .qt {
  color: #94a3b8 !important;
}
[data-theme="dark"] #qtime {
  color: #f8fafc !important;
  font-weight: 700 !important;
}
[data-theme="dark"] .starbtn {
  background: #0f172a !important;
  border-color: #475569 !important;
  color: #cbd5e1 !important;
}
[data-theme="dark"] .starbtn.on {
  background: #451a03 !important;
  border-color: #d97706 !important;
  color: #fbbf24 !important;
}

/* #typeln (The blue bar on text - readable light blue text) */
[data-theme="dark"] #typeln {
  background: #1e3a8a !important;
  color: #93c5fd !important;
  border: 1px solid #3b82f6 !important;
  font-weight: 600 !important;
}

[data-theme="dark"] .src {
  color: #94a3b8 !important;
}
[data-theme="dark"] .stem {
  color: #f8fafc !important;
}
[data-theme="dark"] .stem p {
  color: #f8fafc !important;
}

/* 4. MATH EQUATIONS - PURE WHITE */
[data-theme="dark"] math,
[data-theme="dark"] math * {
  color: #f8fafc !important;
  fill: #f8fafc !important;
}

/* 5. DIAGRAMS / IMAGES - PRESERVED IN WHITE CARD CONTAINER */
[data-theme="dark"] img,
[data-theme="dark"] .fig {
  background: #ffffff !important;
  border-radius: 8px !important;
  padding: 6px !important;
  border: 1px solid #475569 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
  display: inline-block !important;
}

/* 6. OPTIONS */
[data-theme="dark"] .o {
  background: #1e293b !important;
  border: 1.5px solid #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .o:hover {
  background: #26334d !important;
  border-color: #475569 !important;
}
[data-theme="dark"] .o .ol {
  background: #0f172a !important;
  color: #94a3b8 !important;
  border: 1px solid #475569 !important;
}
[data-theme="dark"] .o.sel {
  background: #1e3a8a !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.sel .ol {
  background: #3b82f6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.ok {
  background: #064e3b !important;
  border-color: #10b981 !important;
  color: #ecfdf5 !important;
}
[data-theme="dark"] .o.ok .ol {
  background: #10b981 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.bad {
  background: #7f1d1d !important;
  border-color: #ef4444 !important;
  color: #fef2f2 !important;
}
[data-theme="dark"] .o.bad .ol {
  background: #ef4444 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .o.dead {
  opacity: 0.35 !important;
}

/* Feedback & numerical checking */
[data-theme="dark"] .num.ok { background: #064e3b !important; border-color: #10b981 !important; color: #ecfdf5 !important; }
[data-theme="dark"] .num.bad { background: #7f1d1d !important; border-color: #ef4444 !important; color: #fef2f2 !important; }
[data-theme="dark"] .chkres.r { background: #064e3b !important; color: #a7f3d0 !important; border-color: #059669 !important; }
[data-theme="dark"] .chkres.w { background: #7f1d1d !important; color: #fecaca !important; border-color: #dc2626 !important; }
[data-theme="dark"] .chkres.h { background: #1e293b !important; color: #cbd5e1 !important; border-color: #475569 !important; }

/* 7. BOTTOM NAVIGATION BAR */
[data-theme="dark"] .foot {
  background: #0f172a !important;
  border-top: 1px solid #334155 !important;
  box-shadow: 0 -3px 12px rgba(0, 0, 0, 0.45) !important;
}
[data-theme="dark"] .foot .btn {
  background: #1e293b !important;
  color: #f8fafc !important;
  border-color: #475569 !important;
}
[data-theme="dark"] .foot .btn:hover {
  background: #334155 !important;
}
[data-theme="dark"] .foot .btn:disabled {
  opacity: 0.35 !important;
  background: #1e293b !important;
  color: #64748b !important;
  border-color: #334155 !important;
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
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #f8fafc !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
}
[data-theme="dark"] .side::-webkit-scrollbar {
  width: 8px !important;
}
[data-theme="dark"] .side::-webkit-scrollbar-track {
  background: #1e293b !important;
}
[data-theme="dark"] .side::-webkit-scrollbar-thumb {
  background: #475569 !important;
  border-radius: 4px !important;
}
[data-theme="dark"] .side h3 {
  color: #94a3b8 !important;
}
[data-theme="dark"] .side .tname {
  color: #60a5fa !important;
}
[data-theme="dark"] .pbtn {
  background: #334155 !important;
  border-color: #475569 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .pbtn:hover {
  background: #475569 !important;
}
[data-theme="dark"] .pbtn.cur {
  outline: 2px solid #38bdf8 !important;
  outline-offset: 1px !important;
}
[data-theme="dark"] .pbtn.ans {
  background: #16a34a !important;
  border-color: #22c55e !important;
  color: #ffffff !important;
}
[data-theme="dark"] .pbtn.rev {
  background: #7c3aed !important;
  border-color: #8b5cf6 !important;
  color: #ffffff !important;
}
[data-theme="dark"] .pbtn.r_ans {
  background: #7c3aed !important;
  border-color: #22c55e !important;
  color: #ffffff !important;
}

/* 9. TABLES & HISTORY */
[data-theme="dark"] table {
  background: #0f172a !important;
  color: #f8fafc !important;
  border-color: #334155 !important;
}
[data-theme="dark"] th {
  background: #1e293b !important;
  color: #93c5fd !important;
  border-color: #334155 !important;
}
[data-theme="dark"] td {
  border-color: #334155 !important;
}
[data-theme="dark"] .actr {
  background: #0f172a !important;
}

/* 10. SUMMARY / REVIEW SCREEN */
[data-theme="dark"] .tag.E { background: #064e3b !important; color: #a7f3d0 !important; }
[data-theme="dark"] .tag.M { background: #451a03 !important; color: #fde68a !important; }
[data-theme="dark"] .tag.D { background: #7f1d1d !important; color: #fecaca !important; }
[data-theme="dark"] .qcard {
  background: #1e293b !important;
  border-color: #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .flt select {
  background: #0f172a !important;
  color: #f8fafc !important;
  border-color: #475569 !important;
}

/* 11. CHAPTER INDEX & SUBJECT INDEX PAGES */
[data-theme="dark"] header {
  background: #0b1329 !important;
  border-bottom: 1px solid #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] header h1 {
  color: #60a5fa !important;
}
[data-theme="dark"] header p {
  color: #94a3b8 !important;
}
[data-theme="dark"] header a {
  color: #93c5fd !important;
}

[data-theme="dark"] #q {
  background: #1e293b !important;
  border: 1.5px solid #475569 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] #q::placeholder {
  color: #94a3b8 !important;
}

[data-theme="dark"] .lg {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #cbd5e1 !important;
}
[data-theme="dark"] .lg b {
  color: #f8fafc !important;
}
[data-theme="dark"] .lg ul, [data-theme="dark"] .lg li {
  color: #cbd5e1 !important;
}

[data-theme="dark"] .strip,
[data-theme="dark"] .strip.cA,
[data-theme="dark"] .strip.cB,
[data-theme="dark"] .strip.cC,
[data-theme="dark"] .strip.cD {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #f8fafc !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
}
[data-theme="dark"] .strip.cA { border-left: 6px solid #22c55e !important; }
[data-theme="dark"] .strip.cB { border-left: 6px solid #84cc16 !important; }
[data-theme="dark"] .strip.cC { border-left: 6px solid #f97316 !important; }
[data-theme="dark"] .strip.cD { border-left: 6px solid #64748b !important; }

[data-theme="dark"] .strip .no {
  color: #94a3b8 !important;
}
[data-theme="dark"] .strip .mid b {
  color: #60a5fa !important;
}
[data-theme="dark"] .strip .mid span {
  color: #94a3b8 !important;
}
[data-theme="dark"] .strip .gl {
  color: #cbd5e1 !important;
}
[data-theme="dark"] .strip .gl b {
  color: #f8fafc !important;
}

[data-theme="dark"] .tg em {
  background: #0f172a !important;
  border-color: #475569 !important;
  color: #cbd5e1 !important;
}
[data-theme="dark"] .tg em.pH {
  background: #14532d !important;
  color: #86efac !important;
  border-color: #16a34a !important;
}
[data-theme="dark"] .tg em.pM {
  background: #713f12 !important;
  color: #fde047 !important;
  border-color: #ca8a04 !important;
}
[data-theme="dark"] .tg em.pL {
  background: #334155 !important;
  color: #cbd5e1 !important;
  border-color: #475569 !important;
}

[data-theme="dark"] .lk a {
  background: #0f172a !important;
  border: 1px solid #475569 !important;
  color: #93c5fd !important;
}
[data-theme="dark"] .lk a:hover {
  background: #1e3a8a !important;
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
  background: #1e3a8a !important;
  border: 2px solid #3b82f6 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .gf {
  background: #1e293b !important;
  border: 2px solid #3b82f6 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .gf .gft {
  color: #60a5fa !important;
}
[data-theme="dark"] .gf .gfn {
  color: #94a3b8 !important;
}
[data-theme="dark"] .tc {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .tc .th span {
  color: #f8fafc !important;
}
[data-theme="dark"] .tc .tcnt {
  color: #94a3b8 !important;
}
[data-theme="dark"] .tc.zero .th span {
  color: #64748b !important;
}
[data-theme="dark"] .grp .gl {
  color: #94a3b8 !important;
}
[data-theme="dark"] #typelist .pill input+span {
  background: #0f172a !important;
  border: 2px solid #475569 !important;
  color: #cbd5e1 !important;
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
  color: #94a3b8 !important;
}


/* 13. TYPE NOTES PAGES (.page, .how, .ed, .gt, details, #sym) */
[data-theme="dark"] .page {
  background: #1e293b !important;
  border-color: #334155 !important;
  color: #f8fafc !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
}

[data-theme="dark"] .how {
  background: #0f172a !important;
  border: 1px solid #334155 !important;
  color: #cbd5e1 !important;
}
[data-theme="dark"] .how h3 {
  color: #60a5fa !important;
}
[data-theme="dark"] .how p,
[data-theme="dark"] .how ol,
[data-theme="dark"] .how li {
  color: #cbd5e1 !important;
}

[data-theme="dark"] .ed {
  background: #0f172a !important;
  border: 1px solid #475569 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .ed:focus {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 2px #1e3a8a !important;
}

[data-theme="dark"] .gt {
  border-color: #334155 !important;
}
[data-theme="dark"] .gt td {
  border-color: #334155 !important;
  color: #f8fafc !important;
  background: #0f172a !important;
}
[data-theme="dark"] .gt tr:first-child td {
  background: #1e293b !important;
  color: #93c5fd !important;
}
[data-theme="dark"] .gt td:first-child {
  background: #1e293b !important;
  color: #f8fafc !important;
}

[data-theme="dark"] .rev {
  background: #064e3b !important;
  border-color: #10b981 !important;
  color: #ecfdf5 !important;
}
[data-theme="dark"] .rev h4 {
  color: #6ee7b7 !important;
}

[data-theme="dark"] .top {
  background: #091e3a !important;
  border-bottom: 1px solid #334155 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .top h1 {
  color: #f8fafc !important;
}
[data-theme="dark"] .top a {
  color: #93c5fd !important;
}

[data-theme="dark"] .btn {
  background: #1e293b !important;
  border-color: #475569 !important;
  color: #f8fafc !important;
}
[data-theme="dark"] .btn:hover {
  background: #334155 !important;
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
  color: #94a3b8 !important;
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
  background: #091e3a !important;
  border-top: 1px solid #334155 !important;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.4) !important;
}
[data-theme="dark"] #sym > span {
  color: #93c5fd !important;
  font-weight: 700 !important;
}
[data-theme="dark"] #sym button {
  background: #1e293b !important;
  color: #f8fafc !important;
  border: 1px solid #475569 !important;
}
[data-theme="dark"] #sym button:hover {
  background: #334155 !important;
  border-color: #60a5fa !important;
  color: #60a5fa !important;
}
[data-theme="dark"] #sym button.w {
  background: #1e3a8a !important;
  color: #93c5fd !important;
  border-color: #3b82f6 !important;
}


/* 14. SUBJECT SWITCHER POPUP & SIDEBAR (#sw, #swb, .sj) */
[data-theme="dark"] #sw {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.45) !important;
}
[data-theme="dark"] #sw h2 {
  color: #60a5fa !important;
  font-weight: 700 !important;
}
[data-theme="dark"] #sw .x {
  color: #cbd5e1 !important;
}
[data-theme="dark"] #sw a.sj {
  background: #0f172a !important;
  border-color: #334155 !important;
  color: #f8fafc !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
}
[data-theme="dark"] #sw a.sj b {
  color: #60a5fa !important;
}
[data-theme="dark"] #sw a.sj span {
  color: #cbd5e1 !important;
}
[data-theme="dark"] #sw a.sj:hover {
  background: #1e3a8a !important;
  border-color: #3b82f6 !important;
}
[data-theme="dark"] #sw a.all {
  color: #93c5fd !important;
}
[data-theme="dark"] #sw a.all:hover {
  color: #bfdbfe !important;
}
[data-theme="dark"] #swb {
  background: #1e293b !important;
  border: 1px solid #475569 !important;
  color: #f8fafc !important;
}

/* 15. HIGH-CONTRAST TEXT ENHANCEMENTS */
[data-theme="dark"] header p,
[data-theme="dark"] .top p {
  color: #e2e8f0 !important;
  opacity: 1 !important;
}
[data-theme="dark"] .note {
  color: #cbd5e1 !important;
}
[data-theme="dark"] #q::placeholder {
  color: #cbd5e1 !important;
}
[data-theme="dark"] .lg {
  color: #e2e8f0 !important;
}
[data-theme="dark"] .lg ul,
[data-theme="dark"] .lg li {
  color: #cbd5e1 !important;
}
[data-theme="dark"] .strip .mid span,
[data-theme="dark"] .strip .gl {
  color: #cbd5e1 !important;
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
  background: #1e293b;
  border: 1px solid #475569;
  color: #f8fafc;
}
[data-theme="dark"] .theme-btn:hover {
  background: #334155;
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
        
    # 2. Dark mode CSS (Replace existing dark mode block or inject)
    if "COMPREHENSIVE DARK MODE" in content:
        # Check if the new filter rules are present
        if "14. SUBJECT SWITCHER" not in content:
            # Replace old DARK MODE CSS with the comprehensive updated one
            pattern = r'/\* =+ COMPREHENSIVE DARK MODE =+ \*/.*?\[data-theme="dark"\] \.theme-btn:hover\s*\{[^}]+\}'
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, DARK_MODE_CSS.strip(), content, flags=re.DOTALL)
                modified = True
            else:
                # If pattern didn't match cleanly, inject before </style>
                content = content.replace("</style>", DARK_MODE_CSS + "\n</style>", 1)
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
# MAIN PATCHER RUNNER
# -------------------------------------------------------------

# -------------------------------------------------------------
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
            
            # 1. Option Fixes for PYQ practice files
            if "PYQ Practice.html" in file:
                content, opt_mod = fix_option_images_in_file(content)
                if opt_mod:
                    file_changed = True
                    print(f"  [Options Fixed]   {os.path.relpath(file_path, ROOT_DIR)}")
                    
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
                
    print("=" * 60)
    update_index_portal()
    print(f"Patching complete! Scanned: {total_scanned} files | Updated: {total_modified} files")
    print("Pristine copies are safely archived in the 'backup/' directory.")
    print("=" * 60)

if __name__ == "__main__":
    run_all_patches()
