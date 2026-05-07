"""
Pokemon Sleep Advisor - Ollama版 (APIキー不要・完全無料)

事前準備:
  1. Ollama をインストール: https://ollama.com
  2. モデルをダウンロード:
       ollama pull llama3.2          # テキスト用 (2GB)
       ollama pull llava             # 画像解析用 (4.7GB)
     ※ llama3.2-vision を使えば1つで両方対応 (8GB)
  3. Ollama を起動: ollama serve

使い方:
  cd pokemon_sleep
  pip install flask requests
  python app.py
"""

import base64
import json
import os
import re

import requests
from flask import Flask, jsonify, render_template, request

import pokemon_data as PD

app = Flask(__name__)
app.secret_key = os.urandom(24)

OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# デフォルトモデル（/api/settingsで変更可能）
DEFAULT_TEXT_MODEL = os.environ.get("OLLAMA_TEXT_MODEL", "llama3.2")
DEFAULT_VISION_MODEL = os.environ.get("OLLAMA_VISION_MODEL", "llava")

# ---------------------------------------------------------------------------
# OLLAMA CLIENT
# ---------------------------------------------------------------------------

def ollama_chat(messages: list, model: str, system: str = None, timeout: int = 120) -> str:
    """Send a chat request to Ollama and return the response text."""
    if system:
        messages = [{"role": "system", "content": system}] + messages

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.7},
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]
    except requests.ConnectionError:
        raise RuntimeError("Ollamaに接続できません。`ollama serve` を実行してください。")
    except requests.Timeout:
        raise RuntimeError("タイムアウトしました。モデルが大きすぎるか、PCの性能が不足している可能性があります。")
    except Exception as e:
        raise RuntimeError(f"Ollamaエラー: {e}")


def ollama_vision(image_b64: str, prompt: str, model: str, timeout: int = 180) -> str:
    """Send an image + prompt to a vision-capable Ollama model."""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]
    except requests.ConnectionError:
        raise RuntimeError("Ollamaに接続できません。`ollama serve` を実行してください。")
    except Exception as e:
        raise RuntimeError(f"画像解析エラー: {e}")


def get_available_models() -> list:
    """Return list of locally installed Ollama models."""
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []


def extract_json_from_text(text: str) -> dict | None:
    """Try to extract a JSON object from a text that may contain markdown."""
    # Remove markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip()
    text = text.replace("```", "").strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


# ---------------------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------------------

SYSTEM_ADVISOR = """あなたはポケモンスリープの専門アドバイザーです。日本語で回答してください。
以下の知識を持っています：
- 各ポケモンのきのみタイプ・食材・スキルの特性
- 調査フィールドに合ったきのみの重要性
- チーム編成の最適化（元気管理、お手伝い速度、スキル発動率）
- せいかくによるステータス補正
- サブスキルの重要度とイベント対応
- 育成の優先度

回答は具体的で実践的にしてください。"""

SYSTEM_SCREENSHOT = """あなたはポケモンスリープのスクリーンショット解析AIです。
画像からポケモン情報を抽出し、必ず以下のJSON形式だけを返してください（説明文は不要）:
{
  "pokemon": [
    {
      "name": "ポケモン名（英語推奨）",
      "level": レベル数値,
      "specialty": "berry/ingredient/skill のいずれか",
      "nature": "せいかく英語キー（例: timid）",
      "main_skill": "スキル名",
      "berry": "きのみ名",
      "subskills": ["サブスキル1", "サブスキル2"],
      "note": "その他情報"
    }
  ],
  "analysis_text": "解析の要約"
}
読み取れない項目はnullにしてください。"""


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/game-data")
def game_data():
    return jsonify({
        "areas": PD.RESEARCH_AREAS,
        "skills": PD.MAIN_SKILLS,
        "natures": PD.NATURES,
        "sub_skills": PD.SUB_SKILLS,
        "pokemon_list": PD.COMMON_POKEMON,
    })


@app.route("/api/ollama-status")
def ollama_status():
    """Check Ollama connection and list available models."""
    models = get_available_models()
    is_running = True
    try:
        requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
    except Exception:
        is_running = False
        models = []

    return jsonify({
        "running": is_running,
        "models": models,
        "text_model": DEFAULT_TEXT_MODEL,
        "vision_model": DEFAULT_VISION_MODEL,
        "ollama_host": OLLAMA_BASE,
    })


@app.route("/api/analyze-screenshot", methods=["POST"])
def analyze_screenshot():
    if "image" not in request.files:
        return jsonify({"error": "画像ファイルが見つかりません"}), 400

    vision_model = request.form.get("model", DEFAULT_VISION_MODEL)
    image_file = request.files["image"]
    image_b64 = base64.standard_b64encode(image_file.read()).decode("utf-8")

    prompt = (
        "このポケモンスリープのスクリーンショットを解析して、"
        "ポケモンの情報をJSON形式で返してください。"
        "JSONのみを返し、説明文は不要です。\n\n"
        + SYSTEM_SCREENSHOT
    )

    try:
        result_text = ollama_vision(image_b64, prompt, model=vision_model)
        data = extract_json_from_text(result_text)
        if data:
            return jsonify(data)
        return jsonify({
            "pokemon": [],
            "analysis_text": result_text,
            "error": "JSONの解析に失敗しました。手動で入力してください。",
        })
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"エラー: {e}"}), 500


@app.route("/api/recommend-team", methods=["POST"])
def recommend_team():
    data = request.json
    pokemon_box = data.get("pokemon_box", [])
    area_text = data.get("area_text", data.get("area", "不明"))
    goal = data.get("goal", "balanced")
    style = data.get("style", "snoozing")
    event = data.get("event", "")
    model = data.get("model", DEFAULT_TEXT_MODEL)

    if not pokemon_box:
        return jsonify({"error": "ボックスが空です"}), 400

    box_summary = _format_box_for_prompt(pokemon_box)
    goal_labels = {
        "strength": "ゆめのかけら最大化",
        "ingredients": "食材収集最大化",
        "cooking": "料理効率最大化",
        "weekly_event": "週間イベント対応",
        "balanced": "バランス重視",
    }
    style_labels = {
        "dozing": "うとうと（8時間未満）",
        "snoozing": "すやすや（8〜9時間）",
        "slumbering": "ぐっすり（9時間以上）",
    }

    prompt = f"""以下のポケモンボックスから最適なチーム編成を3パターン提案してください。

設定:
- 調査フィールド: {area_text}
- 目標: {goal_labels.get(goal, goal)}
- 睡眠スタイル: {style_labels.get(style, style)}
{f'- 現在のイベント: {event}' if event else ''}

マイボックス:
{box_summary}

以下のJSON形式で返してください（説明文不要、JSONのみ）:
{{
  "recommendations": [
    {{
      "title": "チームコンセプト名",
      "team": [
        {{"name": "ポケモン名", "role": "役割"}},
        {{"name": "ポケモン名", "role": "役割"}},
        {{"name": "ポケモン名", "role": "役割"}},
        {{"name": "ポケモン名", "role": "役割"}},
        {{"name": "ポケモン名", "role": "役割"}}
      ],
      "strategy": "戦略の説明（150文字程度）",
      "cons": "注意点"
    }}
  ],
  "general_advice": "育成優先度など全体アドバイス（200文字程度）"
}}"""

    try:
        result_text = ollama_chat(
            [{"role": "user", "content": prompt}],
            model=model,
            system=SYSTEM_ADVISOR,
            timeout=180,
        )
        parsed = extract_json_from_text(result_text)
        if parsed:
            return jsonify(parsed)
        # Fallback: return raw text as general_advice
        return jsonify({"recommendations": [], "general_advice": result_text})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    history = data.get("history", [])
    pokemon_box = data.get("pokemon_box", [])
    model = data.get("model", DEFAULT_TEXT_MODEL)

    if not history:
        return jsonify({"error": "メッセージがありません"}), 400

    system = SYSTEM_ADVISOR
    if pokemon_box:
        system += f"\n\n## ユーザーのマイボックス\n{_format_box_for_prompt(pokemon_box)}"

    messages = [{"role": m["role"], "content": m["content"]} for m in history[-20:]]

    try:
        response_text = ollama_chat(messages, model=model, system=system, timeout=120)
        return jsonify({"response": response_text})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _format_box_for_prompt(pokemon_box: list) -> str:
    lines = []
    for i, p in enumerate(pokemon_box, 1):
        specialty_map = {"berry": "きのみ", "ingredient": "食材", "skill": "スキル"}
        specialty = specialty_map.get(p.get("specialty", ""), p.get("specialty", "不明"))
        skill_key = p.get("main_skill", "")
        skill_name = PD.MAIN_SKILLS.get(skill_key, {}).get("name", skill_key) if skill_key else "不明"
        nature_key = p.get("nature", "")
        nature_name = PD.NATURES.get(nature_key, {}).get("name", nature_key) if nature_key else "不明"
        subskills = "、".join(p.get("subskills", [])) or "なし"
        line = (
            f"{i}. {p.get('name','不明')} Lv.{p.get('level','?')} "
            f"[{specialty}] せいかく:{nature_name} スキル:{skill_name} "
            f"きのみ:{p.get('berry','不明')} サブ:{subskills}"
        )
        if p.get("note"):
            line += f" メモ:{p['note']}"
        lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    models = get_available_models()
    print("🌙 ポケモンスリープ アドバイザー (Ollama版) 起動中...")
    if models:
        print(f"  利用可能なモデル: {', '.join(models)}")
    else:
        print("  ⚠️  Ollamaが見つかりません。以下を確認してください:")
        print("     1. ollama をインストール: https://ollama.com")
        print("     2. ollama serve を実行")
        print("     3. ollama pull llama3.2  (テキスト用)")
        print("     4. ollama pull llava      (画像解析用)")
    print("  http://localhost:5000 でアクセスできます")
    app.run(debug=True, host="0.0.0.0", port=5000)
