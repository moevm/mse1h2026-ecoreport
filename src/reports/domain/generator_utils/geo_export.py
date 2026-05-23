import geojson


GREEN_HEX = "#30DB30"
RED_HEX = "#DB3030"

# RGB компоненты зелёного и красного для градиента
_GREEN_RGB = (0x30, 0xDB, 0x30)  # (48, 219, 48)
_RED_RGB   = (0xDB, 0x30, 0x30)  # (219, 48, 48)

# соответствие отображаемых названий показателей ключам свойств GeoJSON
_INDICATOR_KEY_MAP = {
    "pH":       "pH",
    "Железо":   "iron",
    "Марганец": "manganese",
    "Нитраты":  "nitrates",
    "Сульфаты": "sulfates",
}


def compute_gradient_color(ratio: float) -> str:
    """
    Возвращает hex-цвет, линейно интерполированный от зелёного к красному.

    ratio=0.0 — все измерения в норме (зелёный).
    ratio=1.0 — все измерения вне нормы (красный).
    """
    ratio = max(0.0, min(1.0, ratio))
    r = round(_GREEN_RGB[0] + (_RED_RGB[0] - _GREEN_RGB[0]) * ratio)
    g = round(_GREEN_RGB[1] + (_RED_RGB[1] - _GREEN_RGB[1]) * ratio)
    b = round(_GREEN_RGB[2] + (_RED_RGB[2] - _GREEN_RGB[2]) * ratio)
    return f"#{r:02X}{g:02X}{b:02X}"


def _parse_float(value) -> float | None:
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return None


def generate_report_geojson(data: dict) -> str:
    """
    Генерирует GeoJSON FeatureCollection по точкам наблюдения и таблице результатов.

    Каждый Feature содержит:
    - числовые значения показателей (pH, iron, manganese, nitrates, sulfates),
    - hex-цвет маркера («marker-color»)

    :param data: dict - словарь данных формы для генерации отчета
    :return: строка GeoJSON
    """
    observation_points = data.get("OBSERVATION_POINTS", [])
    if not observation_points:
        return ""
    test_results = data.get("TEST_RESULTS", [])

    measurements: dict = {}
    non_compliant = 0
    total = 0

    for result in test_results:
        indicator = str(result.get("indicator", ""))
        key = _INDICATOR_KEY_MAP.get(indicator, indicator.lower())
        value = _parse_float(result.get("result"))
        if value is not None:
            measurements[key] = value

        compliance = str(result.get("compliance", "")).strip().lower()
        if compliance in ("да", "нет"):
            total += 1
            if compliance == "нет":
                non_compliant += 1

    ratio = non_compliant / total if total > 0 else 0.0
    color = compute_gradient_color(ratio)

    features: list = []
    for point in observation_points:
        if not isinstance(point, dict):
            continue
        lat = _parse_float(point.get("latitude") if point.get("latitude") is not None else point.get("lat"))
        lon = _parse_float(point.get("longitude") if point.get("longitude") is not None else point.get("lon"))
        if lat is None or lon is None:
            continue

        properties = {
            "name":        str(point.get("observation_point") or ""),
            "medium_type": str(point.get("medium_type") or ""),
            "description": str(point.get("description") or ""),
            "marker-color": color,
            **measurements,
        }
        features.append(geojson.Feature(geometry=geojson.Point((lon, lat)), properties=properties))

    return geojson.dumps(geojson.FeatureCollection(features))
