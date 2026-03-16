from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch


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


if __name__ == "__main__":
    #Пример создания таблицы
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    doc = SimpleDocTemplate("table_test.pdf")
    #Необходимо зарегистрировать шрифт с кириллицей для корректного отображения, иначе будут черные квадраты!
    pdfmetrics.registerFont(TTFont("TimesNewRoman", "times-new-roman-regular.ttf"))
    elements = [main_system_specifications_table("Какая-то дренажная система", "Какой-то материал труб", 100, 100, 1000, 2026, 1,
                                                 note_system_type="Здесь может быть примечание, если ни в одной строке примечаний нет, то столбец удаляется")]
    doc.build(elements)
