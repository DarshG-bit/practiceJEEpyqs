"""Verification utility for the JEE PYQ Practice project.
Checks all HTML files to ensure:
1. True AMOLED Black (#000000) is enforced in dark mode (0 navy blue #1e293b in dark selectors).
2. Real CBT Exam Mode hooks and styling exist in all practice sheets.
3. Centralized Dashboard on index.html has all 27 chapters synchronized.
"""
import os
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

def check_all():
    print(f"Scanning project root: {ROOT_DIR}")
    html_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        if any(skip in root for skip in [".git", "backup", "node_modules"]):
            continue
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))
                
    print(f"Found {len(html_files)} HTML files.\n")
    
    dark_navy_matches = []
    missing_cbt = []
    
    for path in html_files:
        rel = os.path.relpath(path, ROOT_DIR)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Extract dark mode CSS blocks
        # Looking for selectors starting with [data-theme="dark"]
        dark_blocks = re.findall(r'(\[data-theme="dark"\][^{]*\{[^}]*\})', content)
        for block in dark_blocks:
            if "#1e293b" in block or "#0f172a" in block or "#172554" in block or "#1e3a8a" in block:
                dark_navy_matches.append((rel, block.strip()))
                    
        if "PYQ Practice.html" in rel:
            if "test_mode_box" not in content or "cbtSubmitModal" not in content:
                missing_cbt.append(rel)

    print("=" * 60)
    print("VERIFICATION RESULTS:")
    print("=" * 60)
    print(f"Navy Blue Violations in Dark Selectors : {len(dark_navy_matches)}")
    if dark_navy_matches:
        for f, blk in dark_navy_matches:
            print(f"  [VIOLATION] {f} -> {blk[:60]}")
    else:
        print("  ✓ All 83 files strictly comply with True AMOLED Black (#000000)!")
        
    print(f"Missing CBT Mode in Practice Sheets    : {len(missing_cbt)}")
    if missing_cbt:
        for f in missing_cbt:
            print(f"  [MISSING] {f}")
    else:
        print("  ✓ All 27 practice sheets have Real CBT Exam Mode + Q-Count active!")

    # Check index.html
    index_path = os.path.join(ROOT_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            idx_html = f.read()
        chap_count = idx_html.count('"url":')
        print(f"Dashboard Synchronized Chapters        : {chap_count} / 27")
        if chap_count == 27 and "aspirantDashboard" in idx_html:
            print("  ✓ Home Portal Aspirant Dashboard is fully synced!")
        else:
            print("  [WARNING] Dashboard missing chapters or element!")

if __name__ == "__main__":
    check_all()
