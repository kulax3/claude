# Google Tasks CSV エクスポート - Chrome拡張機能

## セットアップ手順

### 1. Google Cloud Console の設定

1. [Google Cloud Console](https://console.cloud.google.com/) を開く
2. 新しいプロジェクトを作成（または既存を選択）
3. **APIとサービス > ライブラリ** から「Tasks API」を有効化
4. **APIとサービス > 認証情報** で「認証情報を作成」
5. **OAuth 2.0 クライアントID** を選択
6. アプリケーションの種類: **Chrome アプリ**
7. 拡張機能の ID を入力（後述）
8. 作成されたクライアントID をコピー

### 2. manifest.json の編集

`manifest.json` の `client_id` を取得したクライアントIDに変更:

```json
"oauth2": {
  "client_id": "取得したクライアントID.apps.googleusercontent.com",
  ...
}
```

### 3. アイコンの準備

`icons/` ディレクトリに以下のPNGファイルを配置:
- `icon16.png` (16×16px)
- `icon48.png` (48×48px)
- `icon128.png` (128×128px)

`icon.svg` を任意のツールでPNGに変換してください。

### 4. Chrome に拡張機能を読み込む

1. Chrome で `chrome://extensions/` を開く
2. 右上の「デベロッパーモード」をオン
3. 「パッケージ化されていない拡張機能を読み込む」をクリック
4. `chrome_extension/` フォルダを選択
5. 拡張機能のIDが表示される → Google Cloud Console の設定に使用

## 使い方

1. Chrome ツールバーの拡張機能アイコンをクリック
2. オプションを選択（完了済み含める / メモ含める）
3. 「CSV をダウンロード」ボタンをクリック
4. Google アカウントの認証を許可
5. CSV ファイルが自動でダウンロードされます

## CSV の列

| 列名 | 内容 |
|------|------|
| タスクリスト | タスクが属するリスト名 |
| タスク名 | タスクのタイトル |
| ステータス | 完了 / 未完了 |
| 期限 | タスクの期限日 |
| 完了日時 | タスクを完了した日時 |
| メモ | タスクのメモ（オプション） |
| 更新日時 | 最終更新日時 |
| 親タスクID | サブタスクの場合、親タスクのID |
| タスクID | Google Tasks 内部ID |

出力ファイルは UTF-8 BOM付き CSV のため、Excel でそのまま開いても文字化けしません。
