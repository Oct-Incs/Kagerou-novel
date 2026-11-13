#!/usr/bin/env python3
"""対話ログ（"User prompt:" / "Response:" 形式）を話ごとの原文ファイルに分割する。

使い方:
  python3 core/scripts/split_log.py works/<slug>/source/raw/original-log.txt works/<slug> \
      [--overrides works/<slug>/split-overrides.json] [--dry-run]

出力:
  works/<slug>/source/epNNN.md   原作者指示＋原文（段落を復元）
  works/<slug>/notes/turnNNN.md  本文以外のターン（考証・分析・プロット案など）
  works/<slug>/source/INDEX.md   話の一覧
  works/<slug>/PROGRESS.md       進捗表（既存なら上書きしない）

overrides JSON（任意）: {"turns": {"<ターン番号>": {"id": "018-2", "kind": "episode"|"note", "title": "..."}}}
"""
import argparse
import json
import re
import sys
from pathlib import Path

KANJI = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
NOTE_HINT = re.compile(r"詳細プロット|プロンプト案|から第|まで|および|について|における")
EP_RE = re.compile(r"^\s*(?:#+\s*)?(?:\*\*)?第?([〇一二三四五六七八九十百千0-9]+)話[\s（(]*(.*)$")


def kanji_to_int(s: str) -> int:
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch in KANJI:
            cur = KANJI[ch]
        elif ch in "十百千":
            unit = {"十": 10, "百": 100, "千": 1000}[ch]
            total += (cur or 1) * unit
            cur = 0
    return total + cur


def restore_paragraphs(text: str) -> str:
    # Docs書き出しで改行が半角スペースに潰れたものを段落に戻す（非ASCII文字に挟まれた半角スペースのみ）
    text = re.sub(r"(?<=[^\x00-\x7f]) +(?=[^\x00-\x7f])", "\n\n", text)
    text = re.sub(r"\n?_{8,}\s*$", "", text.strip())
    return text.strip() + "\n"


def parse(raw: str):
    raw = raw.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    chunks = re.split(r"\n(?=User prompt: )", raw)
    turns = []
    for c in chunks:
        if not c.startswith("User prompt: "):
            continue
        up, _, rs = c[len("User prompt: "):].partition("\nResponse: ")
        turns.append({"prompt": up.strip(), "response": rs.strip()})
    return turns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("workdir")
    ap.add_argument("--overrides")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    turns = parse(Path(a.log).read_text(encoding="utf-8-sig"))
    ov = json.loads(Path(a.overrides).read_text(encoding="utf-8"))["turns"] if a.overrides else {}
    work = Path(a.workdir)
    rows = []
    for i, t in enumerate(turns, 1):
        first = t["response"].split("\n", 1)[0]
        m = EP_RE.match(first)
        kind = "episode" if (m and not NOTE_HINT.search(first)) else "note"
        epid = f"{kanji_to_int(m.group(1)):03d}" if kind == "episode" else None
        title = first.strip()
        o = ov.get(str(i), {})
        kind = o.get("kind", kind)
        epid = o.get("id", epid)
        title = o.get("title", title)
        rows.append((i, kind, epid, title, t))

    ids = [r[2] for r in rows if r[1] == "episode"]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    print(f"turns={len(rows)} episodes={len(ids)} notes={len(rows) - len(ids)}")
    if dup:
        print("重複した話番号（overridesで解消してください）:", dup)
    for i, kind, epid, title, t in rows:
        print(f"{i:4d} {kind:7s} {epid or '-':6s} {title[:50]}")
    if a.dry_run:
        return
    if dup:
        sys.exit("重複があるため書き出しを中止しました")

    (work / "source").mkdir(parents=True, exist_ok=True)
    (work / "notes").mkdir(parents=True, exist_ok=True)
    index = ["# 原文インデックス", "", "| 話 | 題 | 原文字数 | ログのターン |", "|---|---|---|---|"]
    for i, kind, epid, title, t in rows:
        body = restore_paragraphs(t["response"])
        if kind == "episode":
            n = len(re.sub(r"\s", "", body))
            (work / "source" / f"ep{epid}.md").write_text(
                f"---\nid: \"{epid}\"\ntitle: \"{title}\"\nlog_turn: {i}\nchars: {n}\n---\n\n"
                f"## 原作者指示（当時のプロンプト）\n\n{t['prompt']}\n\n## 原文\n\n{body}",
                encoding="utf-8")
            index.append(f"| {epid} | {title} | {n} | {i} |")
        else:
            (work / "notes" / f"turn{i:03d}.md").write_text(
                f"---\nlog_turn: {i}\nkind: note\n---\n\n## 指示\n\n{t['prompt']}\n\n## 応答\n\n{body}",
                encoding="utf-8")
    (work / "source" / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    prog = work / "PROGRESS.md"
    if not prog.exists():
        lines = ["# 進捗表", "", "状態: `-` 未着手 / `△` 作業中 / `?` 相談待ち / `○` 完了", "",
                 "| 話 | 設計書 | 相談 | 本文 | 監査 | 台帳 | 備考 |", "|---|---|---|---|---|---|---|"]
        lines += [f"| {r[2]} | - | - | - | - | - | |" for r in rows if r[1] == "episode"]
        prog.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("written to", work)


if __name__ == "__main__":
    main()
