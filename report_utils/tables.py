from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from datetime import date


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



def monitored_points_table(points: list,
                           fontname: str = "TimesNewRoman", fontsize: int = 14) -> Table:
    """Создает таблицу "Координаты точек наблюдения" (Таблица 2 из макета)
    Параметры:
        points: список точек наблюдения в формате [(Имя, Широта, Долгота, Тип среды, Описание), ...]
        fontname: str - Имя шрифта, зарегистрированного в ReportLab (для генерации отчета необохдимо зарегистрировать шрифт с кириллицей!!!)
        fontsize: int - размер шрифта
    Возвращает: ReportLab объект Table для включения в pdf отчет"""
    par_style: ParagraphStyle = get_paragraph_style(fontname, fontsize)
    par_style_justify: ParagraphStyle = get_paragraph_style(fontname, fontsize, TA_JUSTIFY)
    header = ("№", Paragraph("Точка наблюдения", par_style), "Широта", "Долгота", "Тип среды", "Описание")
    data = [header,]
    for i in range(len(points)):
        point = points[i]
        data.append((i+1, Paragraph(point[0], par_style), round(point[1], 7), round(point[2], 7), Paragraph(point[3], par_style), Paragraph(point[4], par_style_justify)))
    col_widths = [inch * 0.5, inch * 1.5, inch * 1, inch * 1, inch * 2]
    return Table(data, col_widths, style=get_table_style(fontname=fontname, fontsize=fontsize))


def lab_test_results_table(ph: float, iron: float, mn: float, no3: float, so4: float,
                           fontname: str = "TimesNewRoman", fontsize: int = 14) -> Table:
    """Создает таблицу "Результаты лабораторных анализов" (Таблица 3 из макета)
    Параметры:
        ph: float - pH
        iron: float - Железо
        mn: float - Марганец
        no3: float - Нитраты
        so4: float - Сульфаты
        fontname: str - Имя шрифта, зарегистрированного в ReportLab (для генерации отчета необохдимо зарегистрировать шрифт с кириллицей!!!)
        fontsize: int - размер шрифта
    Возвращает: ReportLab объект Table для включения в pdf отчет"""
    par_style: ParagraphStyle = get_paragraph_style(fontname, fontsize)
    par_style_justify: ParagraphStyle = get_paragraph_style(fontname, fontsize, TA_JUSTIFY)
    header = ("Показатель", "Норматив", "Результат", "Ед. изм.", "Соответствие")
    relative_error = 0.2
    data = [header,
            ("pH", "6-9", round(ph, 2), "-", "Соответсвует" if 6 <= ph <= 9 else "Не соответствует"),
            ("Железо", 0.3, round(iron, 2), "мг/л", "Соответсвует" if abs(iron - 0.3)/0.3 <= relative_error else "Не соответствует"),
            ("Марганец", 0.1, round(mn, 2), "мг/л", "Соответсвует" if abs(mn - 0.1)/0.1 <= relative_error else "Не соответствует"),
            ("Нитраты", 45, round(no3, 2), "мг/л", "Соответсвует" if abs(no3 - 45)/45 <= relative_error else "Не соответствует"),
            ("Сульфаты", 500, round(so4, 2), "мг/л", "Соответсвует" if abs(so4 - 500)/500 <= relative_error else "Не соответствует"),
            ]
    col_widths = [inch * 1, inch * 1, inch * 1.5, inch * 0.8, inch * 2]
    return Table(data, col_widths, style=get_table_style(fontname=fontname, fontsize=fontsize))


def lab_dynamics(entries: list[tuple],
                 fontname: str = "TimesNewRoman", fontsize: int = 14) -> Table:
    """Создает таблицу "Таблица динамики наблюдений" (Таблица 4 из макета)
    Параметры:
        entries: list - надор наблюдений в виде списка кортежей вида:
            date: Date - дата наблюдения в виде объекта date из datetime
            ph: float - pH
            iron: float - Железо
            mn: float - Марганец
            no3: float - Нитраты
            so4: float - Сульфаты
        fontname: str - Имя шрифта, зарегистрированного в ReportLab (для генерации отчета необохдимо зарегистрировать шрифт с кириллицей!!!)
        fontsize: int - размер шрифта
    Возвращает: ReportLab объект Table для включения в pdf отчет"""
    header = ("Дата", "pH", "Железо", "Марганец", "Нитраты", "Сульфаты")
    data = [header,]
    for i in range(len(entries)):
        entry = entries[i]
        date_i: date = entry[0]
        data.append((date_i.strftime("%d.%m.%Y"), round(entry[1], 2), round(entry[2], 2), round(entry[3], 2), round(entry[4], 2), round(entry[5], 2)))
    col_widths = [inch * 1, inch * 1.2, inch * 1.2, inch * 1.2, inch * 1.2, inch * 1.2]
    return Table(data, col_widths, style=get_table_style(fontname=fontname, fontsize=fontsize))


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
