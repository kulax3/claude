"""
米在庫推移スプレッドシート生成スクリプト
パターン2（会社別シート）とパターン3（品種別シート）を生成する
"""

from openpyxl import Workbook
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side,
    GradientFill
)
from openpyxl.utils import get_column_letter

# ===================== マスタデータ =====================
YEARS = [2020, 2021, 2022, 2023, 2024]
VARIETIES = ["コシヒカリ", "ひとめぼれ", "あきたこまち", "ササニシキ", "つや姫", "ゆめぴりか", "新之助"]
COMPANIES = ["会社A", "会社B", "会社C"]
STEPS = ["移入在庫", "購入", "使用", "繰越在庫"]

# ===================== カラーパレット =====================
# 会社カラー（タブ・ヘッダ）
COMPANY_COLORS = {
    "会社A": {"tab": "2E75B6", "header": "BDD7EE", "subrow": "DEEAF1"},
    "会社B": {"tab": "375623", "header": "C6EFCE", "subrow": "E2EFDA"},
    "会社C": {"tab": "C55A11", "header": "FCE4D6", "subrow": "FFF2CC"},
}
# 品種カラー（7種）
VARIETY_COLORS = [
    {"tab": "7030A0", "header": "E2CFEC", "subrow": "F4E6FF"},
    {"tab": "2E75B6", "header": "BDD7EE", "subrow": "DEEAF1"},
    {"tab": "375623", "header": "C6EFCE", "subrow": "E2EFDA"},
    {"tab": "C55A11", "header": "FCE4D6", "subrow": "FFF2CC"},
    {"tab": "833C00", "header": "F8CBAD", "subrow": "FCE4D6"},
    {"tab": "636363", "header": "EDEDED", "subrow": "F5F5F5"},
    {"tab": "1F3864", "header": "B4C6E7", "subrow": "D9E2F3"},
]

YEAR_SEPARATOR_COLOR = "404040"
TOTAL_ROW_COLOR = "FFF2CC"
GRAND_TOTAL_COLOR = "FFD700"

# ===================== スタイルユーティリティ =====================

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def thin_border():
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)

def thick_border_top():
    thick = Side(style="medium", color=YEAR_SEPARATOR_COLOR)
    thin = Side(style="thin", color="BFBFBF")
    return Border(left=thin, right=thin, top=thick, bottom=thin)

def right_thick_border():
    thick = Side(style="medium", color="595959")
    thin = Side(style="thin", color="BFBFBF")
    return Border(left=thin, right=thick, top=thin, bottom=thin)

def set_cell(ws, row, col, value, font_bold=False, font_size=10,
             bg_color=None, align="left", num_format=None,
             border=None, font_color="000000"):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(bold=font_bold, size=font_size, color=font_color)
    cell.alignment = Alignment(
        horizontal=align, vertical="center", wrap_text=False
    )
    if bg_color:
        cell.fill = fill(bg_color)
    if num_format:
        cell.number_format = num_format
    if border:
        cell.border = border
    else:
        cell.border = thin_border()
    return cell

def apply_row_style(ws, row, col_start, col_end, bg_color=None, border_top=False):
    bdr = thick_border_top() if border_top else thin_border()
    for c in range(col_start, col_end + 1):
        cell = ws.cell(row=row, column=c)
        if bg_color:
            cell.fill = fill(bg_color)
        cell.border = bdr

def num_fmt():
    return '#,##0'

# ===================== パターン2：会社別シート =====================

def build_pattern2():
    wb = Workbook()
    wb.remove(wb.active)

    sheets_data = {}

    for ci, company in enumerate(COMPANIES):
        ws = wb.create_sheet(title=company)
        ws.sheet_properties.tabColor = COMPANY_COLORS[company]["tab"]
        col_w = COMPANY_COLORS[company]

        # --- 列幅設定 ---
        ws.column_dimensions["A"].width = 6   # 年度
        ws.column_dimensions["B"].width = 14  # 品種
        ws.column_dimensions["C"].width = 12  # 移入在庫
        ws.column_dimensions["D"].width = 12  # 購入
        ws.column_dimensions["E"].width = 12  # 使用
        ws.column_dimensions["F"].width = 14  # 繰越在庫

        # --- タイトル行 ---
        ws.merge_cells("A1:F1")
        title_cell = ws["A1"]
        title_cell.value = f"米在庫推移管理表　{company}"
        title_cell.font = Font(bold=True, size=14, color="FFFFFF")
        title_cell.fill = fill(COMPANY_COLORS[company]["tab"])
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28

        # --- ヘッダ行 ---
        headers = ["年度", "品種", "移入在庫", "購入", "使用", "繰越在庫"]
        hdr_color = col_w["header"]
        for c, h in enumerate(headers, 1):
            set_cell(ws, 2, c, h, font_bold=True, font_size=10,
                     bg_color=hdr_color, align="center")
        ws.row_dimensions[2].height = 20

        # --- データ行 ---
        current_row = 3
        year_start_rows = {}

        for yi, year in enumerate(YEARS):
            year_start_rows[year] = current_row
            is_first_year_row = True

            for vi, variety in enumerate(VARIETIES):
                row_bg = col_w["subrow"] if vi % 2 == 0 else "FFFFFF"
                border_top = is_first_year_row
                is_first_year_row = False

                # 年度（最初の品種行のみ表示）
                if vi == 0:
                    c = set_cell(ws, current_row, 1, year,
                                 font_bold=True, bg_color=col_w["header"],
                                 align="center",
                                 border=thick_border_top() if border_top else thin_border())
                else:
                    c = set_cell(ws, current_row, 1, "",
                                 bg_color=col_w["header"], align="center",
                                 border=thick_border_top() if border_top else thin_border())

                # 品種
                set_cell(ws, current_row, 2, variety,
                         bg_color=row_bg,
                         border=thick_border_top() if (vi == 0) else thin_border())

                # 移入在庫（前年繰越参照 or 手入力）
                move_in_col = "C"
                purchase_col = "D"
                usage_col = "E"
                carry_col = "F"

                for col_idx in [3, 4, 5]:
                    bdr = thick_border_top() if (vi == 0) else thin_border()
                    cell = ws.cell(row=current_row, column=col_idx, value=0)
                    cell.fill = fill(row_bg)
                    cell.border = bdr
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = num_fmt()
                    cell.font = Font(size=10)

                # 繰越在庫 = 移入在庫 + 購入 - 使用（数式）
                bdr = thick_border_top() if (vi == 0) else thin_border()
                carry_cell = ws.cell(
                    row=current_row, column=6,
                    value=f"=C{current_row}+D{current_row}-E{current_row}"
                )
                carry_cell.fill = fill("FFF2CC" if vi % 2 == 0 else "FFFDE7")
                carry_cell.border = bdr
                carry_cell.alignment = Alignment(horizontal="right", vertical="center")
                carry_cell.number_format = num_fmt()
                carry_cell.font = Font(size=10, bold=True)

                ws.row_dimensions[current_row].height = 18
                current_row += 1

            # 年度合計行
            subtotal_start = year_start_rows[year]
            subtotal_end = current_row - 1
            for col_idx, lbl in [(1, "小計"), (2, f"{year}年度 合計")]:
                cell = ws.cell(row=current_row, column=col_idx, value=lbl)
                cell.fill = fill(TOTAL_ROW_COLOR)
                cell.font = Font(bold=True, size=10)
                cell.alignment = Alignment(horizontal="center" if col_idx == 1 else "left",
                                           vertical="center")
                cell.border = thin_border()

            for col_idx in [3, 4, 5, 6]:
                col_l = get_column_letter(col_idx)
                formula = f"=SUM({col_l}{subtotal_start}:{col_l}{subtotal_end})"
                cell = ws.cell(row=current_row, column=col_idx, value=formula)
                cell.fill = fill(TOTAL_ROW_COLOR)
                cell.font = Font(bold=True, size=10)
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = num_fmt()
                cell.border = thin_border()

            ws.row_dimensions[current_row].height = 20
            current_row += 2  # 空行1行あけて次年度

        sheets_data[company] = ws

    # --- 全品種集計シート ---
    ws_sum = wb.create_sheet(title="全品種集計")
    ws_sum.sheet_properties.tabColor = "595959"
    ws_sum.column_dimensions["A"].width = 8
    ws_sum.column_dimensions["B"].width = 14
    ws_sum.column_dimensions["C"].width = 14
    ws_sum.column_dimensions["D"].width = 12
    ws_sum.column_dimensions["E"].width = 12
    ws_sum.column_dimensions["F"].width = 12
    ws_sum.column_dimensions["G"].width = 14

    ws_sum.merge_cells("A1:G1")
    tc = ws_sum["A1"]
    tc.value = "米在庫推移管理表　全品種集計"
    tc.font = Font(bold=True, size=14, color="FFFFFF")
    tc.fill = fill("404040")
    tc.alignment = Alignment(horizontal="center", vertical="center")
    ws_sum.row_dimensions[1].height = 28

    headers = ["年度", "品種", "会社A 繰越", "会社B 繰越", "会社C 繰越", "合計繰越", "前年比"]
    for c, h in enumerate(headers, 1):
        set_cell(ws_sum, 2, c, h, font_bold=True, bg_color="EDEDED", align="center")
    ws_sum.row_dimensions[2].height = 20

    row = 3
    for year in YEARS:
        for vi, variety in enumerate(VARIETIES):
            bg = "F5F5F5" if vi % 2 == 0 else "FFFFFF"
            set_cell(ws_sum, row, 1, year if vi == 0 else "",
                     font_bold=(vi == 0), bg_color="EDEDED", align="center")
            set_cell(ws_sum, row, 2, variety, bg_color=bg)
            for c in [3, 4, 5]:
                set_cell(ws_sum, row, c, 0, bg_color=bg, align="right", num_format=num_fmt())
            # 合計繰越
            fc = ws_sum.cell(row=row, column=6,
                             value=f"=C{row}+D{row}+E{row}")
            fc.fill = fill(TOTAL_ROW_COLOR)
            fc.font = Font(bold=True, size=10)
            fc.alignment = Alignment(horizontal="right", vertical="center")
            fc.number_format = num_fmt()
            fc.border = thin_border()
            # 前年比（2年目以降）
            if year > YEARS[0]:
                prev_row = row - len(VARIETIES) - 1  # 前年同品種（おおよそ）
                pc = ws_sum.cell(row=row, column=7,
                                 value=f'=IFERROR(F{row}/F{prev_row}-1,"-")')
                pc.number_format = "0.0%"
                pc.alignment = Alignment(horizontal="right", vertical="center")
                pc.border = thin_border()
            else:
                set_cell(ws_sum, row, 7, "-", align="center", bg_color=bg)

            ws_sum.row_dimensions[row].height = 18
            row += 1
        row += 1  # 年度区切り空行

    return wb


# ===================== パターン3：品種別シート =====================

def build_pattern3():
    wb = Workbook()
    wb.remove(wb.active)

    for vi, variety in enumerate(VARIETIES):
        vc = VARIETY_COLORS[vi]
        ws = wb.create_sheet(title=variety)
        ws.sheet_properties.tabColor = vc["tab"]

        # --- 列幅 ---
        ws.column_dimensions["A"].width = 8   # 会社
        ws.column_dimensions["B"].width = 7   # 年度
        ws.column_dimensions["C"].width = 13  # 移入在庫
        ws.column_dimensions["D"].width = 12  # 購入
        ws.column_dimensions["E"].width = 12  # 使用
        ws.column_dimensions["F"].width = 14  # 繰越在庫

        # --- タイトル ---
        ws.merge_cells("A1:F1")
        tc = ws["A1"]
        tc.value = f"米在庫推移管理表　{variety}"
        tc.font = Font(bold=True, size=14, color="FFFFFF")
        tc.fill = fill(vc["tab"])
        tc.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28

        # --- ヘッダ ---
        headers = ["会社", "年度", "移入在庫", "購入", "使用", "繰越在庫"]
        for c, h in enumerate(headers, 1):
            set_cell(ws, 2, c, h, font_bold=True, bg_color=vc["header"], align="center")
        ws.row_dimensions[2].height = 20

        current_row = 3
        company_row_starts = {}

        for ci, company in enumerate(COMPANIES):
            company_row_starts[company] = current_row
            co_color = COMPANY_COLORS[company]

            for yi, year in enumerate(YEARS):
                is_first = (yi == 0)
                row_bg = vc["subrow"] if yi % 2 == 0 else "FFFFFF"

                # 会社（最初の年度行のみ）
                bdr = thick_border_top() if is_first else thin_border()
                if is_first:
                    cell = ws.cell(row=current_row, column=1, value=company)
                    cell.fill = fill(co_color["header"])
                    cell.font = Font(bold=True, size=10)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = bdr
                else:
                    cell = ws.cell(row=current_row, column=1, value="")
                    cell.fill = fill(co_color["subrow"])
                    cell.border = bdr

                # 年度
                bdr2 = thick_border_top() if is_first else thin_border()
                set_cell(ws, current_row, 2, year,
                         font_bold=is_first, bg_color=co_color["header"] if is_first else row_bg,
                         align="center", border=bdr2)

                # 移入在庫・購入・使用
                for col_idx in [3, 4, 5]:
                    bdr3 = thick_border_top() if is_first else thin_border()
                    cell = ws.cell(row=current_row, column=col_idx, value=0)
                    cell.fill = fill(row_bg)
                    cell.border = bdr3
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = num_fmt()
                    cell.font = Font(size=10)

                # 繰越在庫
                bdr4 = thick_border_top() if is_first else thin_border()
                carry = ws.cell(
                    row=current_row, column=6,
                    value=f"=C{current_row}+D{current_row}-E{current_row}"
                )
                carry.fill = fill("FFF2CC" if yi % 2 == 0 else "FFFDE7")
                carry.border = bdr4
                carry.alignment = Alignment(horizontal="right", vertical="center")
                carry.number_format = num_fmt()
                carry.font = Font(bold=True, size=10)

                ws.row_dimensions[current_row].height = 18
                current_row += 1

            # 会社別小計行
            sub_start = company_row_starts[company]
            sub_end = current_row - 1

            cell = ws.cell(row=current_row, column=1, value=company)
            cell.fill = fill(co_color["header"])
            cell.font = Font(bold=True, size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border()

            cell2 = ws.cell(row=current_row, column=2, value="小計")
            cell2.fill = fill(TOTAL_ROW_COLOR)
            cell2.font = Font(bold=True, size=10)
            cell2.alignment = Alignment(horizontal="center", vertical="center")
            cell2.border = thin_border()

            for col_idx in [3, 4, 5, 6]:
                col_l = get_column_letter(col_idx)
                formula = f"=SUM({col_l}{sub_start}:{col_l}{sub_end})"
                cell = ws.cell(row=current_row, column=col_idx, value=formula)
                cell.fill = fill(TOTAL_ROW_COLOR)
                cell.font = Font(bold=True, size=10)
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = num_fmt()
                cell.border = thin_border()

            ws.row_dimensions[current_row].height = 20

            # アウトライン（折りたたみ）設定
            for r in range(sub_start, current_row):
                ws.row_dimensions[r].outline_level = 1
                ws.row_dimensions[r].hidden = False
            ws.sheet_properties.outlinePr.summaryBelow = True

            current_row += 2  # 会社間 空行

        # 全社合計行
        ws.merge_cells(f"A{current_row}:B{current_row}")
        mc = ws.cell(row=current_row, column=1, value=f"{variety}　全社合計")
        mc.fill = fill(GRAND_TOTAL_COLOR)
        mc.font = Font(bold=True, size=11)
        mc.alignment = Alignment(horizontal="center", vertical="center")
        mc.border = thin_border()
        ws.cell(row=current_row, column=2).border = thin_border()

        # 全社合計 = 各社小計行を合計
        subtotal_rows = [company_row_starts[co] + len(YEARS) for co in COMPANIES]
        for col_idx in [3, 4, 5, 6]:
            col_l = get_column_letter(col_idx)
            ref = "+".join([f"{col_l}{r}" for r in subtotal_rows])
            cell = ws.cell(row=current_row, column=col_idx, value=f"={ref}")
            cell.fill = fill(GRAND_TOTAL_COLOR)
            cell.font = Font(bold=True, size=11)
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = num_fmt()
            cell.border = thin_border()

        ws.row_dimensions[current_row].height = 22

    # --- 会社集計シート ---
    ws_co = wb.create_sheet(title="会社別集計")
    ws_co.sheet_properties.tabColor = "404040"
    ws_co.column_dimensions["A"].width = 10
    ws_co.column_dimensions["B"].width = 8
    for c in ["C", "D", "E", "F", "G", "H", "I"]:
        ws_co.column_dimensions[c].width = 12

    ws_co.merge_cells("A1:I1")
    tc = ws_co["A1"]
    tc.value = "会社別集計（全品種）"
    tc.font = Font(bold=True, size=14, color="FFFFFF")
    tc.fill = fill("404040")
    tc.alignment = Alignment(horizontal="center", vertical="center")
    ws_co.row_dimensions[1].height = 28

    headers = ["会社", "年度", "移入在庫", "購入", "使用", "繰越在庫",
               "全社移入合計", "全社購入合計", "全社繰越合計"]
    for c, h in enumerate(headers, 1):
        set_cell(ws_co, 2, c, h, font_bold=True, bg_color="EDEDED", align="center")
    ws_co.row_dimensions[2].height = 20

    row = 3
    for ci, company in enumerate(COMPANIES):
        co_color = COMPANY_COLORS[company]
        for yi, year in enumerate(YEARS):
            is_first = (yi == 0)
            bg = co_color["subrow"] if yi % 2 == 0 else "FFFFFF"
            bdr = thick_border_top() if is_first else thin_border()

            if is_first:
                cell = ws_co.cell(row=row, column=1, value=company)
                cell.fill = fill(co_color["header"])
                cell.font = Font(bold=True, size=10)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = bdr
            else:
                cell = ws_co.cell(row=row, column=1, value="")
                cell.fill = fill(co_color["subrow"])
                cell.border = bdr

            set_cell(ws_co, row, 2, year, bg_color=bg, align="center", border=bdr)
            for c in [3, 4, 5]:
                cell = ws_co.cell(row=row, column=c, value=0)
                cell.fill = fill(bg)
                cell.border = bdr
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = num_fmt()
                cell.font = Font(size=10)

            carry = ws_co.cell(row=row, column=6,
                               value=f"=C{row}+D{row}-E{row}")
            carry.fill = fill("FFF2CC")
            carry.border = bdr
            carry.alignment = Alignment(horizontal="right", vertical="center")
            carry.number_format = num_fmt()
            carry.font = Font(bold=True, size=10)

            for c in [7, 8, 9]:
                cell = ws_co.cell(row=row, column=c, value="-")
                cell.fill = fill("F5F5F5")
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = bdr

            ws_co.row_dimensions[row].height = 18
            row += 1
        row += 1

    # --- 全体集計シート ---
    ws_all = wb.create_sheet(title="全体集計")
    ws_all.sheet_properties.tabColor = "1F3864"
    ws_all.column_dimensions["A"].width = 7
    ws_all.column_dimensions["B"].width = 14
    for c in ["C", "D", "E", "F"]:
        ws_all.column_dimensions[c].width = 13

    ws_all.merge_cells("A1:F1")
    tc = ws_all["A1"]
    tc.value = "全体集計（年度×品種）"
    tc.font = Font(bold=True, size=14, color="FFFFFF")
    tc.fill = fill("1F3864")
    tc.alignment = Alignment(horizontal="center", vertical="center")
    ws_all.row_dimensions[1].height = 28

    headers = ["年度", "品種", "移入在庫", "購入", "使用", "繰越在庫"]
    for c, h in enumerate(headers, 1):
        set_cell(ws_all, 2, c, h, font_bold=True, bg_color="B4C6E7", align="center")
    ws_all.row_dimensions[2].height = 20

    row = 3
    for yi, year in enumerate(YEARS):
        for vi, variety in enumerate(VARIETIES):
            bg = "D9E2F3" if vi % 2 == 0 else "FFFFFF"
            set_cell(ws_all, row, 1, year if vi == 0 else "",
                     font_bold=(vi == 0),
                     bg_color="B4C6E7" if vi == 0 else "D9E2F3",
                     align="center",
                     border=thick_border_top() if vi == 0 else thin_border())
            set_cell(ws_all, row, 2, variety, bg_color=bg,
                     border=thick_border_top() if vi == 0 else thin_border())
            for c in [3, 4, 5]:
                cell = ws_all.cell(row=row, column=c, value=0)
                cell.fill = fill(bg)
                cell.border = thick_border_top() if vi == 0 else thin_border()
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = num_fmt()
                cell.font = Font(size=10)
            carry = ws_all.cell(row=row, column=6,
                                value=f"=C{row}+D{row}-E{row}")
            carry.fill = fill("FFF2CC")
            carry.border = thick_border_top() if vi == 0 else thin_border()
            carry.alignment = Alignment(horizontal="right", vertical="center")
            carry.number_format = num_fmt()
            carry.font = Font(bold=True, size=10)
            ws_all.row_dimensions[row].height = 18
            row += 1
        row += 1

    return wb


# ===================== メイン =====================

if __name__ == "__main__":
    wb2 = build_pattern2()
    wb2.save("/home/user/claude/rice_inventory_pattern2_会社別.xlsx")
    print("パターン2 保存完了: rice_inventory_pattern2_会社別.xlsx")

    wb3 = build_pattern3()
    wb3.save("/home/user/claude/rice_inventory_pattern3_品種別.xlsx")
    print("パターン3 保存完了: rice_inventory_pattern3_品種別.xlsx")
