# Claude Code 設定

## ファイル同期環境 (Windows)

| 用途 | パス |
|------|------|
| Claude Code 作業（メイン） | `%USERPROFILE%\Documents\Obsidian\Work\` |
| 社内共有 | `%USERPROFILE%\Box\shared\` |

## 同期フロー

```
Obsidian vault (ローカル) \ shared \
  ↕ sync_box_obsidian.ps1 (30分ごと自動 / 手動可)
Box Drive \ shared \
  ↕ Box Drive (自動)
社内メンバー
```

## 前提アプリ

| アプリ | 入手先 |
|--------|--------|
| Box Drive | https://www.box.com/ja-jp/resources/downloads |
| Obsidian | https://obsidian.md |

## よく使うコマンド (PowerShell)

```powershell
# 今すぐ同期
powershell -File sync_box_obsidian.ps1 -Direction both

# Box → Obsidian のみ
powershell -File sync_box_obsidian.ps1 -Direction box-to-obs

# Obsidian → Box のみ
powershell -File sync_box_obsidian.ps1 -Direction obs-to-box

# 同期ログを確認
Get-Content "$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log" -Tail 50
```

## 参照ノート (context/)

Obsidian から Claude Code に渡したいノートを `context\` にコピーして使う。

```
claude/ (このリポジトリ)
  context\
    *.md  ← Obsidianからコピーしたノート・思考整理・背景情報
```

- **Claude Codeへの指示**: タスクの背景や判断基準を `context\` のmdに書いておくと参照される
- **更新方法**: Obsidianで編集 → 必要なタイミングで手動コピー
- **gitには含める**: 履歴として残したい場合はコミット、一時的なメモは`.gitignore`に追加

## 初回セットアップ

PowerShell を開いて実行:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned  # 初回のみ
.\setup_env.ps1
```
