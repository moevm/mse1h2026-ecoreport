from reportlab.platypus import Image
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter, date2num
from io import BytesIO
import numpy as np
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfutils import readJPEGInfo
from datetime import datetime, date

# форматирование числовых значений для таблиц
def format_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0

def create_image_through_buffer(figure: plt.Figure) -> Image:
    """Сохраняет фигуру matplotlib в буфер и считывает его для создания ReportLab.platypus.Image"""
    image = BytesIO()
    figure.savefig(image, format="jpg")
    image.seek(0)
    info = readJPEGInfo(image)
    imageWidth = info[0]
    imageHeight = info[1]
    proportions = imageHeight / imageWidth
    return Image(image, width=inch*5.5, height=inch*5.5*proportions)


def concentration_dynamics_lineplot(results: list[dict], dynamics: list[dict], metric: str):
    """
    Создает график динамики измерения по датам для вставки в pdf отчет.

    Параметры:
        dynamics: list[dict] - Набор измерений
        dates: list[date] - Набор дат измерений
        label: str - Заголовок для оси измерений
        norm: float - Значение норматива (если линию рисовать не нужно, оставить как 0)
    Возвращает:
        Объект ReportLab.platypus.Image для включения в pdf отчет
    """

    metric_labels = dict([
        ("pH", "pH"),
        ("iron", "Железо"),
        ("manganese", "Марганец"),
        ("nitrates", "Нитраты"),
        ("sulfates", "Сульфаты")
    ])

    selected_metric_label = metric_labels.get(metric, "")

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

    if all(metric not in entry for entry in simple_dynamics):
        return None

    measurements, dates = list(), list()
    standard = ""
    low_bound, high_bound = 0, 0
    unit = ""

    for result in results:
        indicator = str(result.get("indicator", ""))
        if indicator.lower() == selected_metric_label.lower():
            standard = result.get("standard", "")
            low_bound, high_bound = 0, 0
            if standard:
                low_bound, high_bound = map(format_number, standard.split(' - '))
            unit = str(result.get("unit", ""))


    for entry in simple_dynamics:
        row = []
        date = entry.get("date", "")
        if not date:
            continue
        date = datetime.strptime(date, "%Y-%m-%d")
        value = format_number(entry.get(metric,"-1"))
        if value <= 0:
            continue
        measurements.append(value)
        dates.append(date2num(date))

    if len(dates) == 0 or len(measurements) == 0:
        return

    zipped = list(zip(dates, measurements))
    zipped.sort()
    dates, measurements = list(zip(*zipped))

    fig, ax = plt.subplots()
    fig.tight_layout()
    ax.plot(dates, measurements, color='blue', marker='o', label="Динамика наблюдений")
    if low_bound != 0:
        ax.hlines(low_bound, 0, 1, colors='#4CBA76', transform=ax.get_yaxis_transform(), label="Нижняя граница нормы")
    if high_bound != 0:
        ax.hlines(high_bound, 0, 1, colors='#618071', transform=ax.get_yaxis_transform(), label="Верхняя граница нормы")

    ax.xaxis.set_major_formatter(ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.grid(True)
    if metric:
        ax.set_ylabel(f"{selected_metric_label}, {unit}" if unit not in "-" else selected_metric_label)
    ax.legend()

    return create_image_through_buffer(fig)


def comparison_bar_chart(results: list[dict]) -> Image:
    """
    Создает столбчатый график измерений концентрации для вставки в pdf отчет.

    Параметры:
        iron: float - Железо
        mn: float - Марганец
        no3: float - Нитраты
        so4: float - Сульфаты
        norm_iron: float - Норматив железа
        norm_mn: float - Норматив марганца
        norm_no3: float - Норматив нитратов
        norm_so4: float - Норматив сульфатов
    Возвращает:
        Объект ReportLab.platypus.Image для включения в pdf отчет
    """
    measurements = list()
    measure_data = {
        "Нижняя граница нормы": list(),
        "Результат наблюдения": list(),
        "Верхняя граница нормы": list()
    }

    for result in results:
        indicator = str(result.get("indicator", ""))
        standard = result.get("standard", "")
        low_bound, high_bound = 0, 0
        if standard:
            low_bound, high_bound = map(format_number, standard.split(' - '))
        result_val = format_number(result.get("result", ""))
        unit = str(result.get("unit", ""))
        measurements.append(f"{indicator}, {unit}" if unit not in "-" else indicator)
        measure_data["Результат наблюдения"].append(result_val)
        measure_data["Нижняя граница нормы"].append(low_bound)
        measure_data["Верхняя граница нормы"].append(high_bound)


    fig, ax = plt.subplots()
    fig.tight_layout()
    x = np.arange(len(measurements))
    width = 0.25
    multiplier = 0
    #Чтобы большая разница между разными показателями не приводила к очень маленьким столбцам на графике
    ax.set_yscale('log')

    for attribute, measurement in measure_data.items():
        offset = width * multiplier
        if attribute == "Результат наблюдения":
            color = "#14824E"
        elif attribute == "Верхняя граница нормы":
            color = "#618071"
        else:
            color = "#4CBA76"
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=2)
        multiplier += 1

    ax.legend(loc='best')
    ax.set_xticks(x + width, measurements)
    ax.tick_params(right=False, left=False, axis='y', length=0, which='both')
    ax.set_yticks([])
    #fig.set_figwidth(6)

    return create_image_through_buffer(fig)


if __name__ == "__main__":
    #Пример создания графа
    from reportlab.platypus import SimpleDocTemplate
    from random import randint, random

    doc = SimpleDocTemplate("graph_test.pdf")

    dates, measurements = list(), list()
    for i in range(1,10):
        measure = randint(2,8) + random()
        day = date(2026,1,i)
        dates.append(day)
        measurements.append(measure)

    plot = concentration_dynamics_lineplot(measurements, dates, label="Марганец, мг/л", norm=5.0)
    chart = comparison_bar_chart(1, 1, 50, 390)

    doc.build([plot, chart])
