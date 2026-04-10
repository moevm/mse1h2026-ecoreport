from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from datetime import date


def get_unified_table_style(fontname: str = "TimesNewRoman", fontsize: int = 12) -> TableStyle:
    """Гнуфициранный стиль для всех таблиц отчёта.
    
    Параметры:
        fontname: str - Имя шрифта
        fontsize: int - размер шрифта
    Возвращает: TableStyle объект"""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),  # серый в заголовке
        ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),  # чёрный текст всюду
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # центровка
        ('FONTNAME', (0, 0), (-1, -1), fontname),
        ('FONTSIZE', (0, 0), (-1, -1), fontsize),
        ('GRID', (0, 0), (-1, -1), 0.8, (0, 0, 0)),  # границы
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # вертикальная центровка
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ])


def get_unified_paragraph_style(fontname: str = "TimesNewRoman", fontsize: int = 12, 
                                 alignment=TA_CENTER, firstLineIndent: int = 0) -> ParagraphStyle:
    """Неути для таблиц
    
    Параметры:
        fontname: str - Имя шрифта
        fontsize: int - размер шрифта
        alignment - выравнивание
        firstLineIndent: int - отступ первой строки"""
    return ParagraphStyle(
        name='table_unified',
        fontName=fontname,
        fontSize=fontsize,
        alignment=alignment,
        textColor=(0, 0, 0),
        firstLineIndent=firstLineIndent
    )


def get_table_style(fontname: str = "TimesNewRoman", fontsize: int = 14) -> TableStyle:
    """Создает объект стиля таблицы для вставки в PDF отчет.

    Параметры:
        fontname: str - Имя шрифта, зарегистрированного в ReportLab (для генерации отчета необохдимо зарегистрировать шрифт с кириллицей!!!)
        fontsize: int - размер шрифта"""
    style_params = [("FONT", (0, 0), (-1, -1), fontname, fontsize),
                    ("ALIGN", (0, 0), (-1, -1), "CENTRE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, (0, 0, 0)),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]
    return TableStyle(style_params)


def get_paragraph_style(fontname: str = "TimesNewRoman", fontsize: int = 14, alignment=TA_CENTER):
    """Создает объект стиля параграфа для вставки в таблицу.

    Параметры:
        fontname: str - Имя шрифта, зарегистрированного в ReportLab (для генерации отчета необохдимо зарегистрировать шрифт с кириллицей!!!)
        fontsize: int - размер шрифта
        alignment - режим выравнивания текста (TA_CENTER, TA_JUSTIFY... из reportlab.lib.enums)"""
    style = ParagraphStyle("TableText")
    style.alignment = alignment
    style.fontName = fontname
    style.fontSize = fontsize
    return style


def main_system_specifications_table(system_type: str, pipe_material: str, pipe_diameter: float,
                                     laying_depth: float, total_length: float, year_commissioned: int, well_count: int,
                                     note_system_type: str = "", note_pipe_material: str = "",
                                     note_pipe_diameter: str = "",
                                     note_laying_depth: str = "", note_total_length: str = "",
                                     note_year_commissioned: str = "", note_well_count: str = "",
                                     fontname: str = "TimesNewRoman", fontsize: int = 14) -> Table:
    """Создает таблицу "Основные характеристики системы" (Таблица 1 из макета)
    Параметры:
        system_type: str - Тип дренажной системы
        pipe_material: str - материал труб
        pipe_diameter: float - Диаметр труб
        laying_depth: float - Глубина заложения
        total_length: float - Общая протяженность
        year_commissioned: int - Год ввода в эксплуатацию
        well_count: int - Количество колодцев
        для каждого из полей выше есть note_{параметр}, который содержит примечание (опционально, по умолчанию пустая строка)
        fontname: str - Имя шрифта, зарегистрированного в ReportLab (для генерации отчета необохдимо зарегистрировать шрифт с кириллицей!!!)
        fontsize: int - размер шрифта
    Возвращает: ReportLab объект Table для включения в pdf отчет"""
    par_style: ParagraphStyle = get_paragraph_style(fontname, fontsize)
    par_style_justify: ParagraphStyle = get_paragraph_style(fontname, fontsize, TA_JUSTIFY)
    header = ("Параметр", "Значение", Paragraph("Единицы измерения", style=par_style), "Примечание")
    data = (header,
            (Paragraph("Тип дренажной системы", style=par_style), Paragraph(system_type, style=par_style), "-",
             Paragraph(note_system_type, style=par_style_justify)),
            (Paragraph("Материал труб", style=par_style), Paragraph(pipe_material, style=par_style), "-",
             note_pipe_material),
            (Paragraph("Диаметр труб", style=par_style), pipe_diameter, "мм", note_pipe_diameter),
            (Paragraph("Глубина заложения", style=par_style), laying_depth, "м", note_laying_depth),
            (Paragraph("Общая протяженность", style=par_style), total_length, "м", note_total_length),
            (Paragraph("Год ввода в эксплуатацию", style=par_style), year_commissioned, "-", note_year_commissioned),
            (Paragraph("Количество колодцев", style=par_style), well_count, "шт", note_well_count),
            )
    col_widths = [inch * 1.5, inch * 1.7, inch * 1.1, inch * 3]
    if not any((note_system_type, note_well_count, note_pipe_diameter,
                note_pipe_material, note_total_length, note_laying_depth,
                note_year_commissioned)):
        data = tuple(line[:3] for line in data)
    return Table(data, col_widths, style=get_table_style(fontname=fontname, fontsize=fontsize))



def _parse_coordinate(value):
    if value is None or str(value).strip() == "":
        return "-"
    try:
        return round(float(str(value).replace(",", ".")), 7)
    except (ValueError, TypeError):
        return str(value)


def monitored_points_table(points: list,
                           fontname: str = "TimesNewRoman", fontsize: int = 12) -> Table:
    """Создает таблицу "Координаты точек наблюдения" (Таблица 2 из макета)
    Параметры:
        points: список точек наблюдения в формате [(Имя, Широта, Долгота, Тип среды, Описание), ...]
        fontname: str - Имя шрифта, зарегистрированного в ReportLab (для генерации отчета необохдимо зарегистрировать шрифт с кириллицей!!!)
        fontsize: int - размер шрифта
    Возвращает: ReportLab объект Table для включения в pdf отчет"""
    header_style = get_unified_paragraph_style(fontname, fontsize, alignment=TA_CENTER, firstLineIndent=0)
    cell_style = get_unified_paragraph_style(fontname, fontsize, alignment=TA_CENTER, firstLineIndent=0)
    
    header = [
        Paragraph("№", header_style),
        Paragraph("Точка наблюдения", header_style),
        Paragraph("Широта", header_style),
        Paragraph("Долгота", header_style),
        Paragraph("Тип среды", header_style),
        Paragraph("Описание", header_style)
    ]
    
    data = [header]
    for i, point in enumerate(points):
        latitude = _parse_coordinate(point[1])
        longitude = _parse_coordinate(point[2])
        data.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(str(point[0]), cell_style),
            Paragraph(str(latitude), cell_style),
            Paragraph(str(longitude), cell_style),
            Paragraph(str(point[3]), cell_style),
            Paragraph(str(point[4]), cell_style)
        ])
    
    col_widths = [inch * 0.5, inch * 1.3, inch * 1.2, inch * 1.2, inch * 1.3]
    return Table(data, col_widths, style=get_unified_table_style(fontname=fontname, fontsize=fontsize))


def lab_test_results_table(results: list, fontname: str = "TimesNewRoman", fontsize: int = 12) -> Table:
    """Создает таблицу "Результаты лабораторных анализов" (Таблица 3 из макета)
    Параметры:
        results: list - список результатов в формате [{"indicator": "pH", "standard": "6-9", "result": 7.2, "unit": "-", "compliance": "да"}, ...]
        fontname: str - Имя шрифта
        fontsize: int - размер шрифта
    Возвращает: ReportLab объект Table для включения в pdf отчет"""
    header_style = get_unified_paragraph_style(fontname, fontsize, alignment=TA_CENTER, firstLineIndent=0)
    cell_style = get_unified_paragraph_style(fontname, fontsize, alignment=TA_CENTER, firstLineIndent=0)
    
    header = [
        Paragraph("Показатель", header_style),
        Paragraph("Норматив", header_style),
        Paragraph("Результат", header_style),
        Paragraph("Единицы измерения", header_style),
        Paragraph("Соответствие", header_style)
    ]
    
    data = [header]
    for result in results:
        indicator = str(result.get("indicator", ""))
        standard = str(result.get("standard", ""))
        result_val = str(result.get("result", ""))
        unit = str(result.get("unit", "-"))
        compliance = str(result.get("compliance", ""))
        
        data.append([
            Paragraph(indicator, cell_style),
            Paragraph(standard, cell_style),
            Paragraph(result_val, cell_style),
            Paragraph(unit, cell_style),
            Paragraph(compliance, cell_style)
        ])
    
    col_widths = [inch * 1.3, inch * 1.1, inch * 1.1, inch * 1.2, inch * 1.3]
    return Table(data, col_widths, style=get_unified_table_style(fontname=fontname, fontsize=fontsize))


def observation_dynamics_table(dynamics: list, fontname: str = "TimesNewRoman", fontsize: int = 12) -> Table:
    """Создает таблицу "Таблица динамики наблюдений" (Таблица 4 из макета)
    Параметры:
        dynamics: list - список наблюдений в формате [{"date": "01.01.2026", "pH": 7.2, "iron": 0.2, ...}, ...]
        fontname: str - Имя шрифта
        fontsize: int - размер шрифта
    Возвращает: ReportLab объект Table для включения в pdf отчет"""
    header_style = get_unified_paragraph_style(fontname, fontsize, alignment=TA_CENTER, firstLineIndent=0)
    cell_style = get_unified_paragraph_style(fontname, fontsize, alignment=TA_CENTER, firstLineIndent=0)

    metric_order = [
        ("pH", "pH"),
        ("iron", "Железо"),
        ("manganese", "Марганец"),
        ("nitrates", "Нитраты"),
        ("sulfates", "Сульфаты")
    ]

    def to_simple_dict(item):
        if hasattr(item, "model_dump"):
            return item.model_dump(exclude_unset=True, exclude_none=True)
        if hasattr(item, "dict"):
            try:
                return item.dict(exclude_unset=True, exclude_none=True)
            except TypeError:
                return item.dict()
        if isinstance(item, dict):
            return {k: v for k, v in item.items() if v is not None}
        return dict(item)

    simple_dynamics = [to_simple_dict(entry) for entry in dynamics]

    selected_metrics = [
        metric for metric, label in metric_order
        if any(metric in entry for entry in simple_dynamics)
    ]

    columns = [("date", "Дата")] + [(metric, label) for metric, label in metric_order if metric in selected_metrics]

    header = [Paragraph(label, header_style) for _, label in columns]

    data = [header]
    for entry in simple_dynamics:
        row = []
        for key, _ in columns:
            if key == "date":
                value = str(entry.get("date", ""))
            else:
                value = str(entry.get(key, ""))
            row.append(Paragraph(value, cell_style))
        data.append(row)

    col_widths = [inch * 1.0] + [inch * 1.1 for _ in selected_metrics]
    return Table(data, col_widths, style=get_unified_table_style(fontname=fontname, fontsize=fontsize))


if __name__ == "__main__":
    #Пример создания таблицы
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    doc = SimpleDocTemplate("table_test.pdf")
    #Необходимо зарегистрировать шрифт с кириллицей для корректного отображения, иначе будут черные квадраты!
    pdfmetrics.registerFont(TTFont("TimesNewRoman", "times-new-roman-regular.ttf"))
    table1 = main_system_specifications_table("Какая-то дренажная система", "Какой-то материал труб", 100, 100, 1000, 2026, 1,
                                              note_system_type="Здесь может быть примечание, если ни в одной строке примечаний нет, то столбец удаляется")

    points = [("Точка 1", 0.1111111, 0.1111111, "Дренажная вода", "Контрольная точка"),
              ("Точка 2", 0.1111111, 0.1111111, "Дренажная вода", "Контрольная точка")]
    table2 = monitored_points_table(points)

    table3 = lab_test_results_table(7, 0.2, 0.11, 50, 489)

    entries = [(date.today(), 1, 1, 1, 1, 1),
               (date.today(), 2, 2, 2, 2, 2)]
    table4 = lab_dynamics(entries)

    doc.build([table1, table2, table3, table4])
