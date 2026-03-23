from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from jinja2 import Template  

# определение базовой директории модуля
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# подключение шрифта Times New Roman
font_path = os.path.join(BASE_DIR, "Times New Roman", "timesnewromanpsmt.ttf")
pdfmetrics.registerFont(TTFont("TimesNewRoman", font_path))

def mm_to_pt(mm):
    """ перевод миллиметров в пункты (points) для ReportLab """ 
    return mm * 2.83464567

# поля страницы согласно ГОСТ 7.32-2017
LEFT_MARGIN = mm_to_pt(30)          # левое поле 30 мм
RIGHT_MARGIN = mm_to_pt(15)         # правое поле 15 мм
TOP_MARGIN = mm_to_pt(20)           # верхнее поле 20 мм
BOTTOM_MARGIN = mm_to_pt(20)        # нижнее поле 20 мм
FIRST_LINE_INDENT = mm_to_pt(12.5)  # отступ первой строки абзаца (красная строка) 1.25 мм


# функции колонтитулов

def header_footer_title(canvas, doc, full_name, short_name):
    """ отрисовывает верхний и нижний колонтитулы на титульной странице """
    canvas.saveState()
    width, height = A4

    # стиль верхнего колонтитула
    title_style = ParagraphStyle(
        name="header_title",
        fontName="TimesNewRoman",
        fontSize=14,
        alignment=TA_CENTER,
        leading=16  # межстрочный интервал
    )

    # верхний колонтитул
    top_text = Paragraph(full_name, title_style)
    # wrap на ширину документа с учётом полей
    w, h = top_text.wrap(doc.width, mm_to_pt(30))  # ширина страницы без полей
    top_text.drawOn(canvas, doc.leftMargin, height - mm_to_pt(15) - h/2)

    # нижний колонтитул
    bottom_text = Paragraph(f"ПРЕДПРИЯТИЕ {short_name}", title_style)
    w, h = bottom_text.wrap(doc.width, mm_to_pt(30))
    bottom_text.drawOn(canvas, doc.leftMargin, mm_to_pt(15))

    canvas.restoreState()

def header_footer_main(canvas, doc):
    """ отрисовывает нижний колонтитул с номером страницы на всех страницах, кроме первой (титульной) """
    canvas.saveState()
    page_num = canvas.getPageNumber()
    if page_num > 1:
        canvas.setFont("TimesNewRoman", 12)
        width = doc.pagesize[0]
        y = mm_to_pt(10)
        canvas.drawCentredString(width / 2, y, str(page_num))
    canvas.restoreState()


# вспомогательные функции для построения структуры отчета

def create_list(items, normal_style):
    """ создаёт маркированный список из переданных элементов """
    list_items = []
    for item in items:
        # каждый пункт – отдельный Paragraph с особым стилем
        p = Paragraph(item, ParagraphStyle(
            name='list_item',
            parent=normal_style,
            firstLineIndent=0,  # без красной строки
            leftIndent=10       # отступ текста от маркера
        ))
        list_items.append(ListItem(p))

    # общий контейнер списка с настройками отступов
    return ListFlowable(
        list_items,
        bulletType='bullet',                     # тип маркера
        bulletFontName='TimesNewRoman',
        bulletFontSize=12,
        leftIndent=FIRST_LINE_INDENT + 12.5,     # отступ всего списка слева
        bulletDedent=0,                          # маркер на уровне начала текста
        bulletOffset=0,
        spaceBefore=0,
        spaceAfter=5
    )


# чтение раздела с поддержкой Jinja2
def read_section(file_path, title_style, normal_style, data_dict):
    """ чтение файл раздела, обрабатка его как Jinja2-шаблон и возврат списока элементов PDF для вставки в документ """
    elements = []

    # проверка существования файла
    if not os.path.exists(file_path):
        elements.append(Paragraph("Текст раздела отсутствует.", normal_style))
        return elements
    
    # чтение файла как шаблон Jinja2
    with open(file_path, "r", encoding="utf-8") as f:
        template_text = f.read()

    # рендер шаблона через Jinja2
    template = Template(template_text)
    rendered_text = template.render(**data_dict)

    # переменные для обработки списков
    buffer_list = []    # временное хранилище пунктов текущего списка
    in_list = False     # флаг: нахождения внутри списка

    # разбитие отрендеренного текста построчно
    for line in rendered_text.splitlines():
        line = line.strip()

        # пустая строка – конец текущего блока 
        if not line:
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            continue

        # обработка маркеров разметки
        if line.startswith("TITLE:"):
            # завершение текущего списока, если он есть
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            elements.append(Paragraph(line.replace("TITLE:", "").strip(), title_style))

        elif line.startswith("PARA:"):
            # завершение списока, если он был активен
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            # стиль с красной строкой для абзаца
            para_style = ParagraphStyle(
                name='ParaStyle',
                parent=normal_style,
                firstLineIndent=FIRST_LINE_INDENT,
            )
            elements.append(Paragraph(line.replace("PARA:", "").strip(), para_style))

        elif line.startswith("LIST:"):
             # завершение предыдущего списка, если был
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))

            # начало нового списка
            in_list = True
            buffer_list = []

        elif in_list:
            # обработка строк внутри списка
            # попытка интерпретировать строку как Python-список
            try:
                import ast
                parsed = ast.literal_eval(line)
                if isinstance(parsed, list):
                    # если это список, добавляем все его элементы как отдельные пункты
                    buffer_list.extend(parsed)
                    continue
            except:
                pass
            # обычная строка списка – удаляем возможные маркеры в начале
            item_text = line.lstrip('•-*').strip()
            buffer_list.append(item_text)

        else:
            # обычный текст – рассматриваем как абзац (без маркера PARA)
            if buffer_list and in_list:
                elements.append(create_list(buffer_list, normal_style))
                buffer_list = []
                in_list = False
            para_style = ParagraphStyle(
                name='ParaStyle',
                parent=normal_style,
                firstLineIndent=FIRST_LINE_INDENT,
            )
            elements.append(Paragraph(line, para_style))

    # если после окончания файла остался незавершённый список, добавляем его
    if buffer_list and in_list:
        elements.append(create_list(buffer_list, normal_style))

    return elements


# основная функция генерации отчета
def generate_report(user_data, output_path="report.pdf"):
    """ генерирует PDF-отчёт на основе предоставленных данных """

    # настройка документа
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN
    )

    # определение стилей для разных типов текста
    title_style = ParagraphStyle(
        name="title",
        fontName="TimesNewRoman",
        fontSize=14,
        leading=21,
        alignment=TA_CENTER
    )

    normal_style = ParagraphStyle(
        name="normal",
        fontName="TimesNewRoman",
        fontSize=12,
        leading=18,
        firstLineIndent=FIRST_LINE_INDENT,
        alignment=TA_JUSTIFY
    )

    toc_title_style = ParagraphStyle(
        name="toc_title",
        fontName="TimesNewRoman",
        fontSize=14,
        alignment=TA_CENTER
    )

    elements = []

    # титульный лист
    elements.append(Spacer(1, mm_to_pt(90)))
    elements.append(Paragraph("ОТЧЕТ ПО ЭКОЛОГИЧЕСКОЙ БЕЗОПАСНОСТИ", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("ДРЕНАЖНЫХ СИСТЕМ", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("ЗА 2026 ГОД", title_style))
    elements.append(PageBreak())

    # содержание
    content_file = os.path.join(BASE_DIR, "report_module", "content.txt")
    if not os.path.exists(content_file):
        elements.append(Paragraph("Файл content.txt не найден.", normal_style))
    else:
        with open(content_file, "r", encoding="utf-8") as f:
            # чтение названия разделов (по одному на строке)
            sections = [line.strip() for line in f if line.strip()]

        elements.append(Paragraph("СОДЕРЖАНИЕ", toc_title_style))
        elements.append(Spacer(1, 20))

        # стиль для пунктов содержания (без красной строки)
        toc_style = ParagraphStyle(
            name='toc_item',
            parent=normal_style,
            firstLineIndent=0
        )

        # вывод нумерованного списока разделов
        for i, section in enumerate(sections, 1):
            elements.append(Paragraph(f"{i}. {section}", toc_style))
            elements.append(Spacer(1, 5))

        elements.append(PageBreak())

        # чтение и добавление разделов с подстановкой данных
        for i, section in enumerate(sections, 1):
            section_file = os.path.join(BASE_DIR, "report_module", f"section_{i}.txt")
            if os.path.exists(section_file):
                elements.extend(read_section(section_file, title_style, normal_style, user_data))
            else:
                # если файл раздела отсутствует, выводим только заголовок
                elements.append(Paragraph(f"Раздел {i}. {section}", title_style))
                elements.append(Paragraph("Текст отсутствует.", normal_style))
            # каждый раздел начинается с новой страницы
            elements.append(PageBreak())

    # построение структуры документа
    doc.build( elements,
    onFirstPage=lambda c, d: header_footer_title(c, d, user_data["FULL_OBJECT_NAME"], user_data["SHORT_OBJECT_NAME"]),
    onLaterPages=lambda c, d: header_footer_main(c, d)
    )
    print(f"Отчёт готов: {output_path}")