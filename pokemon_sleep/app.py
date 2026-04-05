"""
Pokemon Sleep Advisor - Flask app with Claude API integration.

Usage:
  cd pokemon_sleep
  ANTHROPIC_API_KEY=your_key python app.py
"""

import base64
import json
import os

import anthropic
from flask import Flask, jsonify, render_template, request

import pokemon_data as PD

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = anthropic.Anthropic()
MODEL = "claude-opus-4-6"


# ---------------------------------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------------------------------

SYSTEM_ADVISOR = """あなたはポケモンスリープの専門アドバイザーです。
日本語で回答してください。
以下の知識を持っています：
- 各ポケモンのきのみタイプ・食材・スキルの特性
- 調査フィールドに合ったきのみの重要性
- チーム編成の最適化（元気管理、お手伝い速度、スキル発動率）
- せいかくによるステータス補正（お手伝い速度、スキル発動率、元気回復）
- サブスキルの重要度
- イベント対応チーム編成
- 育成の優先度

回答は具体的で実践的にしてください。
ユーザーのボックス情報が提供される場合、そのポケモンを優先的に参照してください。"""

SYSTEM_SCREENSHOT_ANALYSIS = """あなたはポケモンスリープのスクリーンショットを解析する専門AIです。
画像からポケモンの情報を抽出し、以下のJSON形式で返してください。

必ず以下のJSON形式で返してください（他のテキストは含めない）：
{
  "pokemon": [
    {
      "name": "ポケモン名（英語推奨）",
      "level": レベル数値,
      "specialty": "berry/ingredient/skill のいずれか",
      "nature": "せいかく（英語キー、例: timid, jolly, modest）",
      "main_skill": "スキル名（日本語でも可）",
      "berry": "きのみ名",
      "subskills": ["サブスキル1", "サブスキル2"],
      "note": "その他気づいた情報"
    }
  ],
  "analysis_text": "解析の要約テキスト"
}

情報が読み取れない場合はnullや空文字列を使用してください。
複数のポケモンが写っている場合はすべて抽出してください。"""


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


@app.route("/api/analyze-screenshot", methods=["POST"])
def analyze_screenshot():
    if "image" not in request.files:
        return jsonify({"error": "画像ファイルが見つかりません"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    # Detect media type
    content_type = image_file.content_type or "image/jpeg"
    if content_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        content_type = "image/jpeg"

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM_SCREENSHOT_ANALYSIS,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": content_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "このポケモンスリープのスクリーンショットを解析して、ポケモンの情報をJSON形式で返してください。",
                        },
                    ],
                }
            ],
        ) as stream:
            final_msg = stream.get_final_message()

        # Extract text block (not thinking block)
        result_text = ""
        for block in final_msg.content:
            if block.type == "text":
                result_text = block.text
                break

        # Try to parse JSON
        try:
            # Find JSON in the response (sometimes wrapped in markdown code block)
            json_text = result_text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            data = json.loads(json_text)
            return jsonify(data)
        except json.JSONDecodeError:
            # Return raw text if JSON parsing fails
            return jsonify({
                "pokemon": [],
                "analysis_text": result_text,
                "error": "JSONの解析に失敗しました。手動で入力してください。",
            })

    except anthropic.BadRequestError as e:
        return jsonify({"error": f"画像の解析に失敗しました: {e.message}"}), 400
    except Exception as e:
        return jsonify({"error": f"エラーが発生しました: {str(e)}"}), 500


@app.route("/api/search-events", methods=["POST"])
def search_events():
    """Search for current Pokemon Sleep events using Claude with web search."""
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "ポケモンスリープの現在開催中または最近開催されたイベント情報を調べてください。"
                        "特に週間イベント、限定イベント、コラボイベントについて教えてください。"
                        "簡潔に（200文字以内で）まとめてください。"
                    ),
                }
            ],
            tools=[
                {"type": "web_search_20260209", "name": "web_search"},
            ],
        ) as stream:
            final_msg = stream.get_final_message()

        result_text = ""
        for block in final_msg.content:
            if block.type == "text":
                result_text += block.text

        return jsonify({"events": result_text.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommend-team", methods=["POST"])
def recommend_team():
    """Generate team recommendations based on user's Pokemon box."""
    data = request.json
    pokemon_box = data.get("pokemon_box", [])
    area = data.get("area", "")
    area_text = data.get("area_text", area)
    goal = data.get("goal", "balanced")
    style = data.get("style", "snoozing")
    event = data.get("event", "")

    if not pokemon_box:
        return jsonify({"error": "ボックスが空です"}), 400

    # Build context about the user's Pokemon
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

    prompt = f"""以下のポケモンボックスの情報を元に、チーム編成を提案してください。

## 設定
- 調査フィールド: {area_text}
- 目標: {goal_labels.get(goal, goal)}
- 睡眠スタイル: {style_labels.get(style, style)}
{f'- 現在のイベント: {event}' if event else ''}

## マイボックス
{box_summary}

## 依頼
このボックスから最適なチーム（5匹）を3パターン提案してください。
各パターンについて：
1. チームの5匹（名前と役割）
2. このチームの戦略・強み
3. 注意点・デメリット

必ず以下のJSON形式で返してください：
{{
  "recommendations": [
    {{
      "title": "チームのコンセプト名",
      "team": [
        {{"name": "ポケモン名", "role": "役割（例: エース/サポート/食材担当）"}},
        ...5匹
      ],
      "strategy": "戦略の説明（200文字程度）",
      "cons": "注意点"
    }}
  ],
  "general_advice": "全体的なアドバイス（育成優先度、改善点など）"
}}"""

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM_ADVISOR,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            final_msg = stream.get_final_message()

        result_text = ""
        for block in final_msg.content:
            if block.type == "text":
                result_text = block.text
                break

        # Parse JSON
        try:
            json_text = result_text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            result = json.loads(json_text)
            return jsonify(result)
        except json.JSONDecodeError:
            # Return as general advice if JSON fails
            return jsonify({
                "recommendations": [],
                "general_advice": result_text,
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Multi-turn advisor chat."""
    data = request.json
    history = data.get("history", [])
    pokemon_box = data.get("pokemon_box", [])

    if not history:
        return jsonify({"error": "メッセージがありません"}), 400

    # Build system prompt with box context
    system = SYSTEM_ADVISOR
    if pokemon_box:
        box_summary = _format_box_for_prompt(pokemon_box)
        system += f"\n\n## ユーザーのマイボックス\n{box_summary}"

    # Convert history to API format (keep last 20 turns to manage context)
    messages = []
    for msg in history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=system,
            messages=messages,
        ) as stream:
            final_msg = stream.get_final_message()

        response_text = ""
        for block in final_msg.content:
            if block.type == "text":
                response_text = block.text
                break

        return jsonify({"response": response_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _format_box_for_prompt(pokemon_box: list) -> str:
    """Format the Pokemon box into a readable string for Claude."""
    lines = []
    for i, p in enumerate(pokemon_box, 1):
        specialty_map = {"berry": "きのみ", "ingredient": "食材", "skill": "スキル"}
        specialty = specialty_map.get(p.get("specialty", ""), p.get("specialty", "不明"))

        # Resolve skill name
        skill_key = p.get("main_skill", "")
        skill_name = ""
        if skill_key in PD.MAIN_SKILLS:
            skill_name = PD.MAIN_SKILLS[skill_key]["name"]
        elif skill_key:
            skill_name = skill_key

        # Resolve nature name
        nature_key = p.get("nature", "")
        nature_name = PD.NATURES.get(nature_key, {}).get("name", nature_key) if nature_key else "不明"

        subskills = p.get("subskills", [])
        subskills_str = "、".join(subskills) if subskills else "なし"

        line = (
            f"{i}. {p.get('name', '不明')} "
            f"Lv.{p.get('level', '?')} "
            f"[{specialty}] "
            f"せいかく:{nature_name} "
            f"スキル:{skill_name or '不明'} "
            f"きのみ:{p.get('berry', '不明')} "
            f"サブスキル:{subskills_str}"
        )
        if p.get("note"):
            line += f" メモ:{p['note']}"
        lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("警告: ANTHROPIC_API_KEY が設定されていません")
        print("  export ANTHROPIC_API_KEY=your_key_here")

    print("🌙 ポケモンスリープ アドバイザー 起動中...")
    print("  http://localhost:5000 でアクセスできます")
    app.run(debug=True, host="0.0.0.0", port=5000)
