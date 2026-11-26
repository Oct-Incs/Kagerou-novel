# 小説 推敲・拡張スタジオ

長編小説を「毎回同じ基準で、1話ずつ順に」推敲・拡張するための作業場。
汎用部（`core/`）と作品固有部（`works/<slug>/`）に分かれている。

## 現在の作品
- active: `works/youen-no-fujigimi`（『陽炎の藤君』）

## 作業を始める前に必ず読む（この順）
1. `core/WORKFLOW.md` — ベースプロンプト（手順・相談ゲート・禁止事項）
2. `core/standards/` — drama / style / consistency / web-format
3. active 作品の `WORK.md`
4. active 作品の `bible/` 全ファイルと `PROGRESS.md`（**`bible/period.md`＝時代考証は、設計書・本文・Notion 見直しのたびに必ず照らす**）

## 優先順位
ユーザーの当該セッションでの指示 ＞ `works/<slug>/WORK.md` ＞ `works/<slug>/bible/*` ＞ `core/standards/*` ＞ `core/WORKFLOW.md` の既定値

## よく使う指示
| ユーザーの言い方 | すること |
|---|---|
| 「フェーズ0を進めて」 | WORKFLOW §1 フェーズ0 の未完了の手順を進める |
| 「第N話」「次」 | WORKFLOW の1話パイプライン（「次」は PROGRESS.md の最初の未完了話） |
| 「設計書だけ」 | Step2 で止める |
| 「相談の回答：C-00X は案A」 | consultations.md に記録し、影響する台帳・設計書を更新する |

## コマンド
```bash
python3 core/scripts/lint.py works/youen-no-fujigimi/drafts/ep001.md --work works/youen-no-fujigimi
python3 core/scripts/lint.py --source --work works/youen-no-fujigimi works/youen-no-fujigimi/source/ep*.md
python3 core/scripts/new_work.py <slug>
```

## 時代考証（2026-11-26 ユーザー指示）
- 時代に合わない物・語・現象（江戸期の船型、後世の産物、海流・季節風の向きの誤りなど）を書かない
- `lint.py` は作品の `lint.json` の `anachronisms` を1回でも ERROR、`period_watch` を WARN にする。根拠と代替は `bible/period.md`
- 新しい誤りを見つけたら、`bible/period.md` と `lint.json` の両方に足す。既存の話にも同じ誤りがないか grep して直す

## 禁止
- `works/*/source/` の編集（原文は不変）
- 相談ゲートの事項を承認前に本文へ書くこと
- push は作業の区切りごとに行ってよい（2026-11-13 ユーザー承認）。コミットの作成者は環境の既定（Claude）のままにする
