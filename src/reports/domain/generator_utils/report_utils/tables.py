from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime, date

# преобразование даты из формата YYYY-MM-DD в DD.MM.YYYY
def format_date(value):
    try:
        if isinstance(value, (datetime, date)):
            return value.strftime("%d.%m.%Y")
        # если строка типа 2026-04-03
        dt = datetime.strptime(str(value), "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return str(value)

# создание стиля для всех таблиц отчёта
def get_unified_table_style(fontname: str = "TimesNewRoman", fontsize: int = 12) -> TableStyle:
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),  # серый в заголовке
        ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),        # чёрный текст всюду
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),             # горизонтальное выравнивание
        ('FONTNAME', (0, 0), (-1, -1), fontname),          # шрифт для всей таблицы
        ('FONTSIZE', (0, 0), (-1, -1), fontsize),          # размер шрифта для всей таблицы
        ('GRID', (0, 0), (-1, -1), 0.8, (0, 0, 0)),        # толщина границ
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),            # вертикальное выравнивание
        ('LEFTPADDING', (0, 0), (-1, -1), 6),              # отступы внутри ячеек слева
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),             # отступы внутри ячеек справа
        ('TOPPADDING', (0, 0), (-1, -1), 4),               # отступы внутри ячеек сверху
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),            # отступы внутри ячеек снизу
    ])

# создание стиля для всех параграфов в таблицах отчёта
def get_unified_paragraph_style(fontname: str = "TimesNewRoman", fontsize: int = 12, alignment=TA_CENTER, firstLineIndent: int = 0) -> ParagraphStyle:
    return ParagraphStyle(
        name='table_unified',
        fontName=fontname,
        fontSize=fontsize,
        alignment=alignment,
        textColor=(0, 0, 0),
        firstLineIndent=firstLineIndent
    )
# создание стиля для параграфов в таблицах отчёта
def get_paragraph_style(fontname: str = "TimesNewRoman", fontsize: int = 14, alignment=TA_CENTER):
    style = ParagraphStyle("TableText")
    style.alignment = alignment
    style.fontName = fontname
    style.fontSize = fontsize
    return style

# создание таблицы "Основные характеристики системы"
def main_system_specifications_table(system_type: str, pipe_material: str, pipe_diameter: float,
                                     laying_depth: float, total_length: float, year_commissioned: int, well_count: int,
                                     note_system_type: str = "", note_pipe_material: str = "",
                                     note_pipe_diameter: str = "",
                                     note_laying_depth: str = "", note_total_length: str = "",
                                     note_year_commissioned: str = "", note_well_count: str = "",
                                     fontname: str = "TimesNewRoman", fontsize: int = 14) -> Table:
    
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
    return Table(data, col_widths, style=get_unified_table_style(fontname=fontname, fontsize=fontsize))

# форматирование координат для таблицы "Координаты точек наблюдения"
def _parse_coordinate(value):
    if value is None or str(value).strip() == "":
        return "-"
    try:
        return round(float(str(value).replace(",", ".")), 7)
    except (ValueError, TypeError):
        return str(value)

# создание таблицы "Координаты точек наблюдения"
def monitored_points_table(points: list, fontname: str = "TimesNewRoman", fontsize: int = 12) -> Table:
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

# форматирование числовых значений для таблиц
def format_number(value):
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""

# создание таблицы "Результаты лабораторных анализов"
def lab_test_results_table(results: list, fontname: str = "TimesNewRoman", fontsize: int = 12) -> Table:
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
        result_val = format_number(result.get("result", ""))
        unit = str(result.get("unit", "-"))
        compliance = str(result.get("compliance", ""))
        
        data.append([
            Paragraph(indicator, cell_style),
            Paragraph(standard, cell_style),
            Paragraph(result_val, cell_style),
            Paragraph(unit, cell_style),
            Paragraph(compliance, cell_style)
        ])
    
    col_widths = [inch * 1.1, inch * 1.6, inch * 1.0, inch * 1.2, inch * 1.1]
    return Table(data, col_widths, style=get_unified_table_style(fontname=fontname, fontsize=fontsize))

# множество числовых полей для динамики наблюдений
NUMERIC_FIELDS = {"pH", "iron", "manganese", "nitrates", "sulfates"} # 

# создание таблицы "Таблица динамики наблюдений"
def observation_dynamics_table(dynamics: list, fontname: str = "TimesNewRoman", fontsize: int = 12) -> Table:
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
                value = format_date(entry.get("date", ""))
            
            elif key in NUMERIC_FIELDS:
                value = format_number(entry.get(key, ""))
            
            else:
                value = str(entry.get(key, ""))
            
            row.append(Paragraph(value, cell_style))
        data.append(row)

    col_widths = [inch * 1.0] + [inch * 1.1 for _ in selected_metrics]
    return Table(data, col_widths, style=get_unified_table_style(fontname=fontname, fontsize=fontsize))
