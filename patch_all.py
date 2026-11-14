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
/* --- Clean Print & Save as PDF Styling --- */
@media print {
  @page { margin: 12mm 15mm; size: A4 portrait; }
  body { background: #fff !important; color: #000 !important; font-size: 11pt !important; line-height: 1.45 !important; }
  .page { border: none !important; box-shadow: none !important; padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
  
  /* HIDE ALL NAVIGATION, BUTTONS, INSTRUCTIONS */
  .top, #back, .btn, button, .noprint, .how, details, #types, #types+ul, #sym,
  .theme-btn, .top-links, a[href="#top"], .tpdf, .rev, .sm, .back, header {
    display: none !important;
  }

  /* HEADINGS */
  h1.t { font-size: 18pt !important; margin: 0 0 12px !important; color: #1f4e8c !important; }
  h2 { font-size: 14pt !important; margin: 16px 0 6px !important; color: #1f4e8c !important; break-after: avoid !important; page-break-after: avoid !important; }
  h3 { font-size: 12pt !important; margin: 12px 0 4px !important; break-after: avoid !important; page-break-after: avoid !important; }
  p { margin: 4px 0 !important; }

  /* EACH TYPE STARTS ON A NEW PAGE */
  section.typ {
    border-top: 2px solid #1f4e8c !important;
    padding-top: 10px !important;
    margin-top: 14px !important;
    break-inside: auto !important;
    page-break-inside: auto !important;
  }
  section.typ ~ section.typ {
    break-before: page !important;
    page-break-before: page !important;
  }

  /* TABLES: ROW-LEVEL BREAKING (NO WASTED SPACE ON PREVIOUS PAGE) */
  .gt, table {
    width: 100% !important;
    border-collapse: collapse !important;
    break-inside: auto !important;
    page-break-inside: auto !important;
    margin: 8px 0 !important;
  }
  .gt tr, tr {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }
  .gt td, td, th {
    border: 1px solid #94a3b8 !important;
    padding: 6px 8px !important;
    font-size: 10.5pt !important;
    color: #000 !important;
    background: #fff !important;
  }
  .gt tr:first-child td {
    background: #f1f5fb !important;
    font-weight: 700 !important;
  }

  /* EDITABLE BOXES / USER WRITTEN NOTES */
  .ed {
    border: 1px solid #94a3b8 !important;
    background: #fff !important;
    color: #000 !important;
    min-height: 48px !important;
    font-size: 10.5pt !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
    white-space: pre-wrap !important;
  }
}
"""

UNBLOCK_PDF_SCRIPT = """
<script>
// Unblock Save as PDF button so it always prints cleanly
(function(){
  function setupPdfBtn() {
    var btn = document.getElementById('pdf') || document.getElementById('savepdf');
    if (btn) {
      btn.onclick = function(e) {
        if (e) e.preventDefault();
        var secs = [].slice.call(document.querySelectorAll('section.typ'));
        secs.forEach(function(s) {
          s.classList.remove('pr-skip');
          s.style.display = 'block';
        });
        document.body.classList.remove('one');
        window.print();
      };
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupPdfBtn);
  } else {
    setupPdfBtn();
  }
})();
</script>
"""

def patch_type_notes(content):
    modified = False
    
    # 1. Clean up existing corrupted or old print styles
    if "@media print" in content:
        # Replace existing print block or inject our perfect print CSS
        pattern = r'@media\s*print\s*\{.*?\}(?:\s*\}\s*)?'
        # Replace the first print media block or append clean version
        if "/* --- Clean Print & Save as PDF Styling --- */" not in content:
            content = re.sub(r'/\* --- Save as PDF Print Styling --- \*/.*?\}', '', content, flags=re.DOTALL)
            content = content.replace("</style>", PERFECT_PRINT_CSS + "\n</style>", 1)
            modified = True
    else:
        content = content.replace("</style>", PERFECT_PRINT_CSS + "\n</style>", 1)
        modified = True
        
    # 2. Add unblock PDF script if missing
    if "setupPdfBtn" not in content and "</body>" in content:
        content = content.replace("</body>", UNBLOCK_PDF_SCRIPT + "\n</body>", 1)
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
        if "FILTER GROUPS & DIFFICULTY PILLS" not in content:
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
        content = content.replace("</body>", THEME_TOGGLE_JS + "\n</body>", 1)
        modified = True
        
    return content, modified

# -------------------------------------------------------------
# MAIN PATCHER RUNNER
# -------------------------------------------------------------
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
    print(f"Patching complete! Scanned: {total_scanned} files | Updated: {total_modified} files")
    print("Pristine copies are safely archived in the 'backup/' directory.")
    print("=" * 60)

if __name__ == "__main__":
    run_all_patches()
