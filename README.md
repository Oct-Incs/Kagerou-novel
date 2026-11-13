# novel-revision-studio

長編小説の推敲・拡張を、同じ基準で1話ずつ順に進めるための枠組み。Claude Code での運用を前提とする。

```
core/                    汎用部（どの作品にも使う）
  WORKFLOW.md            ベースプロンプト：フェーズ0（全体設計）と1話パイプライン、相談ゲート
  standards/             劇作・文体・人物整合性・Web書式の基準
  templates/             設計書・監査・相談・台帳・作品指示のひな形
  scripts/
    split_log.py         対話ログ（User prompt / Response 形式）を話ごとに分割
    lint.py              字数・禁止語・反復・総括ナレーション等の機械チェック
    new_work.py          新しい作品フォルダを作る
  lint-default.json      lint の既定値
works/<slug>/            作品固有部
  WORK.md                作品固有の指示（core より優先）
  lint.json              作品固有の lint 設定
  bible/                 canon（人物台帳）/ style / drama / master-plan / ledger（伏線・負債）/ consultations（相談記録）
  source/                原文（不変）。raw/ に元ログ
  notes/                 原ログ内の考証・分析ターン
  plans/ drafts/ reviews/  設計書・改稿本文・監査
  PROGRESS.md            進捗表
```

## 新しい作品を始める
1. `python3 core/scripts/new_work.py <slug>`
2. 原稿を `works/<slug>/source/raw/` に置き、`split_log.py` で分割（ログ形式でない場合は手で `source/epNNN.md` を作る）
3. `WORK.md` と `bible/` を埋め、`CLAUDE.md` の active を切り替える
4. フェーズ0から始める
