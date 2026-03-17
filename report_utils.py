from reportlab.platypus import Image
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter, date2num
from io import BytesIO


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

    doc.build([plot])
