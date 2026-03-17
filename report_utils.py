from reportlab.platypus import Image
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter, date2num
from io import BytesIO
import numpy as np


def create_image_through_buffer(figure: plt.Figure) -> Image:
    """Сохраняет фигуру matplotlib в буфер и считывает его для создания ReportLab.platypus.Image"""
    image = BytesIO()
    figure.savefig(image, format="png")
    image.seek(0)
    return Image(image)


def concentration_dynamics_lineplot(measurements: list[float], dates: list[date], label: str = "", norm: float = 0) -> Image:
    """
    Создает график динамики измерения по датам для вставки в pdf отчет.

    Параметры:
        measurements: list[float] - Набор измерений
        dates: list[date] - Набор дат измерений
        label: str - Заголовок для оси измерений
        norm: float - Значение норматива (если линию рисовать не нужно, оставить как 0)
    Возвращает:
        Объект ReportLab.platypus.Image для включения в pdf отчет
    """
    dates_plt = list(map(date2num, dates))
    fig, ax = plt.subplots()
    ax.plot(dates_plt, measurements, color='blue', marker='o', label="Динамика наблюдений")
    if norm != 0:
        ax.hlines(norm, 0, 1, colors='g', transform=ax.get_yaxis_transform(), label="Норматив")
    ax.xaxis.set_major_formatter(ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.grid(True)
    if label:
        ax.set_ylabel(label)
    ax.legend()
    fig.set_figwidth(6)

    return create_image_through_buffer(fig)


def comparison_bar_chart(iron: float, mn: float, no3: float, so4: float,
                         norm_iron: float = 0.3, norm_mn: float = 0.1, norm_no3: float = 45, norm_so4: float = 500) -> Image:
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
    fig, ax = plt.subplots()
    measurements = ("Железо", "Марганец", "Нитраты", "Сульфаты")
    measure_data = {
        "Результат наблюдения": (iron, mn, no3, so4),
        "Норматив": (norm_iron, norm_mn, norm_no3, norm_so4)
    }
    x = np.arange(len(measurements))
    width = 0.25
    multiplier = 0
    #Чтобы большая разница между разными показателями не приводила к очень маленьким столбцам на графике
    ax.set_yscale('log')

    for attribute, measurement in measure_data.items():
        offset = width * multiplier
        color = "gray" if attribute == "Результат наблюдения" else "green"
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=2)
        multiplier += 1

    ax.set_ylabel('Концентрация, мг/л')
    ax.legend(loc='upper left')
    ax.set_xticks(x + width, measurements)
    ax.tick_params(right=False, left=False, axis='y', length=0, which='both')
    fig.set_figwidth(6)

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
