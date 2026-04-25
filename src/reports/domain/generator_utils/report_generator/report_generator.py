from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, KeepTogether,
    PageBreak, ListFlowable, ListItem, Table, TableStyle
)
from datetime import datetime
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from jinja2 import Template
import os
from reports.domain.generator_utils.report_utils.tables import (
    monitored_points_table,
    lab_test_results_table,
    observation_dynamics_table
)

from reports.domain.generator_utils.report_utils.diagrams import (
    comparison_bar_chart,
    concentration_dynamics_lineplot
)

class ReportGenerator:
    """ Генератор PDF-отчетов """
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # шрифт
        font_path = os.path.join(self.BASE_DIR, "Times New Roman", "timesnewromanpsmt.ttf")
        pdfmetrics.registerFont(TTFont("TimesNewRoman", font_path))

        # отступы
        self.LEFT_MARGIN = self.mm_to_pt(30)
        self.RIGHT_MARGIN = self.mm_to_pt(15)
        self.TOP_MARGIN = self.mm_to_pt(20)
        self.BOTTOM_MARGIN = self.mm_to_pt(20)
        self.FIRST_LINE_INDENT = self.mm_to_pt(12.5)

    # конвертация мм в пункты 
    def mm_to_pt(self, mm):
        return mm * 2.83464567

    # преобразование даты из формата YYYY-MM-DD в DD.MM.YYYY
    def format_date_ddmmyyyy(self, value):
        if not value:
            return ""

        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.strftime("%d.%m.%Y")
        except Exception:
            return value
    
    # верхний/нижний колонтитулы на титульной странице
    def header_footer_title(self, canvas, doc, full_name, short_name):
        canvas.saveState()
        width, height = A4

        style = ParagraphStyle(
            name="header",
            fontName="TimesNewRoman",
            fontSize=14,
            alignment=TA_CENTER,
            leading=16,
            textColor=(0, 0, 0)
        )

        top = Paragraph(full_name, style)
        w, h = top.wrap(doc.width, self.mm_to_pt(30))
        top.drawOn(canvas, doc.leftMargin, height - self.mm_to_pt(15) - h / 2)

        bottom = Paragraph(f"ПРЕДПРИЯТИЕ {short_name}", style)
        w, h = bottom.wrap(doc.width, self.mm_to_pt(30))
        bottom.drawOn(canvas, doc.leftMargin, self.mm_to_pt(15))

        canvas.restoreState()

    # нижний колонтитул на остальных страницах (нумерация страниц)
    def header_footer_main(self, canvas, doc):
        canvas.saveState()
        if canvas.getPageNumber() > 1:
            canvas.setFont("TimesNewRoman", 12)
            width = doc.pagesize[0]
            canvas.drawCentredString(width / 2, self.mm_to_pt(10), str(canvas.getPageNumber()))
        canvas.restoreState()

    # создание маркированных списков
    def create_list(self, items, normal_style):
        list_items = []

        for item in items:
            p = Paragraph(item, ParagraphStyle(
                name='list_item',
                parent=normal_style,
                firstLineIndent=0,
                leftIndent=0
            ))
            list_items.append(ListItem(p))

        return ListFlowable(
            list_items,
            bulletType='bullet',
            bulletFontName='TimesNewRoman',
            bulletFontSize=12,
            leftIndent=10,
            bulletIndent=0
        )

    # создание таблицы характеристики системы
    def create_system_characteristics_table(self, data_dict, normal_style):
        # стиль для заголовков таблицы
        header_style = ParagraphStyle(
            name='table_header',
            parent=normal_style,
            firstLineIndent=0,
            alignment=TA_CENTER,
            fontName='TimesNewRoman',
            fontSize=12,
            leading=14,
            spaceAfter=4,
            spaceBefore=4,
            textColor=(0, 0, 0)
        )

        # стиль для текста в ячейках
        table_text_style = ParagraphStyle(
            name='table_text',
            parent=normal_style,
            firstLineIndent=0,
            alignment=TA_CENTER,
            fontName='TimesNewRoman',
            fontSize=12,
            textColor=(0, 0, 0)
        )

        # стиль для значений в ячейках
        value_style = ParagraphStyle(
            name='table_value',
            parent=table_text_style,
            alignment=TA_CENTER,
            fontName='TimesNewRoman',
            fontSize=12,
            textColor=(0, 0, 0)
        )

        # данные таблицы
        data = [
            [Paragraph("Параметр", header_style), Paragraph("Значение", header_style), Paragraph("Единицы измерения", header_style)],
            [Paragraph("Тип дренажной системы", table_text_style), Paragraph(str(data_dict.get("SYSTEM_TYPE", "Не указано")), value_style), "-"],
            [Paragraph("Материал труб", table_text_style), Paragraph(str(data_dict.get("PIPE_MATERIAL", "Не указано")), value_style), "-"],
            [Paragraph("Диаметр труб", table_text_style), Paragraph(str(data_dict.get("PIPE_DIAMETER", "Не указано")), value_style), "мм"],
            [Paragraph("Глубина заложения", table_text_style), Paragraph(str(data_dict.get("PIPE_DEPTH", "Не указано")), value_style), "м"],
            [Paragraph("Общая протяженность", table_text_style), Paragraph(str(data_dict.get("PIPE_LENGTH", "Не указано")), value_style), "м"],
            [Paragraph("Год ввода в эксплуатацию", table_text_style), Paragraph(str(data_dict.get("PIPE_INSTALL_YEAR", "Не указано")), value_style), "-"],
            [Paragraph("Количество колодцев", table_text_style), Paragraph(str(data_dict.get("MANHOLE_COUNT", "Не указано")), value_style), "шт"],
        ]

        # создание таблицы с заданными данными и стилем
        table = Table(data, colWidths=[self.mm_to_pt(66), self.mm_to_pt(53), self.mm_to_pt(50)])
        
        # применение стиля к таблице
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'TimesNewRoman'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.8, (0, 0, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        return table

    # проверка наличия данных для раздела "Характеристики системы"
    def has_system_characteristics(self, data_dict):
        # проверка наличия положительных числовых значений
        def has_positive_number(value):
            if value is None:
                return False
            try:
                return float(str(value).replace(',', '.')) > 0
            except ValueError:
                return False

        text_values = [
            data_dict.get('SYSTEM_TYPE'),
            data_dict.get('PIPE_MATERIAL')
        ]
        if any(str(v).strip() for v in text_values):
            return True

        # проверка числовых полей
        numeric_values = [
            data_dict.get('PIPE_DIAMETER'),
            data_dict.get('PIPE_DEPTH'),
            data_dict.get('PIPE_LENGTH')
        ]
        if any(has_positive_number(v) for v in numeric_values):
            return True

        if has_positive_number(data_dict.get('PIPE_INSTALL_YEAR')):
            return True

        if has_positive_number(data_dict.get('MANHOLE_COUNT')):
            return True

        return False

    # создание таблиц для разделов "Контрольные точки", "Результаты лабораторных исследований" и "Динамика наблюдений"
    def create_table_element(self, table_type, data_dict, normal_style):
        # таблица "Характеристики системы"
        if table_type == "SYSTEM_CHARACTERISTICS":
            if self.has_system_characteristics(data_dict):
                return self.create_system_characteristics_table(data_dict, normal_style)
            return None

        # таблица "Контрольные точки"
        if table_type == "OBSERVATION_POINTS":
            points = []
            for item in data_dict.get("OBSERVATION_POINTS", []):
                if not isinstance(item, dict):
                    continue
                points.append((
                    str(item.get("observation_point") or item.get("name") or ""),
                    item.get("latitude") if item.get("latitude") is not None else item.get("lat") or 0,
                    item.get("longitude") if item.get("longitude") is not None else item.get("lon") or 0,
                    str(item.get("medium_type") or item.get("type") or ""),
                    str(item.get("description") or "")
                ))
            return monitored_points_table(points, fontname="TimesNewRoman", fontsize=12) if points else None

        # таблица "Результаты лабораторных исследований"
        if table_type == "TEST_RESULTS":
            results = data_dict.get("TEST_RESULTS", [])
            return lab_test_results_table(results, fontname="TimesNewRoman", fontsize=12) if results else None

        # таблица "Динамика наблюдений"
        if table_type == "OBSERVATION_DYNAMICS":
            dynamics = data_dict.get("OBSERVATION_DYNAMICS", [])
            return observation_dynamics_table(dynamics, fontname="TimesNewRoman", fontsize=12) if dynamics else None

        return None

    def create_graph_element(self, graph_type, data_dict, normal_style):
        # график "Сравнение концентраций загрязняющих веществ"
        if graph_type == "TEST_RESULTS":
            results = data_dict.get("TEST_RESULTS", [])
            return comparison_bar_chart(results) if results else None

        # таблица "Динамика наблюдений"
        if "OBSERVATION_DYNAMICS" in graph_type:
            dynamics = data_dict.get("OBSERVATION_DYNAMICS", [])
            metric = graph_type.replace("OBSERVATION_DYNAMICS: ", "").strip()
            results = data_dict.get("TEST_RESULTS", [])
            return concentration_dynamics_lineplot(results, dynamics, metric) if dynamics else None

        return None


    # чтение и обработка шаблонов разделов
    def read_section(self, file_path, title_style, normal_style, data_dict):
        elements = []

        if not os.path.exists(file_path):
            elements.append(Paragraph("Текст раздела отсутствует", normal_style))
            return elements

        # обработка специальных полей перед рендерингом
        processed_data = data_dict.copy()
        
        # преобразование DOCUMENTS_GOST из списка в строку для отображения в LIST
        if isinstance(processed_data.get("DOCUMENTS_GOST"), list):
            processed_data["DOCUMENTS_GOST"] = "\n".join(processed_data["DOCUMENTS_GOST"])

        with open(file_path, "r", encoding="utf-8") as f:
            template = Template(f.read())

        rendered = template.render(**processed_data)

        buffer_list = []
        in_list = False
        pending_right_para = None
        pending_center_para = None
        pending_graph_desc = None

        for line in rendered.splitlines():
            line = line.strip()

            if not line:
                if buffer_list and in_list:
                    elements.append(self.create_list(buffer_list, normal_style))
                    buffer_list, in_list = [], False
                continue

            if line.startswith("TITLE:"):
                elements.append(Paragraph(line.replace("TITLE:", "").strip(), title_style))

            elif line.startswith("PARA:"):
                style = ParagraphStyle(
                    name='para',
                    parent=normal_style,
                    firstLineIndent=self.FIRST_LINE_INDENT
                )
                elements.append(Paragraph(line.replace("PARA:", "").strip(), style))

            elif line.startswith("RIGHT_PARA:"):
                pending_right_para = line.replace("RIGHT_PARA:", "").strip()

            elif line.startswith("CENTER_PARA:"):
                pending_center_para = line.replace("CENTER_PARA:", "").strip()

            elif line.startswith("GRAPH_DESC:"):
                pending_graph_desc = line.replace("GRAPH_DESC:", "").strip()

            elif line.startswith("TABLE:"):
                table_type = line.replace("TABLE:", "").strip()
                table_element = self.create_table_element(table_type, data_dict, normal_style)
                if table_element:
                    if pending_right_para is not None:
                        style = ParagraphStyle(
                            name='right_para',
                            parent=normal_style,
                            alignment=TA_RIGHT
                        )
                        elements.append(Paragraph(pending_right_para, style))
                        pending_right_para = None
                    elements.append(table_element)
                else:
                    pending_right_para = None

            elif line.startswith("GRAPH:"):
                graph_type = line.replace("GRAPH:", "").strip()
                graph_element = self.create_graph_element(graph_type, data_dict, normal_style)
                if graph_element:
                    group = [graph_element]
                    if pending_graph_desc:
                        style = ParagraphStyle(
                            name='para',
                            parent=normal_style,
                            firstLineIndent=self.FIRST_LINE_INDENT
                        )
                        group.insert(0, Paragraph(pending_graph_desc, style))
                        pending_graph_desc = None
                    if pending_center_para is not None:
                        style = ParagraphStyle(
                            name='center_para',
                            parent=normal_style,
                            alignment=TA_CENTER
                        )

                        group.append(Paragraph(pending_center_para, style))
                        pending_center_para = None
                    group.append(Spacer(72, 24))
                    elements.append(KeepTogether(group))
                else:
                    pending_center_para = None

            elif line.startswith("LIST:"):
                in_list = True
                buffer_list = []

            elif in_list:
                buffer_list.append(line.lstrip('•-*').strip())

            else:
                style = ParagraphStyle(
                    name='para',
                    parent=normal_style,
                    firstLineIndent=self.FIRST_LINE_INDENT
                )
                elements.append(Paragraph(line, style))

        if buffer_list and in_list:
            elements.append(self.create_list(buffer_list, normal_style))

        return elements

    # основная функция генерации отчета
    def generate(self, user_data) -> bytes:
        buffer = BytesIO()

        # форматирование даты
        user_data = user_data.copy()
        user_data["REPORT_DATE"] = self.format_date_ddmmyyyy(
            user_data.get("REPORT_DATE")
        )

        # создание документа
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=self.LEFT_MARGIN,
            rightMargin=self.RIGHT_MARGIN,
            topMargin=self.TOP_MARGIN,
            bottomMargin=self.BOTTOM_MARGIN
        )

        # стиль для заголовков
        title_style = ParagraphStyle(
            name="title",
            fontName="TimesNewRoman",
            fontSize=14,
            leading=21,
            alignment=TA_CENTER,
            textColor=(0, 0, 0)
        )

        # стиль для основного текста
        normal_style = ParagraphStyle(
            name="normal",
            fontName="TimesNewRoman",
            fontSize=12,
            leading=18,
            firstLineIndent=self.FIRST_LINE_INDENT,
            alignment=TA_JUSTIFY
        )

        elements = []

        # титульник
        elements.append(Spacer(1, self.mm_to_pt(90)))
        elements.append(Paragraph("ОТЧЕТ ПО ЭКОЛОГИЧЕСКОЙ БЕЗОПАСНОСТИ", title_style))
        elements.append(Paragraph("ДРЕНАЖНЫХ СИСТЕМ", title_style))
        elements.append(Paragraph(f"ЗА {user_data.get('YEAR', '')} ГОД", title_style))
        elements.append(PageBreak())

        # разделы
        content_file = os.path.join(self.BASE_DIR, "report_module", "content.txt")

        if os.path.exists(content_file):
            with open(content_file, "r", encoding="utf-8") as f:
                sections = [line.strip() for line in f if line.strip()]

            for i, section in enumerate(sections, 1):
                section_file = os.path.join(self.BASE_DIR, "report_module", f"section_{i}.txt")
                elements.extend(
                    self.read_section(section_file, title_style, normal_style, user_data)
                )
                elements.append(PageBreak())

        doc.build(
            elements,
            onFirstPage=lambda c, d: self.header_footer_title(
                c, d,
                user_data["FULL_OBJECT_NAME"],
                user_data["SHORT_OBJECT_NAME"]
            ),
            onLaterPages=self.header_footer_main
        )

        buffer.seek(0)
        return buffer.getvalue()