"""
Скрипт генерации примеров файлов CSV и XLSX для тестирования импорта.

CSV  — вертикальный формат (несколько строк):
  Строка 1 (первая строка данных): все скалярные поля + DOCUMENTS_GOST +
    первая точка наблюдения (OP_POINT, OP_LATITUDE, ...) +
    первая запись динамики (DYN_DATE, DYN_PH, ...).
  Строки 2, 3, ... : скалярные поля пустые; заполнены только OP_* и DYN_*.

XLSX — многолистовой формат:
  Лист «Отчет»              — скалярные поля (без DOCUMENTS_GOST)
  Лист «ГОСТ»               — список выбранных нормативных документов (по одному на строку)
  Лист «Точки_наблюдения»   — таблица точек мониторинга
  Лист «Динамика»           — таблица динамики измерений
  (TEST_RESULTS реконструируется импортером из RESULTS_PH ... на листе «Отчет»)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd

SELECTED_GOSTS = [
    "ГОСТ Р 72274-2025",
    "ГОСТ 1811-2019",
    "СП 32.13330.2018",
]
OBSERVATION_POINTS = [
    {"observation_point": "ПН-1", "latitude": 59.952, "longitude": 30.321,
     "medium_type": "Дренажная вода", "description": "Точка контроля №1"},
    {"observation_point": "ПН-2", "latitude": 59.955, "longitude": 30.325,
     "medium_type": "Дренажная вода", "description": "Точка контроля №2"},
    {"observation_point": "ПН-3", "latitude": 59.948, "longitude": 30.318,
     "medium_type": "Дренажная вода", "description": "Точка контроля №3"},
]

DYNAMICS = [
    {"date": "2025-01-15", "pH": 7.10, "iron": 0.28, "manganese": 0.09, "nitrates": 11.50, "sulfates": 19.00},
    {"date": "2025-04-10", "pH": 7.20, "iron": 0.25, "manganese": 0.07, "nitrates": 12.00, "sulfates": 20.00},
    {"date": "2025-07-05", "pH": 7.15, "iron": 0.22, "manganese": 0.08, "nitrates": 11.80, "sulfates": 18.50},
]
SCALAR_FIELDS = {
    "FULL_OBJECT_NAME": "Дренажная система промышленного предприятия г. Санкт-Петербург",
    "SHORT_OBJECT_NAME": "Дренаж СПб",
    "YEAR": 2025,
    "ORGANIZATION_NAME": "ООО ЭкоМониторинг",
    "REGION": "Санкт-Петербург",
    "RELIEF_TYPE": "Равнинный",
    "SOIL_TYPE": "Суглинок",
    "GROUNDWATER_LEVEL": "1.50",
    "CLIMATE_ZONE": "умеренный континентальный",
    "COORDINATES_LATITUDE": 59.95,
    "COORDINATES_LONGITUDE": 30.32,
    "OBJECT_TYPE": "промышленный объект",
    "SYSTEM_TYPE": "горизонтальный",
    "PIPE_MATERIAL": "ПВХ",
    "PIPE_DIAMETER": "110.00",
    "PIPE_DEPTH": "2.00",
    "PIPE_LENGTH": "750.00",
    "PIPE_INSTALL_YEAR": 2018,
    "MANHOLE_COUNT": 8,
    "MONITORING_POINT_COUNT": 3,
    "OBSERVATION_FREQUENCY": "Ежеквартально",
    "RESULTS_PH": 7.20,
    "RESULTS_IRON": 0.25,
    "RESULTS_MANGANESE": 0.07,
    "RESULTS_NITRATES": 12.00,
    "RESULTS_SULFATES": 20.00,
    "ORGANIZATION_ADDRESS": "г. Санкт-Петербург, ул. Экологическая, д. 10",
    "ORGANIZATION_PHONE": "+7 (812) 555-12-34",
    "ORGANIZATION_EMAIL": "info@ecomonitoring.ru",
    "RESPONSIBLE_NAME": "Петров П.П.",
    "RESPONSIBLE_POSITION": "Главный эколог",
    "REPORT_DATE": "2025-06-01",
}

out_dir = os.path.dirname(os.path.abspath(__file__))


def build_csv_rows() -> list:
    n_rows = max(len(OBSERVATION_POINTS), len(DYNAMICS), len(SELECTED_GOSTS))
    rows = []
    for i in range(n_rows):
        row: dict = {}
        if i == 0:
            row.update(SCALAR_FIELDS)
        if i < len(SELECTED_GOSTS):
            row["DOCUMENTS_GOST"] = SELECTED_GOSTS[i]
        if i < len(OBSERVATION_POINTS):
            pt = OBSERVATION_POINTS[i]
            row["OP_POINT"] = pt["observation_point"]
            row["OP_LATITUDE"] = pt["latitude"]
            row["OP_LONGITUDE"] = pt["longitude"]
            row["OP_MEDIUM_TYPE"] = pt["medium_type"]
            row["OP_DESCRIPTION"] = pt["description"]
        if i < len(DYNAMICS):
            dyn = DYNAMICS[i]
            row["DYN_DATE"] = dyn["date"]
            row["DYN_PH"] = dyn["pH"]
            row["DYN_IRON"] = dyn["iron"]
            row["DYN_MANGANESE"] = dyn["manganese"]
            row["DYN_NITRATES"] = dyn["nitrates"]
            row["DYN_SULFATES"] = dyn["sulfates"]
        rows.append(row)
    return rows


csv_path = os.path.join(out_dir, "example_report.csv")
pd.DataFrame(build_csv_rows()).to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"CSV: {csv_path}")
print(f"  Строк данных: {max(len(OBSERVATION_POINTS), len(DYNAMICS))}")
print(f"  DOCUMENTS_GOST = '{','.join(SELECTED_GOSTS)}'")

xlsx_path = os.path.join(out_dir, "example_report.xlsx")

df_main = pd.DataFrame([SCALAR_FIELDS])
df_gost = pd.DataFrame({"name": SELECTED_GOSTS})
df_points = pd.DataFrame(OBSERVATION_POINTS)
df_dynamic = pd.DataFrame(DYNAMICS)

with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
    df_main.to_excel(writer, sheet_name="Отчет", index=False)
    df_gost.to_excel(writer, sheet_name="ГОСТ", index=False)
    df_points.to_excel(writer, sheet_name="Точки_наблюдения", index=False)
    df_dynamic.to_excel(writer, sheet_name="Динамика", index=False)

print(f"XLSX (многолистовой): {xlsx_path}")
print("  Листы: Отчет | ГОСТ | Точки_наблюдения | Динамика")
print(f"  ГОСТ ({len(SELECTED_GOSTS)} шт.): {SELECTED_GOSTS}")

xlsx_single_path = os.path.join(out_dir, "example_report_single.xlsx")

with pd.ExcelWriter(xlsx_single_path, engine="openpyxl") as writer:
    pd.DataFrame(build_csv_rows()).to_excel(writer, sheet_name="Отчет", index=False)

print(f"XLSX (одно-листовой): {xlsx_single_path}")
print(f"  Строк данных: {max(len(OBSERVATION_POINTS), len(DYNAMICS))}")
print(f"  DOCUMENTS_GOST = '{','.join(SELECTED_GOSTS)}'")
