# Keep & Tasks Knowledge Base

Google Keep と Google Tasks を **4段階AIパイプライン** で分析し、ローカルSQLiteナレッジベースに変換するCLIツール。

[Siftly](https://github.com/viperrcrypto/Siftly) のアーキテクチャを参考に、Google サービス向けに実装。

---

## アーキテクチャ

```
データソース
├── Google Keep  ── gkeepapi（非公式）または Google Takeout
└── Google Tasks ── 公式 Tasks API (OAuth 2.0)

↓ 4段階AIパイプライン

Stage 1: エンティティ抽出  (APIコストゼロ)
  └─ URL, ハッシュタグ, 日付, 既知ツール名を正規表現で抽出

Stage 2: ビジョン分析 (Keep のみ)
  └─ Claude Vision で画像OCR・説明・ビジュアルタグ生成

Stage 3: 意味論的タグ付け
  └─ Claude で 20〜30 件の検索用タグ + 1文要約 + センチメント

Stage 4: カテゴリ分類
  └─ 1〜3 カテゴリ + 信頼スコア (0〜1)

↓

SQLite + FTS5 (完全ローカル)
  ├── 自然言語検索
  ├── Claude 意味検索 (オプション)
  └── CSV / JSON / ZIP エクスポート
```

---

## セットアップ

### 1. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 2. Claude APIキーを設定

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# または Claude CLI をインストール済みであれば自動検出されます
```

### 3. Google Tasks を使う場合

[Google Cloud Console](https://console.cloud.google.com/apis/credentials) で:

1. **Google Tasks API** を有効化
2. OAuth 2.0 クライアントID を作成（デスクトップアプリ）
3. `credentials.json` を `data/google_credentials.json` に配置

### 4. Google Keep を使う場合

**Takeout モード（推奨・安全）:**
1. [Google Takeout](https://takeout.google.com) から Keep をエクスポート
2. 解凍して `Takeout/Keep/` ディレクトリのパスを控える

**gkeepapi モード（リアルタイム・非公式）:**
1. `pip install gkeepapi` でインストール済み
2. Googleアカウントのマスタートークンを取得 ([gkeepapi ドキュメント](https://gkeepapi.readthedocs.io/))

---

## 使い方

```bash
# DB初期化
python main.py init

# --- データ取得 ---

# Google Tasks を同期
python main.py sync tasks

# Google Keep を同期（Takeoutモード）
python main.py sync keep --mode takeout --takeout-dir ~/Downloads/Takeout/Keep

# Google Keep を同期（gkeepapi モード）
python main.py sync keep --mode gkeepapi --email you@gmail.com --token YOUR_MASTER_TOKEN

# --- AIパイプライン実行 ---
python main.py process

# Vision分析をスキップしてコストを削減
python main.py process --skip-vision

# --- 検索 ---

# キーワード検索（高速・無料）
python main.py search "機械学習の勉強メモ"

# 意味検索（Claude使用）
python main.py search "AIツールの使い方" --semantic

# --- エクスポート ---
python main.py export --format json
python main.py export --format csv
python main.py export --format zip

# --- 統計 ---
python main.py stats
```

---

## ファイル構成

```
keep_tasks_pipeline/
├── main.py              # CLI エントリーポイント
├── config.py            # 設定・定数
├── requirements.txt
├── auth/
│   ├── google_auth.py   # Google OAuth2
│   └── claude_auth.py   # Claude APIキー解決
├── sources/
│   ├── google_tasks.py  # Google Tasks コネクタ（公式API）
│   └── google_keep.py   # Google Keep コネクタ（gkeepapi / Takeout）
├── pipeline/
│   ├── stage1_entity.py    # エンティティ抽出
│   ├── stage2_vision.py    # 画像分析（Claude Vision）
│   ├── stage3_tagging.py   # タグ生成
│   └── stage4_categorize.py # カテゴリ分類
├── storage/
│   └── database.py      # SQLite + FTS5
├── search/
│   └── search.py        # 検索（FTS5 + Claude reranking）
├── export/
│   └── exporter.py      # CSV / JSON / ZIP エクスポート
└── data/                # ローカルデータ（gitignore推奨）
    ├── knowledge_base.db
    ├── google_credentials.json
    └── google_token.json
```

---

## カテゴリ一覧

`config.py` の `DEFAULT_CATEGORIES` で変更可能：

- 仕事・業務
- 学習・勉強
- アイデア・企画
- 買い物・TODO
- 健康・生活
- エンタメ・趣味
- 読書・記事
- 技術・IT
- その他

---

## 注意事項

- **gkeepapi は非公式**です。Googleが内部APIを変更すると動作しなくなる可能性があります。安定性重視なら Takeout モードを推奨。
- AIパイプラインの処理コストは Claude Haiku を使用することで最小化しています（`CLAUDE_MODEL` 環境変数で変更可）。
- すべてのデータはローカルSQLiteに保存。クラウド送信なし（AI APIコール時のテキスト送信を除く）。
