# Claude Code 設定

## ファイル同期環境 (Windows)

| 用途 | パス |
|------|------|
| 社内共有 | `%USERPROFILE%\Box\shared\` |
| Claude Code 作業 | `%USERPROFILE%\Apple\iCloud Drive\Obsidian\Work\` |
| iPhone同期 | iCloud経由で自動（Obsidian Mobile アプリ） |

## 同期フロー

```
iPhone
  ↕ iCloud (自動)
Obsidian Vault (Work\)  ←  iCloud for Windows
  ↕ sync_box_obsidian.ps1 (30分ごと自動 / 手動可)
Box Drive (shared\)
  ↕ Box Drive (自動)
社内メンバー
```

## 前提アプリ

| アプリ | 入手先 |
|--------|--------|
| Box Drive | https://www.box.com/ja-jp/resources/downloads |
| iCloud for Windows | Microsoft Store で「iCloud」を検索 |
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

## 初回セットアップ

PowerShell を開いて実行:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned  # 初回のみ
.\setup_env.ps1
```
