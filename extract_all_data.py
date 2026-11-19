import os
import json
import re

ROOT_DIR = r"C:\My Stuff\Darsh\Darsh School\JEE\PYQ Practice HTML Site\practiceJEEpyqs-main"
DATA_DIR = os.path.join(ROOT_DIR, "data")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")

os.makedirs(CHAPTERS_DIR, exist_ok=True)

CHAPTER_SOURCES = []
for subj in ["Maths", "Physics", "Chemistry"]:
    subj_path = os.path.join(ROOT_DIR, subj)
    if os.path.exists(subj_path):
        for fname in sorted(os.listdir(subj_path)):
            if fname.endswith("PYQ Practice.html"):
                ch_name = fname.replace(" PYQ Practice.html", "")
                CHAPTER_SOURCES.append({
                    "name": ch_name,
                    "subject": subj,
                    "rel": f"{subj}/{fname}",
                    "cls": "Class B"
                })


def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

catalog = []
total_all_questions = 0

for item in CHAPTER_SOURCES:
    fpath = os.path.join(ROOT_DIR, item["rel"])
    if not os.path.exists(fpath):
        print(f"Warning: File not found: {fpath}")
        continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
        
    meta_match = re.search(r'var META=({.*?});\s*var TY=', html, re.DOTALL)
    if not meta_match:
        meta_match = re.search(r'var META=({.*?});', html, re.DOTALL)
        
    if not meta_match:
        print(f"Failed to find META in {item['name']}")
        continue
        
    meta = json.loads(meta_match.group(1))
    
    types_map = {}
    for t in meta.get("types", []):
        types_map[int(t["id"])] = t["name"]
        
    tags = meta.get("tags", {})
    answers = meta.get("ans", {})
    formats = meta.get("fmt", {})
    expected_times = meta.get("exp", {"E": 150, "M": 210, "D": 270})
    
    qv_pattern = re.compile(
        r'<div class="qv" id="qv(\d+)" data-n="(\d+)" data-kind="([^"]+)" data-type="(\d+)"[^>]*>(.*?)</div>\s*(?=<div class="qv"|<div id="done"|<div class="side"|<script)',
        re.DOTALL
    )
    
    matches = qv_pattern.findall(html)
    questions = []
    
    diff_counts = {"E": 0, "M": 0, "D": 0}
    fmt_counts = {"MCQ": 0, "Numerical": 0}
    slug = slugify(item["name"])
    
    for n_str, dn_str, kind, type_id_str, inner in matches:
        n = int(n_str)
        t_id = int(type_id_str)
        t_name = types_map.get(t_id, f"Type {t_id}")
        
        # Source
        src_m = re.search(r'<div class="src">(.*?)</div>', inner, re.DOTALL)
        source = src_m.group(1).strip() if src_m else ""
        
        # Stem
        stem_m = re.search(r'<div class="stem">(.*?)</div>\s*(?=<div class="opts"|<div class="resp"|<div class="chk")', inner, re.DOTALL)
        stem_html = stem_m.group(1).strip() if stem_m else ""
        
        # Difficulty
        diff = tags.get(str(n), "M")
        diff_counts[diff] = diff_counts.get(diff, 0) + 1
        
        # Format
        fmt_letter = formats.get(str(n), "Q" if kind == "single" else "N")
        if fmt_letter == "Q" or kind == "single":
            fmt_counts["MCQ"] += 1
        else:
            fmt_counts["Numerical"] += 1
            
        # Options
        options = []
        if kind == "single":
            opt_pattern = re.compile(r'<div class="o" data-l="([A-D])"[^>]*>.*?<div class="oc">(.*?)</div>\s*</div>', re.DOTALL)
            for l, oc in opt_pattern.findall(inner):
                options.append({
                    "label": l,
                    "html": oc.strip()
                })
                
        # Correct answer
        ans_val = str(answers.get(str(n), "")).strip()
        exp_sec = expected_times.get(diff, 180)
        
        questions.append({
            "id": n,
            "uid": f"{slug}-{n}",
            "chapter_slug": slug,
            "chapter_name": item["name"],
            "subject": item["subject"],
            "type_id": t_id,
            "type_name": t_name,
            "kind": "single" if (kind == "single" or fmt_letter == "Q") else "int",
            "source": source,
            "difficulty": diff,
            "expected_time_sec": exp_sec,
            "stem_html": stem_html,
            "options": options,
            "answer": ans_val
        })
        
    subj_slug = item["subject"].lower()
    out_dir = os.path.join(CHAPTERS_DIR, subj_slug)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{slug}.json")
    
    chapter_data = {
        "name": item["name"],
        "subject": item["subject"],
        "slug": slug,
        "class_tier": item["cls"],
        "total_questions": len(questions),
        "difficulty_counts": diff_counts,
        "format_counts": fmt_counts,
        "types": meta.get("types", []),
        "expected_times": expected_times,
        "questions": questions
    }
    
    with open(out_file, "w", encoding="utf-8") as out_fp:
        json.dump(chapter_data, out_fp, indent=2, ensure_ascii=False)
        
    total_all_questions += len(questions)
    
    catalog.append({
        "name": item["name"],
        "subject": item["subject"],
        "slug": slug,
        "class_tier": item["cls"],
        "total_questions": len(questions),
        "difficulty_counts": diff_counts,
        "format_counts": fmt_counts,
        "types_count": len(meta.get("types", [])),
        "data_path": f"data/chapters/{subj_slug}/{slug}.json",
        "legacy_url": item["rel"]
    })
    
    print(f"✓ [{item['subject']}] {item['name']}: {len(questions)} questions extracted to {subj_slug}/{slug}.json")

catalog_file = os.path.join(DATA_DIR, "catalog.json")
with open(catalog_file, "w", encoding="utf-8") as f:
    json.dump({
        "platform": "JEE Main PYQ Practice Platform",
        "total_chapters": len(catalog),
        "total_questions": total_all_questions,
        "chapters": catalog
    }, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print(f"DATA EXTRACTION COMPLETE!")
print(f"Total Chapters Processed : {len(catalog)} / {len(CHAPTER_SOURCES)}")
print(f"Total Questions Extracted : {total_all_questions}")
print(f"Master Catalog Saved To   : {catalog_file}")
print("=" * 60)
