# Claude Code 設定

## ファイル同期環境

| 用途 | 場所 |
|------|------|
| 社内共有 | `~/Library/CloudStorage/Box-Box/shared/` |
| Claude Code 作業 | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Work/` |
| iPhone同期 | iCloud経由で自動（Obsidian Mobile アプリ） |

## ノートの場所

- 作業ノート・メモ: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Work/`
- 社内共有ドキュメント: `~/Library/CloudStorage/Box-Box/shared/`
- 同期スクリプト: `sync_box_obsidian.sh`

## 同期フロー

```
iPhone
  ↕ iCloud (自動)
Obsidian Vault (Work/)
  ↕ sync_box_obsidian.sh (30分ごと自動 / 手動可)
Box Drive (shared/)
  ↕ Box (自動)
社内メンバー
```

## よく使うコマンド

```bash
# 今すぐ同期
bash sync_box_obsidian.sh both

# Box → Obsidian のみ
bash sync_box_obsidian.sh box-to-obs

# Obsidian → Box のみ
bash sync_box_obsidian.sh obs-to-box

# 同期ログを確認
tail -f ~/Library/Logs/box-obsidian-sync.log
```

## 初回セットアップ

```bash
bash setup_env.sh
```
