#!/usr/bin/env python3
"""改稿本文の機械チェック。人間（とモデル）の監査の前に必ず通す。

使い方:
  python3 core/scripts/lint.py works/<slug>/drafts/ep001.md [--work works/<slug>] [--source]

  --work   作品の lint.json を既定設定（core/lint-default.json）に上書きマージする
  --source 原文ファイル（## 原文 以降のみ）を対象にする。診断用で、合否は出さない

設定キー（lint.json）:
  length: [最小, 最大]               空白・記号を除いた本文字数
  katakana_allow: [...]               許可するカタカナ語（部分一致）
  limited_words: {語: 1話あたり上限}
  narration_patterns: {正規表現: 上限} 総括ナレーションなどの癖
  info_words: [...]                    数だけ報告する語（口癖・語尾）
  repeat_ngram: {n: 長さ, min: 回数}   反復フレーズの検出
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **v}
        elif isinstance(v, list) and isinstance(out.get(k), list):
            out[k] = list(dict.fromkeys(out[k] + v))
        else:
            out[k] = v
    return out


def body_of(text: str, source: bool) -> str:
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    if source and "## 原文" in text:
        text = text.split("## 原文", 1)[1]
    # 見出し・ルビ記法・区切り記号を除く
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    text = re.sub(r"[｜|]([^《\n]+)《[^》\n]+》", r"\1", text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--work")
    ap.add_argument("--source", action="store_true")
    a = ap.parse_args()

    cfg = json.loads((ROOT / "core/lint-default.json").read_text(encoding="utf-8"))
    if a.work:
        wl = Path(a.work) / "lint.json"
        if wl.exists():
            cfg = merge(cfg, json.loads(wl.read_text(encoding="utf-8")))

    failed = False
    for f in a.files:
        body = body_of(Path(f).read_text(encoding="utf-8"), a.source)
        flat = re.sub(r"\s", "", body)
        errs, warns, infos = [], [], []

        n = len(re.sub(r"[◇◆＊*―\-]", "", flat))
        lo, hi = cfg["length"]
        (errs if not (lo <= n <= hi) else infos).append(f"本文字数 {n}（基準 {lo}〜{hi}）")

        kata = Counter(re.findall(r"[ァ-ヴー]{2,}", body))
        allow = cfg.get("katakana_allow", [])
        bad = Counter({k: v for k, v in kata.items() if not any(w in k for w in allow)})
        onoma = re.compile(r"[ァィゥェォッ]|(.)\1|ー.*ー|[リン]$")  # 擬音・擬態語らしさ
        words = Counter({k: v for k, v in bad.items() if not onoma.search(k)})
        sfx = Counter({k: v for k, v in bad.items() if onoma.search(k)})
        if words:
            errs.append("許可外のカタカナ語: " + "、".join(f"{k}×{v}" for k, v in words.most_common()))
        mx_sfx = cfg.get("katakana_sfx_max", 2)
        if sum(sfx.values()) > mx_sfx:
            warns.append(f"カタカナ擬音 {sum(sfx.values())}回（目安 {mx_sfx}以下）: " + "、".join(sfx))
        elif sfx:
            infos.append("カタカナ擬音: " + "、".join(sfx))

        for w, mx in cfg.get("limited_words", {}).items():
            c = flat.count(w)
            if c > mx:
                errs.append(f"「{w}」{c}回（上限 {mx}）")

        for pat, mx in cfg.get("narration_patterns", {}).items():
            c = len(re.findall(pat, body, flags=re.M))
            if c > mx:
                warns.append(f"/{pat}/ {c}回（目安 {mx}以下）")

        for w in cfg.get("info_words", []):
            c = flat.count(w)
            if c:
                infos.append(f"「{w}」{c}回")

        rn = cfg.get("repeat_ngram", {"n": 7, "min": 4})
        sents = re.sub(r"「[^」]*」", "", flat)  # 台詞は除外して地の文の癖を見る
        grams = Counter(sents[i:i + rn["n"]] for i in range(len(sents) - rn["n"]))
        rep = [(g, c) for g, c in grams.most_common(40) if c >= rn["min"] and not re.search(r"[、。]", g[1:-1])]
        if rep:
            warns.append("反復フレーズ: " + "、".join(f"「{g}」×{c}" for g, c in rep[:10]))

        dialogue = re.findall(r"「[^」]*」", body)
        ratio = sum(len(d) for d in dialogue) / max(1, len(flat))
        infos.append(f"台詞比率 {ratio:.0%}")

        print(f"## {f}")
        for tag, lst in (("ERROR", errs), ("WARN", warns), ("INFO", infos)):
            for x in lst:
                print(f"- [{tag}] {x}")
        print()
        if errs and not a.source:
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
