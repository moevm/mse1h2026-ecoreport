import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()                     # .../report_generator/report_generator.py
REPORT_GENERATOR_DIR = CURRENT_FILE.parent                  # .../report_generator/
TASK_DIR = REPORT_GENERATOR_DIR.parent                      # .../task 4.2_implement_creation_minimal_report/
PROJECT_ROOT = TASK_DIR.parent                              # корень проекта (mse1h2026-ecoreport)

REPORT_UTILS_DIR = PROJECT_ROOT / "report_utils"
sys.path.insert(0, str(REPORT_UTILS_DIR))

print(f"DEBUG: REPORT_UTILS_DIR = {REPORT_UTILS_DIR}")
print(f"DEBUG: Файлы в report_utils: {[f.name for f in REPORT_UTILS_DIR.iterdir() if f.is_file()]}")

# Импортируем таблицы и графики
from tables import (
    main_system_specifications_table,
    monitored_points_table,
    lab_test_results_table,
    lab_dynamics
)
from diagrams import (
    concentration_dynamics_lineplot,
    comparison_bar_chart
)

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Image
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from jinja2 import Template
from datetime import datetime

BASE_DIR = REPORT_GENERATOR_DIR   # папка report_generator

# Регистрация шрифта
font_path = BASE_DIR / "Times New Roman" / "timesnewromanpsmt.ttf"
if font_path.exists():
    pdfmetrics.registerFont(TTFont("TimesNewRoman", str(font_path)))
else:
    print(f"⚠️ Шрифт не найден: {font_path}")

def mm_to_pt(mm):
    return mm * 2.83464567

LEFT_MARGIN = mm_to_pt(30)
RIGHT_MARGIN = mm_to_pt(15)
TOP_MARGIN = mm_to_pt(20)
BOTTOM_MARGIN = mm_to_pt(20)
FIRST_LINE_INDENT = mm_to_pt(12.5)


# функции колонтитулов
def header_footer_title(canvas, doc, full_name, short_name):
    """отрисовывает верхний и нижний колонтитулы на титульной странице"""

    canvas.saveState()
    width, height = A4
    title_style = ParagraphStyle(name="header_title", fontName="TimesNewRoman", fontSize=14, alignment=TA_CENTER, leading=16)

    top_text = Paragraph(full_name, title_style)
    w, h = top_text.wrap(doc.width, mm_to_pt(30))
    top_text.drawOn(canvas, doc.leftMargin, height - mm_to_pt(15) - h/2)

    bottom_text = Paragraph(f"ПРЕДПРИЯТИЕ {short_name}", title_style)
    w, h = bottom_text.wrap(doc.width, mm_to_pt(30))
    bottom_text.drawOn(canvas, doc.leftMargin, mm_to_pt(15))
    canvas.restoreState()


def header_footer_main(canvas, doc):
    """отрисовывает нижний колонтитул с номером страницы на всех страницах, кроме первой (титульной)"""
    canvas.saveState()
    if canvas.getPageNumber() > 1:
        canvas.setFont("TimesNewRoman", 12)
        canvas.drawCentredString(doc.pagesize[0] / 2, mm_to_pt(10), str(canvas.getPageNumber()))
    canvas.restoreState()


# вспомогательные функции
def create_list(items, normal_style):
    """создаёт маркированный список из переданных элементов"""

    list_items = [ListItem(Paragraph(item, ParagraphStyle(name='list_item', parent=normal_style, firstLineIndent=0, leftIndent=10))) 
                  for item in items]
    return ListFlowable(list_items, bulletType='bullet', bulletFontName='TimesNewRoman', 
                        bulletFontSize=12, leftIndent=FIRST_LINE_INDENT + 12.5, spaceAfter=5)


def read_section(file_path, title_style, normal_style, data_dict):
    """чтение файл раздела, обрабатка его как Jinja2-шаблон и возврат списока элементов PDF для вставки в документ"""

    elements = []
    if not os.path.exists(file_path):
        elements.append(Paragraph("Текст раздела отсутствует.", normal_style))
        return elements

    with open(file_path, "r", encoding="utf-8") as f:
        template_text = f.read()

    template = Template(template_text)
    rendered_text = template.render(**data_dict)

    buffer_list = []
    in_list = False

    for line in rendered_text.splitlines():
        line = line.strip()
        if not line:
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            continue

        if line.startswith("TITLE:"):
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            elements.append(Paragraph(line.replace("TITLE:", "").strip(), title_style))
        elif line.startswith("PARA:"):
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            para_style = ParagraphStyle(name='ParaStyle', parent=normal_style, firstLineIndent=FIRST_LINE_INDENT)
            elements.append(Paragraph(line.replace("PARA:", "").strip(), para_style))
        elif line.startswith("LIST:"):
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
            in_list = True
            buffer_list = []
        elif in_list:
            item_text = line.lstrip('•-*').strip()
            buffer_list.append(item_text)
        else:
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            para_style = ParagraphStyle(name='ParaStyle', parent=normal_style, firstLineIndent=FIRST_LINE_INDENT)
            elements.append(Paragraph(line, para_style))

    if buffer_list and in_list:
        elements.append(create_list(buffer_list, normal_style))
    return elements


def generate_report(user_data: dict, output_path: str = None):
    """генерирует PDF-отчёт на основе предоставленных данных"""

    if output_path is None:
        output_path = str(PROJECT_ROOT / "uploads" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN
    )

    title_style = ParagraphStyle(name="title", fontName="TimesNewRoman", fontSize=14, leading=21, alignment=TA_CENTER)
    normal_style = ParagraphStyle(name="normal", fontName="TimesNewRoman", fontSize=12, leading=18,
                                  firstLineIndent=FIRST_LINE_INDENT, alignment=TA_JUSTIFY)

    elements = []

    # Титульный лист
    elements.append(Spacer(1, mm_to_pt(90)))
    elements.append(Paragraph("ОТЧЕТ ПО ЭКОЛОГИЧЕСКОЙ БЕЗОПАСНОСТИ", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("ДРЕНАЖНЫХ СИСТЕМ", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"ЗА {user_data.get('YEAR', 2026)} ГОД", title_style))
    elements.append(PageBreak())

    # Содержание
    content_file = BASE_DIR / "report_module" / "content.txt"
    sections = []
    if content_file.exists():
        with open(content_file, "r", encoding="utf-8") as f:
            sections = [line.strip() for line in f if line.strip()]

        elements.append(Paragraph("СОДЕРЖАНИЕ", ParagraphStyle(name="toc", fontName="TimesNewRoman", fontSize=14, alignment=TA_CENTER)))
        elements.append(Spacer(1, 20))

        for i, section in enumerate(sections, 1):
            elements.append(Paragraph(f"{i}. {section}", normal_style))
            elements.append(Spacer(1, 5))
        elements.append(PageBreak())

    # 1–4 секции полностью из шаблонов
    for i in range(1, 5):
        section_file = BASE_DIR / "report_module" / f"section_{i}.txt"
        if section_file.exists():
            elements.extend(read_section(str(section_file), title_style, normal_style, user_data))
        elements.append(PageBreak())

    # характеристика дренажной системы (5 секция)
    section_file = BASE_DIR / "report_module" / "section_5.txt"
    if section_file.exists():
        elements.extend(read_section(str(section_file), title_style, normal_style, user_data))

    try:
        pipe_diam_str = str(user_data.get("PIPE_DIAMETER", "100")).replace(" мм", "").replace("mm", "").strip()
        pipe_depth_str = str(user_data.get("PIPE_DEPTH", "2.5")).replace(" м", "").replace("m", "").strip()
        pipe_length_str = str(user_data.get("PIPE_LENGTH", "1000")).replace(" м", "").replace("m", "").strip()

        table_system = main_system_specifications_table(
            system_type=user_data.get("OBJECT_TYPE", "город"),
            pipe_material=user_data.get("PIPE_MATERIAL", "—"),
            pipe_diameter=float(pipe_diam_str),
            laying_depth=float(pipe_depth_str),
            total_length=float(pipe_length_str),
            year_commissioned=int(user_data.get("PIPE_INSTALL_YEAR", 2026)),
            well_count=int(user_data.get("MANHOLE_COUNT", 5))
        )
        elements.append(table_system)
    except Exception as e:
        elements.append(Paragraph(f"Ошибка таблицы характеристик: {e}", normal_style))
    elements.append(Spacer(1, 15))
    elements.append(PageBreak())

    # =программа экологического мониторинга (6 секция)
    section_file = BASE_DIR / "report_module" / "section_6.txt"
    if section_file.exists():
        elements.extend(read_section(str(section_file), title_style, normal_style, user_data))

    if user_data.get("RESULTS_DYNAMIC"):
        try:
            dates = [datetime.strptime(d["date"], "%Y-%m-%d").date() for d in user_data["RESULTS_DYNAMIC"]]
            ph_values = [float(d.get("pH", 7.0)) for d in user_data["RESULTS_DYNAMIC"]]
            plot = concentration_dynamics_lineplot(ph_values, dates, label="pH", norm=7.0)
            elements.append(plot)
            elements.append(Paragraph("Рисунок 1 — Динамика показателя pH", normal_style))
        except Exception as e:
            elements.append(Paragraph(f"Не удалось построить график динамики: {e}", normal_style))
    else:
        elements.append(Paragraph("Данные динамики наблюдений отсутствуют.", normal_style))
    elements.append(Spacer(1, 15))
    elements.append(PageBreak())

    # результаты лабораторных исследований (7 секция)
    section_file = BASE_DIR / "report_module" / "section_7.txt"
    if section_file.exists():
        elements.extend(read_section(str(section_file), title_style, normal_style, user_data))

    try:
        bar = comparison_bar_chart(
            iron=float(user_data.get("RESULTS_IRON", 0.25)),
            mn=float(user_data.get("RESULTS_MANGANESE", 0.12)),
            no3=float(user_data.get("RESULTS_NITRATES", 42)),
            so4=float(user_data.get("RESULTS_SULFATES", 450))
        )
        elements.append(bar)
        elements.append(Paragraph("Рисунок 2 — Сравнение результатов наблюдений с нормативами", normal_style))

        table_lab = lab_test_results_table(
            ph=float(user_data.get("RESULTS_PH", 7.2)),
            iron=float(user_data.get("RESULTS_IRON", 0.25)),
            mn=float(user_data.get("RESULTS_MANGANESE", 0.12)),
            no3=float(user_data.get("RESULTS_NITRATES", 42)),
            so4=float(user_data.get("RESULTS_SULFATES", 450))
        )
        elements.append(table_lab)
    except Exception as e:
        elements.append(Paragraph(f"Ошибка результатов анализов: {e}", normal_style))
    elements.append(Spacer(1, 15))
    elements.append(PageBreak())

    # 8–11 секция
    for i in range(8, 12):
        section_file = BASE_DIR / "report_module" / f"section_{i}.txt"
        if section_file.exists():
            elements.extend(read_section(str(section_file), title_style, normal_style, user_data))
        elements.append(PageBreak())

    doc.build(
        elements,
        onFirstPage=lambda c, d: header_footer_title(c, d,
            user_data.get("FULL_OBJECT_NAME", "Объект"),
            user_data.get("SHORT_OBJECT_NAME", "КП")),
        onLaterPages=header_footer_main
    )

    print(f"Отчёт успешно создан: {output_path}")