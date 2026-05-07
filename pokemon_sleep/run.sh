#!/bin/bash
# ポケモンスリープ アドバイザー 起動スクリプト (Ollama版)
#
# 事前準備:
#   1. Ollama インストール: https://ollama.com
#   2. ollama pull llama3.2        # テキスト用 (2GB)
#   3. ollama pull llava           # 画像解析用 (4.7GB)
#      ※ llama3.2-vision なら1つで両対応 (8GB)
#   4. ollama serve                # Ollama起動
#
# オプション:
#   OLLAMA_HOST=http://localhost:11434  (デフォルト)
#   OLLAMA_TEXT_MODEL=llama3.2         (デフォルト)
#   OLLAMA_VISION_MODEL=llava          (デフォルト)

cd "$(dirname "$0")"

# 依存パッケージの確認
python3 -c "import flask, requests" 2>/dev/null || {
  echo "📦 パッケージをインストールします..."
  pip install -r requirements.txt
}

echo "🌙 ポケモンスリープ アドバイザーを起動します..."
echo "   http://localhost:5000 でアクセスできます"
echo "   停止: Ctrl+C"
echo ""
python3 app.py
