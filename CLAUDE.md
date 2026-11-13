# 小説 推敲・拡張スタジオ

長編小説を「毎回同じ基準で、1話ずつ順に」推敲・拡張するための作業場。
汎用部（`core/`）と作品固有部（`works/<slug>/`）に分かれている。

## 現在の作品
- active: `works/youen-no-fujigimi`（『陽炎の藤君』）

## 作業を始める前に必ず読む（この順）
1. `core/WORKFLOW.md` — ベースプロンプト（手順・相談ゲート・禁止事項）
2. `core/standards/` — drama / style / consistency / web-format
3. active 作品の `WORK.md`
4. active 作品の `bible/` 全ファイルと `PROGRESS.md`

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

## 禁止
- `works/*/source/` の編集（原文は不変）
- 相談ゲートの事項を承認前に本文へ書くこと
- push はユーザーの指示があるときのみ
