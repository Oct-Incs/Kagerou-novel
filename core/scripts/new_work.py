#!/usr/bin/env python3
"""新しい作品フォルダを作る。  python3 core/scripts/new_work.py <slug>"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
slug = sys.argv[1]
w = ROOT / "works" / slug
if w.exists():
    sys.exit(f"{w} は既にあります")
for d in ("bible", "source/raw", "notes", "plans", "drafts", "reviews"):
    (w / d).mkdir(parents=True)
t = ROOT / "core" / "templates"
shutil.copy(t / "WORK.md", w / "WORK.md")
for name in ("canon.md", "ledger.md", "master-plan.md"):
    shutil.copy(t / name, w / "bible" / name)
(w / "bible" / "style.md").write_text("# 文体（作品固有）\n\n## 口調の定義\n\n## 語彙\n", encoding="utf-8")
(w / "bible" / "drama.md").write_text("# 劇作（作品固有）\n", encoding="utf-8")
(w / "bible" / "consultations.md").write_text("# 相談記録\n\n書式は core/templates/consult.md\n", encoding="utf-8")
(w / "lint.json").write_text('{\n  "katakana_allow": [],\n  "limited_words": {}\n}\n', encoding="utf-8")
print(f"作成しました: {w}\n次: 原稿を {w}/source/raw/ に置き、split_log.py で分割。CLAUDE.md の active を切り替える。")
