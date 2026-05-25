import json
import math
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Tuple

import pandas as pd

from reports.schemas.report_models import ReportInputData

_COMPLEX_FIELDS = [
    "DOCUMENTS_GOST",
    "RESULTS_DYNAMIC",
    "OBSERVATION_POINTS",
    "TEST_RESULTS",
    "OBSERVATION_DYNAMICS",
]


class Importer(ABC):
    """
    Базовый класс для импорта данных.

    Обеспечивает базовый интерфейс для загрузки данных и общую логику обработки
    сырых записей, включая парсинг JSON-строк во вложенных полях.
    """

    # Соответствие фиксированных показателей → скалярным полям модели и единицам измерения.
    # Используется при реконструкции TEST_RESULTS из плоских колонок RESULTS_PH и т.д.
    _TEST_INDICATORS: List[Tuple[str, str, str]] = [
        ("pH",       "RESULTS_PH",        "-"),
        ("Железо",   "RESULTS_IRON",      "мг/л"),
        ("Марганец", "RESULTS_MANGANESE", "мг/л"),
        ("Нитраты",  "RESULTS_NITRATES",  "мг/л"),
        ("Сульфаты", "RESULTS_SULFATES",  "мг/л"),
    ]

    _OP_FIELD_MAP: List[Tuple[str, str]] = [
        ("OP_POINT",       "observation_point"),
        ("OP_LATITUDE",    "latitude"),
        ("OP_LONGITUDE",   "longitude"),
        ("OP_MEDIUM_TYPE", "medium_type"),
        ("OP_DESCRIPTION", "description"),
    ]

    _DYN_FIELD_MAP: List[Tuple[str, str]] = [
        ("DYN_DATE",      "date"),
        ("DYN_PH",        "pH"),
        ("DYN_IRON",      "iron"),
        ("DYN_MANGANESE", "manganese"),
        ("DYN_NITRATES",  "nitrates"),
        ("DYN_SULFATES",  "sulfates"),
    ]

    def __init__(self, source: Any):
        """
        Инициализирует импортер источником данных.

        :param source: Источник данных (словарь/список для ManualImporter,
                       путь к файлу или файловый объект для CSV/XLSX).
        """
        self.source = source

    @abstractmethod
    def import_data(self) -> List[ReportInputData]:
        """
        Абстрактный метод для выполнения импорта данных.

        Должен быть реализован в подклассах.

        :return: Список провалидированных объектов ReportInputData.
        :raises NotImplementedError: Если метод не переопределен в подклассе.
        """
        pass

    @abstractmethod
    def _read_records(self) -> List[Dict[str, Any]]:
        """
        Абстрактный метод чтения сырых записей из источника.

        :return: Список словарей с необработанными данными.
        """
        pass

    def parse_form_data(self) -> List[Dict[str, Any]]:
        """
        Читает и очищает записи из источника
        Используется для предзаполнения формы: возвращает готовые словари,
        в которых убраны NaN-значения и раскрыты вложенные JSON-строки

        :return: Список очищенных словарей.
        """
        return [self._clean_record(rec) for rec in self._read_records()]

    def _process_records(self, records: List[Dict[str, Any]]) -> List[ReportInputData]:
        """
        Очищает записи и валидирует через Pydantic-модель ReportInputData.

        :param records: Список словарей с сырыми данными.
        :return: Список провалидированных объектов ReportInputData.
        """
        return [ReportInputData.model_validate(self._clean_record(rec)) for rec in records]

    @classmethod
    def _reconstruct_test_results(cls, record: Dict[str, Any]) -> None:
        """
        Строит TEST_RESULTS из скалярных полей RESULTS_PH, RESULTS_IRON и т.д.,
        если TEST_RESULTS ещё отсутствует в записи.

        Изменяет словарь record на месте.
        """
        if "TEST_RESULTS" in record:
            return
        test_results = []
        for indicator, field, unit in cls._TEST_INDICATORS:
            val = record.get(field)
            if val is not None and not (isinstance(val, float) and math.isnan(val)):
                test_results.append({
                    "indicator":  indicator,
                    "result":     val,
                    "unit":       unit,
                    "compliance": "",
                })
        if test_results:
            record["TEST_RESULTS"] = test_results

    @staticmethod
    def _normalize_date(val: Any) -> str:
        """
        Нормализует значение даты в строку формата ``YYYY-MM-DD``.

        Поддерживает:

        * ``pd.Timestamp`` / ``datetime.datetime`` / ``datetime.date`` — из Excel-ячеек.
        * Строки с разделителем ``"-"`` (``"2025-01-15"``, ``"15-01-2025"``).
        * Строки с разделителем ``"/"`` (``"15/01/2025"``, ``"2025/01/15"``).

        При неоднозначности (``DD/MM`` vs ``MM/DD``) предпочитается европейский
        порядок ``DD/MM`` (``dayfirst=True``).

        :param val: Любое значение даты.
        :return: Строка ``"YYYY-MM-DD"`` или исходное строковое представление, если
                 парсинг не удался.
        """
        import datetime as _dt
        import warnings as _warnings
        if isinstance(val, (pd.Timestamp, _dt.datetime, _dt.date)):
            return pd.Timestamp(val).strftime("%Y-%m-%d")
        s = str(val).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                return _dt.datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        try:
            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")
                return pd.to_datetime(val, dayfirst=True).strftime("%Y-%m-%d")
        except Exception:
            return s

    @classmethod
    def _merge_vertical_rows(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Сливает несколько строк плоской таблицы (DataFrame) в одну запись.
        """
        def _missing(v: Any) -> bool:
            return v is None or (isinstance(v, float) and math.isnan(v))

        _GOST_COL = "DOCUMENTS_GOST"
        table_cols = {src for src, _ in cls._OP_FIELD_MAP + cls._DYN_FIELD_MAP}
        vertical_cols = table_cols | {_GOST_COL}
        scalar_cols = [c for c in df.columns if c not in vertical_cols]

        # Скалярные поля: первое непустое значение
        record: Dict[str, Any] = {}
        for col in scalar_cols:
            for val in df[col]:
                if not _missing(val):
                    record[col] = val
                    break

        # DOCUMENTS_GOST: все непустые значения столбца как список строк
        if _GOST_COL in df.columns:
            gosts: List[str] = []
            for val in df[_GOST_COL]:
                if not _missing(val):
                    for part in str(val).split(","):
                        part = part.strip()
                        if part:
                            gosts.append(part)
            if gosts:
                record[_GOST_COL] = gosts

        # OBSERVATION_POINTS
        op_anchor = "OP_POINT"
        if op_anchor in df.columns:
            points = []
            for _, row in df.iterrows():
                if _missing(row.get(op_anchor)):
                    continue
                point: Dict[str, Any] = {}
                for src, dst in cls._OP_FIELD_MAP:
                    val = row.get(src)
                    if not _missing(val):
                        point[dst] = val
                if point:
                    points.append(point)
            if points:
                record["OBSERVATION_POINTS"] = points

        # RESULTS_DYNAMIC / OBSERVATION_DYNAMICS
        dyn_anchor = "DYN_DATE"
        if dyn_anchor in df.columns:
            dynamics = []
            for _, row in df.iterrows():
                date_val = row.get(dyn_anchor)
                if _missing(date_val):
                    continue
                entry: Dict[str, Any] = {"date": cls._normalize_date(date_val)}
                for src, dst in cls._DYN_FIELD_MAP[1:]:
                    val = row.get(src)
                    if not _missing(val):
                        entry[dst] = val
                dynamics.append(entry)
            if dynamics:
                record["RESULTS_DYNAMIC"] = dynamics
                record.setdefault("OBSERVATION_DYNAMICS", dynamics)

        cls._reconstruct_test_results(record)
        return record

    @classmethod
    def _clean_record(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Очищает одну запись: удаляет NaN/None и раскрывает вложенные структуры.

        * JSON-строки в полях ``_COMPLEX_FIELDS`` разворачиваются в объекты.
        * ``REPORT_DATE`` нормализуется в формат ``YYYY-MM-DD``.

        :param record: Сырой словарь с данными.
        :return: Очищенный словарь.
        """
        def _is_missing(v: Any) -> bool:
            if v is None:
                return True
            if isinstance(v, float) and math.isnan(v):
                return True
            return False

        clean = {k: v for k, v in record.items() if not _is_missing(v)}

        # Раскрываем JSON-строки в сложных полях
        for field in _COMPLEX_FIELDS:
            if field in clean and isinstance(clean[field], str):
                value = clean[field].strip()
                if (value.startswith("{") and value.endswith("}")) or \
                   (value.startswith("[") and value.endswith("]")):
                    try:
                        clean[field] = json.loads(value.replace("'", '"'))
                    except (json.JSONDecodeError, ValueError):
                        pass

        # REPORT_DATE: нормализуем в YYYY-MM-DD (обрабатывает форматы с «/»)
        if "REPORT_DATE" in clean:
            clean["REPORT_DATE"] = cls._normalize_date(clean["REPORT_DATE"])

        return clean


class ManualImporter(Importer):
    """
    Импортер для работы с данными, переданными напрямую в виде структур Python (dict, list).
    """

    def _read_records(self) -> List[Dict[str, Any]]:
        if isinstance(self.source, dict):
            return [self.source]
        elif isinstance(self.source, list):
            return self.source
        raise ValueError("Для ManualImporter источник должен быть словарем или списком словарей.")

    def import_data(self) -> List[ReportInputData]:
        """
        Выполняет импорт из словаря или списка словарей.

        :return: Список объектов ReportInputData.
        :raises ValueError: Если источник данных не является словарем или списком.
        """
        return [ReportInputData.model_validate(rec) for rec in self._read_records()]


class XLSXImporter(Importer):
    """
    Импортер для загрузки данных из файлов формата Excel (.xlsx).

    Поддерживаются два формата (детектируются автоматически):

    Вертикальный одно-листовой формат:
    Единственный лист содержит все данные — скалярные поля в первой строке,
    таблицы идут вниз построчно.

    Многолистовой формат:

    * **Отчет** — скалярные поля
    * **ГОСТ** — один столбец с названиями нормативных документов
    * **Точки_наблюдения** — таблица точек мониторинга
    * **Динамика** — таблица динамики измерений
    """

    _TABLE_SHEETS: Dict[str, str] = {
        "Точки_наблюдения": "OBSERVATION_POINTS",
        "Динамика":         "RESULTS_DYNAMIC",
    }
    _GOST_SHEET = "ГОСТ"

    def _read_records(self) -> List[Dict[str, Any]]:
        xls = pd.ExcelFile(self.source, engine="openpyxl")
        df_main = pd.read_excel(xls, sheet_name=xls.sheet_names[0])

        if "OP_POINT" in df_main.columns or "DYN_DATE" in df_main.columns:
            return [self._merge_vertical_rows(df_main)]

        records = df_main.to_dict(orient="records")

        # Таблицы с отдельных листов
        table_data: Dict[str, List] = {}
        for sheet_name, field_key in self._TABLE_SHEETS.items():
            if sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name).dropna(how="all")
                table_data[field_key] = df.to_dict(orient="records") if not df.empty else []

        gost_list: List[str] | None = None
        if self._GOST_SHEET in xls.sheet_names:
            df_gost = pd.read_excel(xls, sheet_name=self._GOST_SHEET).dropna(how="all")
            if not df_gost.empty:
                gost_list = df_gost.iloc[:, 0].dropna().astype(str).tolist()

        for record in records:
            record.update(table_data)
            if "RESULTS_DYNAMIC" in table_data:
                record.setdefault("OBSERVATION_DYNAMICS", table_data["RESULTS_DYNAMIC"])
            if gost_list is not None:
                record["DOCUMENTS_GOST"] = gost_list
            self._reconstruct_test_results(record)

        return records

    def import_data(self) -> List[ReportInputData]:
        """
        Читает Excel-файл и преобразует его содержимое в объекты ReportInputData.

        :return: Список объектов ReportInputData.
        """
        return self._process_records(self._read_records())


class CSVImporter(Importer):
    """
    Импортер для загрузки данных из файлов формата CSV.
    """

    def _read_records(self) -> List[Dict[str, Any]]:
        df = pd.read_csv(self.source)

        if "OP_POINT" in df.columns or "DYN_DATE" in df.columns:
            return [self._merge_vertical_rows(df)]

        return df.to_dict(orient="records")

    def import_data(self) -> List[ReportInputData]:
        """
        Читает CSV-файл и преобразует его содержимое в объекты ReportInputData.

        :return: Список объектов ReportInputData.
        """
        return self._process_records(self._read_records())


def import_from_any(source: Any, source_type: str) -> List[ReportInputData]:
    """
    Универсальная функция для импорта данных.
    :param source: Данные или путь к файлу
    :param source_type: Тип источника ('manual', 'xlsx', 'csv')
    :return: Список объектов ReportInputData
    """
    importers = {
        "manual": ManualImporter,
        "xlsx":   XLSXImporter,
        "csv":    CSVImporter,
    }
    if source_type not in importers:
        raise ValueError(
            f"Неподдерживаемый тип источника: {source_type}. Допустимые: {list(importers.keys())}"
        )
    return importers[source_type](source).import_data()
