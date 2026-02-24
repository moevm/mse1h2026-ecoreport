import geojson


POLLUTION_THRESHOLD = 10.0
GREEN_HEX = "#30DB30"
RED_HEX = "#DB3030"


def feature_data_point(longitude: float, latitude: float, pollution_level: float) -> geojson.Feature:
    '''
    create a GeoJSON Feature object representing a Point with included data, such as the color to display based on pollution level

    :type longitude: float
    :type latitude: float
    :type pollution_level: float
    :return:
    :rtype: geojson.Feature
    '''

    color_hex: str = GREEN_HEX if pollution_level < POLLUTION_THRESHOLD else RED_HEX
    properties: dict = {"pollution_level": pollution_level, "marker-color": color_hex}
    new_point: geojson.Point = geojson.Point((longitude, latitude))
    new_feature: geojson.Feature = geojson.Feature(geometry=new_point, properties=properties)
    return new_feature


def create_collection_geojson(longitudes: list[float], latitudes: list[float], pollution_levels: list[float]) -> str:
    '''
    create a GeoJSON Feature object representing a Point with included data, such as the color to display based on pollution level

    :type longitudes: list[float]
    :type latitudes: list[float]
    :type pollution_levels: list[float]
    :return:
    :rtype: geojson.FeatureCollection
    '''
    points: list = list()
    for i in range(len(longitudes)):
        points.append(feature_data_point(longitudes[i], latitudes[i], pollution_levels[i]))
    collection: geojson.FeatureCollection = geojson.FeatureCollection(points)
    return geojson.dumps(collection)


def create_point_feature_geojson(longitude: float, latitude: float, pollution_level: float) -> str:
    return geojson.dumps(feature_data_point(longitude, latitude, pollution_level))


if __name__ == "__main__":
    #example of creating a geojson file
    longs = [0.4214, 61.12315, 57.24239]
    lats = [75.5466, 15.4521, 87.342521]
    pollution = [0.0, 5.0, 11.7]
    with open("example1.geojson", "w") as file:
        file.write(create_collection_geojson(longs, lats, pollution))
    with open("example2.geojson", "w") as file:
        file.write(create_point_feature_geojson(longs[0], lats[0], pollution[0]))
