from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from decimal import Decimal

class UserBase(BaseModel):
    user_name: Optional[str] = None
    password_hash: Optional[str] = None
    image_path: Optional[str] = None
    created_at: Optional[date] = None
    update_at: Optional[date] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class DocumentsGostBase(BaseModel):
    gost_r_72274_2025: Optional[bool] = None
    gost_1811_2019: Optional[bool] = None
    gost_4_225_83: Optional[bool] = None
    sp_32_13330_2018: Optional[bool] = None
    snip_32_03_96: Optional[bool] = None
    gost_r_71831_2024: Optional[bool] = None
    gost_r_54560_2015: Optional[bool] = None
    gost_286_82: Optional[bool] = None
    sp_100_13330_2016: Optional[bool] = None
    snip_2_06_15_85: Optional[bool] = None
    gost_r_71856_2024: Optional[bool] = None
    gost_33068_2014: Optional[bool] = None
    sanpin_2_1_3684_21: Optional[bool] = None
    sp_104_13330_2016: Optional[bool] = None
    snip_2_04_03_85: Optional[bool] = None
    gost_r_70628_1_2023: Optional[bool] = None
    gost_31416_2009: Optional[bool] = None
    sp_31_13330_2021: Optional[bool] = None
    sp_250_1325800_2016: Optional[bool] = None
    snip_2_05_02_85: Optional[bool] = None
    gost_r_70628_2_2023: Optional[bool] = None
    gost_6942_98: Optional[bool] = None
    sp_34_13330_2021: Optional[bool] = None
    sp_116_13330_2012: Optional[bool] = None
    snip_2_06_03_85: Optional[bool] = None
    gost_r_70628_5_2023: Optional[bool] = None
    gost_17_1_3_13_86: Optional[bool] = None
    sp_121_13330_2019: Optional[bool] = None
    sp_50_101_2004: Optional[bool] = None
    description: Optional[str] = None

class DocumentsGostCreate(DocumentsGostBase):
    pass

class DocumentsGostUpdate(DocumentsGostBase):
    pass

class ObservationPointBase(BaseModel):
    file_id: Optional[int] = None
    observation_point: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    medium_type: Optional[str] = None
    description: Optional[str] = None

class ObservationPointCreate(ObservationPointBase):
    pass

class ObservationPointUpdate(ObservationPointBase):
    pass

class TestResultsBase(BaseModel):
    results_ph: Optional[Decimal] = None
    results_iron: Optional[Decimal] = None
    results_manganese: Optional[Decimal] = None
    results_nitrates: Optional[Decimal] = None
    results_sulfates: Optional[Decimal] = None

class TestResultsCreate(TestResultsBase):
    pass

class TestResultsUpdate(TestResultsBase):
    pass

class ObservationDynamicBase(BaseModel):
    file_id: Optional[int] = None
    dynamic_ph: Optional[Decimal] = None
    dynamic_iron: Optional[Decimal] = None
    dynamic_manganese: Optional[Decimal] = None
    dynamic_nitrates: Optional[Decimal] = None
    dynamic_sulfates: Optional[Decimal] = None
    dynamic_data: Optional[date] = None

class ObservationDynamicCreate(ObservationDynamicBase):
    pass

class ObservationDynamicUpdate(ObservationDynamicBase):
    pass

class DynamicResult(BaseModel):
    """Модель для динамики результатов наблюдений"""
    date: str = Field(..., description="Дата измерения")
    pH: float = Field(..., description="Показатель pH")
    iron: float = Field(..., description="Содержание железа")
    manganese: float = Field(..., description="Показатель марганца")
    nitrates: float = Field(..., description="Показатель нитратов")
    sulfates: float = Field(..., description="Показатель сульфатов")

class ReportInputData(BaseModel):
    """Актуальная модель данных для генерации отчета, соответствующая требованиям модуля генерации"""
    user_id: str = Field(...)
    report_id: str = Field(...)
    
    # Информация об объекте
    FULL_OBJECT_NAME: str = Field(..., description="Полное наименование объекта")
    SHORT_OBJECT_NAME: str = Field(..., description="Сокращенное наименование объекта")
    YEAR: int = Field(..., description="Год отчетного периода")
    ORGANIZATION_NAME: str = Field(..., description="Наименование организации")
    REGION: str = Field(..., description="Регион размещения")
    
    # Нормативные документы
    DOCUMENTS_GOST: List[str] = Field(default_factory=list, description="Список нормативных документов (ГОСТ и др.)")
    
    # Природные условия
    RELIEF_TYPE: str = Field(..., description="Тип рельефа")
    SOIL_TYPE: str = Field(..., description="Тип почвы")
    GROUNDWATER_LEVEL: str = Field(..., description="Уровень грунтовых вод")
    CLIMATE_ZONE: str = Field(..., description="Климатическая зона")
    
    # Координаты объекта
    COORDINATES_LATITUDE: float = Field(..., description="Широта объекта (градусы)")
    COORDINATES_LONGITUDE: float = Field(..., description="Долгота объекта (градусы)")
    
    # Характеристика системы
    OBJECT_TYPE: str = Field(..., description="Тип объекта (например, город)")
    SYSTEM_TYPE: str = Field(..., description="Тип дренажной системы")
    PIPE_MATERIAL: str = Field(..., description="Материал труб")
    PIPE_DIAMETER: str = Field(..., description="Диаметр трубы")
    PIPE_DEPTH: str = Field(..., description="Глубина заложения труб")
    PIPE_LENGTH: str = Field(..., description="Общая протяженность труб")
    PIPE_INSTALL_YEAR: int = Field(..., description="Год ввода системы в эксплуатацию")
    MANHOLE_COUNT: int = Field(..., description="Количество смотровых колодцев")
    
    # Мониторинг
    MONITORING_POINT_COUNT: int = Field(..., description="Количество точек мониторинга")
    OBSERVATION_POINT: str = Field(..., description="Наименование точки наблюдения")
    LATITUDE: float = Field(..., description="Широта точки наблюдения")
    LONGITUDE: float = Field(..., description="Долгота точки наблюдения")
    MEDIUM_TYPE: str = Field(..., description="Тип контролируемой среды (например, вода)")
    DESCRIPTION: str = Field(..., description="Описание точки/объекта мониторинга")
    OBSERVATION_POINTS: List[Dict[str, Any]] = Field(default_factory=list, description="Список точек наблюдения для таблицы")
    OBSERVATION_FREQUENCY: str = Field(..., description="Периодичность наблюдений")
    
    # Текущие результаты
    RESULTS_PH: float = Field(..., description="Текущий показатель pH")
    RESULTS_IRON: float = Field(..., description="Текущее содержание железа")
    RESULTS_MANGANESE: float = Field(..., description="Текущее содержание марганца")
    RESULTS_NITRATES: float = Field(..., description="Текущее содержание нитратов")
    RESULTS_SULFATES: float = Field(..., description="Текущее содержание сульфатов")
    
    # Результаты лабораторных анализов
    TEST_RESULTS: List[Dict[str, Any]] = Field(default_factory=list, description="Таблица результатов лабораторных анализов")
    
    # Динамика
    RESULTS_DYNAMIC: List[DynamicResult] = Field(default_factory=list, description="Динамика изменения показателей")
    OBSERVATION_DYNAMICS: List[Dict[str, Any]] = Field(default_factory=list, description="Таблица динамики наблюдений")
    
    # Контактная информация
    ORGANIZATION_ADDRESS: str = Field(..., description="Юридический адрес организации")
    ORGANIZATION_PHONE: str = Field(..., description="Контактный телефон")
    ORGANIZATION_EMAIL: str = Field(..., description="Электронная почта")
    RESPONSIBLE_NAME: str = Field(..., description="ФИО ответственного лица")
    RESPONSIBLE_POSITION: str = Field(..., description="Должность ответственного лица")
    REPORT_DATE: str = Field(..., description="Дата составления отчета")

    model_config = ConfigDict(extra="ignore")


class GeneratedReportData(BaseModel):
    user_id: str = Field(...)
    file_name: str = Field(...)
    