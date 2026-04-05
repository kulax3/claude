#!/bin/bash
# ポケモンスリープ アドバイザー 起動スクリプト
# Usage: bash run.sh

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "❌ ANTHROPIC_API_KEY が設定されていません"
  echo "   export ANTHROPIC_API_KEY=your_key_here"
  exit 1
fi

echo "🌙 ポケモンスリープ アドバイザーを起動します..."
cd "$(dirname "$0")"
python app.py
