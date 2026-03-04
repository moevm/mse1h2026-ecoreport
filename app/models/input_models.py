from datetime import date
from enum import Enum
from typing import List, Optional, Union, Literal

# импорты из Pydantic - библиотеки для валидации данных
from pydantic import BaseModel, Field, field_validator, ConfigDict

# перечисления (Enums) для ограниченных наборов значений
class ObjectType(str, Enum):
    """Общая информация об объекте: тип"""
    BOG = "болото"
    URBAN = "город"
    PROTECTED_AREA = "ООПТ"

class MaterialType(str, Enum):
    """Материал: тип"""
    PVC = "ПВХ"
    HDPE = "ПНД"
    CONCRETE = "бетон"
    CERAMIC = "керамика"
    METAL = "металл"

class SubstanceType(str, Enum):
    """Результаты выщелачивания: вещество"""
    FE = "железо"
    CD = "кадмий"
    PB = "свинец"
    HG = "ртуть"
    AS = "мышьяк"
    NI = "никель"
    CU = "медь"
    CR = "хром"
    ZN = "цинк"
    OIL = "нефтепродукты"
    PHENOL = "фенолы"

class UnitOfMeasure(str, Enum):
    """Результаты выщелачивания: единица измерения"""
    MG_L = "мг/л"
    MCG_L = "мкг/л"
    MG_KG = "мг/кг"

# модели географических координат
class PointCoordinate(BaseModel):
    """Географическая точка (широта, долгота) в градусах"""
    lat: float = Field(..., description = "широта, градусы (от -90 до 90)")
    lon: float = Field(..., description = "долгота, градусы (от -180 до 180)")

    @field_validator("lat")
    def validate_lat(cls, value: float) -> float:
        """
        Проверяет, что широта находится в допустимом диапазоне [-90, 90].
        """
        if not -90 <= value <= 90:
            raise ValueError("широта должна быть в диапазоне [-90, 90]")
        return value

    @field_validator("lon")
    def validate_lon(cls, value: float) -> float:
        """
        Проверяет, что долгота находится в допустимом диапазоне [-180, 180].
        """
        if not -180 <= value <= 180:
            raise ValueError("долгота должна быть в диапазоне [-180, 180]")
        return value

class PolygonCoordinate(BaseModel):
    """Общая информация об объекте: площадь – список точек в порядке обхода (минимум 3 точки)"""
    points: List[PointCoordinate] = Field(..., min_length = 3, description = "список координат, образующих замкнутую площадь")

# модели материалов и результатов выщелачивания
class Material(BaseModel):
    """Материал"""
    name: MaterialType = Field(..., description = "тип материала")
    description: Optional[str] = Field(None, description = "описание материала")
    density: Optional[float] = Field(None, ge = 0, description = "плотность материала, кг/м^3")
    composition: Optional[str] = Field(None, description = "химический состав материала")

class LeachingResult(BaseModel):
    """Результаты выщелачивания"""
    substance: SubstanceType = Field(..., description = "вещество")
    concentration: float = Field(..., ge = 0, description = "концентрация")
    unit: UnitOfMeasure = Field(..., description = "единица измерения")
    sampling_date: date = Field(..., description = "дата отбора пробы")
    method: Optional[str] = Field(None, description = "методика анализа")
    sampling_point: PointCoordinate = Field(..., description = "координаты точки отбора, градусы")

    @field_validator("concentration")
    def check_positive(cls, value: float) -> float:
        """
        Проверяет, что концентрация является положительным числом.
        """
        if value < 0:
            raise ValueError("concentration не может быть отрицательной")
        return value
    
    @field_validator("sampling_date")
    def validate_date_range(cls, value: date) -> date:
        """
        Проверяет, что дата отбора пробы находится в разумных пределах (не раньше 1900 года и не в будущем).
        """
        min_date = date(1900, 1, 1)
        max_date = date.today()
        if value < min_date:
            raise ValueError(f"дата не может быть раньше {min_date}")
        if value > max_date:
            raise ValueError("дата отбора не может быть в будущем")
        return value

# модели для разных типов объектов
class BaseSiteInfo(BaseModel):
    """Общая информация об объекте"""
    object_type: ObjectType = Field(..., description = "тип объекта")
    name: str = Field(..., min_length = 1, description = "наименование")
    location_description: Optional[str] = Field(None, description = "описание местоположения")
    coordinates: Union[PointCoordinate, PolygonCoordinate] = Field(..., description = "координаты объекта (точка или область)")
    area_ha: Optional[float] = Field(None, ge = 0, description = "площадь объекта, га")
    land_category: Optional[str] = Field(None, description = "категория земель")

class BogSiteInfo(BaseSiteInfo):
    """Специальная информация об объекте: болото"""
    object_type: Literal[ObjectType.BOG] = ObjectType.BOG  # переопределение
    bog_type: Optional[str] = Field(None, description = "тип болота")
    peat_depth_avg: Optional[float] = Field(None, ge = 0, description = "средняя глубина, м")
    peat_volume: Optional[float] = Field(None, ge = 0, description = "объём торфа, м³")
    hydrological_regime: Optional[str] = Field(None, description = "характеристика водного режима")

class UrbanSiteInfo(BaseSiteInfo):
    """Специальная информация об объекте: город"""
    object_type: Literal[ObjectType.URBAN] = ObjectType.URBAN # переопределение
    population: Optional[int] = Field(None, ge = 0, description = "численность населения")
    infrastructure_density: Optional[float] = Field(None, ge = 0, description = "плотность застройки, %")
    drainage_system_type: Optional[str] = Field(None, description = "тип дренажной системы")

class ProtectedAreaSiteInfo(BaseSiteInfo):
    """Специальная информация об объекте: ООПТ"""
    object_type: Literal[ObjectType.PROTECTED_AREA] = ObjectType.PROTECTED_AREA # переопределение
    category: Optional[str] = Field(None, description = "категория ООПТ")
    protection_regime: Optional[str] = Field(None, description = "режим особой охраны")
    responsible_authority: Optional[str] = Field(None, description = "организация, ответственная за охрану")

# модель дренажной системы
class DrainageSystem(BaseModel):
    """Дренажные системы"""
    system_id: str = Field(..., min_length = 1, description = "ID")
    system_type: str = Field(..., description = "тип дренажной системы")
    material: List[Material] = Field(..., min_length = 1, description="материалы")
    installation_year: Optional[int] = Field(None, ge = 1700, le = 2100, description = "год ввода в эксплуатацию")
    depth_min: Optional[float] = Field(None, ge = 0, description = "минимальная глубина заложения, м")
    depth_max: Optional[float] = Field(None, ge = 0, description = "максимальная глубина заложения, м")
    diameter_mm: Optional[float] = Field(None, ge = 0, description = "диаметр трубы, мм")
    total_length_m: Optional[float] = Field(None, ge = 0, description = "общая протяжённость, м")
    serviced_area_ha: Optional[float] = Field(None, ge = 0, description = "обслуживаемая площадь, га")

    @field_validator("depth_max")
    def check_depth_order(cls, value: Optional[float], info) -> Optional[float]:
        """
        Проверяет корректность порядка глубин (максимальная должна быть больше или равна минимальной).
        """
        if value is not None and "depth_min" in info.data and info.data["depth_min"] is not None:
            if value < info.data["depth_min"]:
                raise ValueError("максимальная глубина не может быть меньше минимальной")
        return value

# общая входная модель для генерации отчёта
class ReportInputData(BaseModel):
    """общая модель, объединяющая все данные"""
    report_id: str = Field(..., min_length = 1, description = "ID отчёта")
    generated_at: date = Field(default_factory = date.today, description = "дата создания отчета")
    site_info: Union[BogSiteInfo, UrbanSiteInfo, ProtectedAreaSiteInfo] = Field(..., discriminator = "object_type", description = "специальная информация об объекте")
    drainage_systems: List[DrainageSystem] = Field(..., min_length = 1, description = "дренажные системы")
    leaching_results: List[LeachingResult] = Field(..., description = "результаты выщелачивания")
    normative_docs: List[str] = Field(default_factory = list, description = "применённые ГОСТ/СНиП/приказы")
    model_config = ConfigDict(extra="forbid")
    