import json
from abc import ABC, abstractmethod
from typing import List, Any, Dict
import pandas as pd
from reports.schemas.report_models import ReportInputData


class Importer(ABC):
    """
    Базовый класс для импорта данных.

    Обеспечивает базовый интерфейс для загрузки данных и общую логику обработки
    сырых записей, включая парсинг JSON-строк во вложенных полях.
    """
    def __init__(self, source: Any):
        """
        Инициализирует импортер источником данных.

        :param source: Источник данных (словарь/список для ManualImporter, путь к файлу для CSV/XLSX).
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

    def _process_records(self, records: List[Dict[str, Any]]) -> List[ReportInputData]:
        """
        Вспомогательный метод для обработки сырых записей, полученных из табличных данных.

        Метод выполняет:
        1. Очистку записей от отсутствующих значений (NaN).
        2. Попытку парсинга строковых представлений JSON во вложенных структурах
           (site_info, drainage_systems и др.).
        3. Валидацию данных через Pydantic-модель ReportInputData.

        :param records: Список словарей с сырыми данными.
        :return: Список провалидированных объектов ReportInputData.
        """
        results = []
        for record in records:
            clean_record = {k: v for k, v in record.items() if pd.notna(v)}

            # Попытка распарсить JSON в полях, которые ожидают вложенные структуры
            complex_fields = ["DOCUMENTS_GOST", "RESULTS_DYNAMIC"]
            for field in complex_fields:
                if field in clean_record and isinstance(clean_record[field], str):
                    value = clean_record[field].strip()
                    if (value.startswith('{') and value.endswith('}')) or \
                       (value.startswith('[') and value.endswith(']')):
                        try:
                            json_val = value.replace("'", '"')
                            clean_record[field] = json.loads(json_val)
                        except (json.JSONDecodeError, ValueError):
                            pass

            results.append(ReportInputData.model_validate(clean_record))
        return results


class ManualImporter(Importer):
    """
    Импортер для работы с данными, переданными напрямую в виде структур Python (dict, list).
    """
    def import_data(self) -> List[ReportInputData]:
        """
        Выполняет импорт из словаря или списка словарей.

        :return: Список объектов ReportInputData.
        :raises ValueError: Если источник данных не является словарем или списком.
        """
        if isinstance(self.source, dict):
            return [ReportInputData.model_validate(self.source)]
        elif isinstance(self.source, list):
            return [ReportInputData.model_validate(item) for item in self.source]
        else:
            raise ValueError("Для ManualImporter источник должен быть словарем или списком словарей.")


class XLSXImporter(Importer):
    """
    Импортер для загрузки данных из файлов формата Excel (.xlsx).
    """
    def import_data(self) -> List[ReportInputData]:
        """
        Читает Excel-файл и преобразует его содержимое в объекты ReportInputData.

        :return: Список объектов ReportInputData.
        """
        df = pd.read_excel(self.source)
        records = df.to_dict(orient='records')
        return self._process_records(records)


class CSVImporter(Importer):
    """
    Импортер для загрузки данных из файлов формата CSV.
    """
    def import_data(self) -> List[ReportInputData]:
        """
        Читает CSV-файл и преобразует его содержимое в объекты ReportInputData.

        :return: Список объектов ReportInputData.
        """
        df = pd.read_csv(self.source)
        records = df.to_dict(orient='records')
        return self._process_records(records)


def import_from_any(source: Any, source_type: str) -> List[ReportInputData]:
    """
    Универсальная функция для импорта данных.
    :param source: Данные или путь к файлу
    :param source_type: Тип источника ('manual', 'xlsx', 'csv')
    :return: Список объектов ReportInputData
    """
    importers = {
        "manual": ManualImporter,
        "xlsx": XLSXImporter,
        "csv": CSVImporter
    }
    if source_type not in importers:
        raise ValueError(f"Неподдерживаемый тип источника: {source_type}. Допустимые: {list(importers.keys())}")
    
    return importers[source_type](source).import_data()


