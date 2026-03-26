import csv
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---- 共通スタイル定義 ----
def header_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def make_border():
    s = Side(style="thin", color="AAAAAA")
    return Border(left=s, right=s, top=s, bottom=s)

def set_header(ws, row, col, value, bg="2E75B6", fg="FFFFFF", size=11):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(bold=True, color=fg, size=size)
    c.fill = header_fill(bg)
    c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    c.border = make_border()
    return c

def set_cell(ws, row, col, value, bg=None, bold=False, wrap=True, indent=0):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(bold=bold, size=10)
    c.alignment = Alignment(wrap_text=wrap, vertical="top", indent=indent)
    c.border = make_border()
    if bg:
        c.fill = header_fill(bg)
    return c

def set_section(ws, row, col_span, value, bg="D6E4F0"):
    c = ws.cell(row=row, column=1, value=value)
    c.font = Font(bold=True, size=10, color="1F4E79")
    c.fill = header_fill(bg)
    c.alignment = Alignment(vertical="center", indent=1)
    c.border = make_border()
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=col_span)

# ---- CSVを読み込んでAIタスクを抽出 ----
def load_ai_tasks(filepath):
    tasks = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("タスクリスト", "").strip() == "AI":
                tasks.append(row)
    return tasks

# ---- タスクをカテゴリに分類 ----
CATEGORIES = [
    ("Claude Code系",        ["code", ".claude", "コンソール", "Claude code", "クラウド実行"]),
    ("AI活用事例",           ["例1", "例2", "例3", "例4", "例5"]),
    ("NotebookLM/Gemini系",  ["notebookLM", "LM", "gem", "Gemini", "書籍"]),
    ("Cowork/ツール系",      ["cowork", "channels", "antigravity", "ブラウザ", "google AI Studio", "拡張機能", "skills人格", "meet文字", "Tasks →"]),
    ("その他",               []),  # fallback
]

def classify(task_name):
    name_lower = task_name.lower()
    for cat, keywords in CATEGORIES[:-1]:
        for kw in keywords:
            if kw.lower() in name_lower:
                return cat
    return "その他"

# ---- カテゴリ色マップ ----
CAT_COLORS = {
    "Claude Code系":       "D6E4F0",
    "AI活用事例":          "E2EFDA",
    "NotebookLM/Gemini系": "FFF2CC",
    "Cowork/ツール系":     "FCE4D6",
    "その他":              "F2F2F2",
}

CAT_HEADER_COLORS = {
    "Claude Code系":       "2E75B6",
    "AI活用事例":          "548235",
    "NotebookLM/Gemini系": "BF8F00",
    "Cowork/ツール系":     "C55A11",
    "その他":              "7F7F7F",
}

# 手順書の内容定義
PROCEDURES = {
    "Claude Code系": {
        "概要": "Claude Codeの導入・設定・活用に関するタスク群。開発環境の整備からスキル習得まで含む。",
        "手順": [
            ("1", "初期設定を完了する", "code 初期設定 タスクを参照。認証・プロジェクト設定を行う。"),
            ("2", "コマンド早見表を作成する", "code コマンド早見表 タスク。よく使うコマンドを一覧化。"),
            ("3", "フォルダ・階層構造を整理する", "code 階層、フォルダ 公式 タスク。公式ドキュメントを参照。"),
            ("4", ".claudeフォルダを育てる", ".claude 育てる / .claude フォルダ 説明 タスク。カスタム設定を充実させる。"),
            ("5", "セキュリティ設定を行う", "code 堅めのセキュリティ タスク。アクセス制御・権限設定を確認。"),
            ("6", "Skillsを設定する", "code skill / skills人格設定 タスク。AIエージェントの役割を定義。"),
            ("7", "エージェントの作り方を学ぶ", "code エージェントのつくりかた タスク。公式ドキュメント・サンプルを学習。"),
            ("8", "Chrome拡張・コンソールを整備", "改善 claude chrome / codeコンソール タスク。"),
            ("9", "活用事例28を整備 (KEITA)", "code 活用事例28 KEITA タスク。社内展開用の事例集を作成。"),
            ("10", "クラウド実行環境を確認", "ニュース codeクラウド実行 タスク。"),
        ],
    },
    "AI活用事例": {
        "概要": "Claude Codeを活用した具体的な業務改善事例の整備。",
        "手順": [
            ("1", "例1: 価格比較を実装", "AIを使った価格データの自動収集・比較スクリプト作成。"),
            ("2", "例2: 週レポート作成を自動化", "週次レポートの雛形生成・データ集計を自動化。"),
            ("3", "例3: 日タスク作成を自動化", "Google Tasksと連携した日次タスクの自動生成フローを構築。"),
            ("4", "例4: スライド作成を効率化", "AIによるプレゼン資料の自動生成・構成提案。"),
            ("5", "例5: ダサくないスライドを作成", "デザインテンプレート活用でビジュアルクオリティを向上。"),
        ],
    },
    "NotebookLM/Gemini系": {
        "概要": "NotebookLM・Geminiを活用した情報管理・分析タスク。",
        "手順": [
            ("1", "NotebookLMのプロンプト保管庫を整備", "notebookLM プロンプト保管庫 タスク。よく使うプロンプトを体系化して保存。"),
            ("2", "Gem × LM の連携設定", "gem x LM すべて タスク。GeminiとNotebookLMの連携フローを確立。"),
            ("3", "書籍LMを整備", "（書籍LM）タスク。書籍情報のNotebookLM管理を設定。"),
            ("4", "Meetの文字起こし・構造化", "meet文字起こしと構造化 Gemini？タスク。会議録の自動構造化フローを構築。"),
        ],
    },
    "Cowork/ツール系": {
        "概要": "Cowork・Antigravity等のAIツールの導入・設定タスク。",
        "手順": [
            ("1", "Cowork導入時の注意事項を確認", "cowork 導入の注意 タスク。契約・権限・データ管理ポリシーを確認。"),
            ("2", "Coworkを設定・運用開始", "cowork タスク。チームアカウントの設定・メンバー招待を実施。"),
            ("3", "Channelsを設定", "channels 設定 タスク。通知・連携チャンネルを整備。"),
            ("4", "Antigravityの日本語プロンプトを整備", "antigravity / antigravity 日本語プロンプト タスク。"),
            ("5", "ブラウザ操作自動化を設定", "ブラウザ操作 タスク。AIによるブラウザ自動化ツールを導入。"),
            ("6", "PC変更時の拡張機能を引き継ぎ", "拡張機能 PC変更 タスク。Chrome拡張の設定をエクスポート・インポート。"),
            ("7", "Google AI Studioを活用", "google AI Studio タスク。APIキー取得・プロトタイプ開発環境として活用。"),
            ("8", "TasksのスプレッドシートB化", "Tasks →スプシ化 タスク。Google Tasksデータを自動でスプシに転記。"),
        ],
    },
    "その他": {
        "概要": "上記カテゴリに分類されないAI関連タスク。",
        "手順": [
            ("1", "投資関連AIツールを調査", "投資 タスク。AIを活用した投資分析・情報収集ツールを調査・導入。"),
        ],
    },
}

# ========================================================
# シート1: AI タスク一覧
# ========================================================
def build_sheet_list(wb, tasks):
    ws = wb.active
    ws.title = "AI タスク一覧"
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"

    headers = ["#", "タスク名", "カテゴリ", "ステータス", "期限", "メモ"]
    col_widths = [5, 40, 20, 10, 12, 30]

    for i, (h, w) in enumerate(zip(headers, col_widths), 1):
        set_header(ws, 1, i, h)
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.row_dimensions[1].height = 22

    for idx, task in enumerate(tasks, 1):
        name = (task.get("タスク名") or "").strip()
        cat = classify(name)
        status = (task.get("ステータス") or "").strip()
        deadline = (task.get("期限") or "").strip()
        memo = (task.get("メモ") or "").strip()
        bg = CAT_COLORS[cat]

        set_cell(ws, idx + 1, 1, idx, bg=bg)
        set_cell(ws, idx + 1, 2, name, bg=bg)
        set_cell(ws, idx + 1, 3, cat, bg=bg)
        set_cell(ws, idx + 1, 4, status, bg=bg)
        set_cell(ws, idx + 1, 5, deadline, bg=bg)
        set_cell(ws, idx + 1, 6, memo, bg=bg)
        ws.row_dimensions[idx + 1].height = 18

# ========================================================
# シート2: カテゴリ別分類
# ========================================================
def build_sheet_category(wb, tasks):
    ws = wb.create_sheet("カテゴリ別分類")
    ws.sheet_view.showGridLines = False

    col_widths = [5, 40, 10, 12, 30]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    row = 1
    for cat, _, in CATEGORIES:
        cat_tasks = [t for t in tasks if classify(t.get("タスク名", "").strip()) == cat]
        if not cat_tasks:
            continue

        # カテゴリヘッダー
        set_section(ws, row, 5, f"■ {cat}（{len(cat_tasks)}件）", bg=CAT_COLORS[cat])
        row += 1

        # 列ヘッダー
        for i, h in enumerate(["#", "タスク名", "ステータス", "期限", "メモ"], 1):
            set_header(ws, row, i, h, bg=CAT_HEADER_COLORS[cat])
        row += 1

        for sub_idx, task in enumerate(cat_tasks, 1):
            name = (task.get("タスク名") or "").strip()
            status = (task.get("ステータス") or "").strip()
            deadline = (task.get("期限") or "").strip()
            memo = (task.get("メモ") or "").strip()
            bg = CAT_COLORS[cat]
            set_cell(ws, row, 1, sub_idx, bg=bg)
            set_cell(ws, row, 2, name, bg=bg)
            set_cell(ws, row, 3, status, bg=bg)
            set_cell(ws, row, 4, deadline, bg=bg)
            set_cell(ws, row, 5, memo, bg=bg)
            ws.row_dimensions[row].height = 18
            row += 1

        row += 1  # カテゴリ間の空行

# ========================================================
# シート3: 手順書
# ========================================================
def build_sheet_manual(wb, tasks):
    ws = wb.create_sheet("手順書")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 45

    # タイトル
    title_cell = ws.cell(row=1, column=1, value="AI タスク 手順書")
    title_cell.font = Font(bold=True, size=14, color="1F4E79")
    title_cell.fill = header_fill("2E75B6")
    title_cell.alignment = Alignment(vertical="center", horizontal="center")
    title_cell.border = make_border()
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3)
    ws.row_dimensions[1].height = 30

    row = 2

    for cat, _ in CATEGORIES:
        cat_tasks = [t for t in tasks if classify(t.get("タスク名", "").strip()) == cat]
        proc = PROCEDURES.get(cat, {})
        if not cat_tasks and not proc:
            continue

        # カテゴリタイトル
        cat_cell = ws.cell(row=row, column=1, value=f"【{cat}】")
        cat_cell.font = Font(bold=True, size=12, color="FFFFFF")
        cat_cell.fill = header_fill(CAT_HEADER_COLORS[cat])
        cat_cell.alignment = Alignment(vertical="center", indent=1)
        cat_cell.border = make_border()
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
        ws.row_dimensions[row].height = 24
        row += 1

        # 概要
        set_section(ws, row, 3, "概要", bg="E9EFF8")
        row += 1
        c = ws.cell(row=row, column=1, value=proc.get("概要", ""))
        c.font = Font(size=10)
        c.alignment = Alignment(wrap_text=True, vertical="top", indent=1)
        c.border = make_border()
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
        ws.row_dimensions[row].height = 40
        row += 1

        # 手順ヘッダー
        for i, h in enumerate(["手順", "作業内容", "詳細・備考"], 1):
            set_header(ws, row, i, h, bg=CAT_HEADER_COLORS[cat])
        ws.row_dimensions[row].height = 22
        row += 1

        # 手順内容
        for step_num, step_title, step_detail in proc.get("手順", []):
            bg = CAT_COLORS[cat]
            set_cell(ws, row, 1, step_num, bg=bg, bold=True)
            set_cell(ws, row, 2, step_title, bg=bg, bold=True)
            set_cell(ws, row, 3, step_detail, bg=bg)
            ws.row_dimensions[row].height = 32
            row += 1

        row += 1  # セクション間の空行

# ========================================================
# メイン処理
# ========================================================
def main():
    csv_path = "tasks.csv"
    output_path = "AI_tasks_organized.xlsx"

    tasks = load_ai_tasks(csv_path)
    print(f"AIタスク数: {len(tasks)}件")

    wb = openpyxl.Workbook()

    build_sheet_list(wb, tasks)
    build_sheet_category(wb, tasks)
    build_sheet_manual(wb, tasks)

    wb.save(output_path)
    print(f"保存完了: {output_path}")

if __name__ == "__main__":
    main()
