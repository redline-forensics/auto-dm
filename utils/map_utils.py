import math

earth_pix = 268435456
pix_rad = earth_pix / math.pi


def lat_to_px(lat):
    sin_lat = math.sin(math.radians(lat))
    return earth_pix - pix_rad * math.log((1 + sin_lat) / (1 - sin_lat)) / 2


def px_to_lat(pix):
    r = math.exp(2 * earth_pix / pix_rad)
    x = math.exp(2 * pix / pix_rad)
    return math.degrees(math.asin((r - x) / (r + x)))


def lon_to_px(lon):
    return earth_pix + lon * math.radians(pix_rad)


def px_to_lon(pix):
    return math.degrees((pix - earth_pix) / pix_rad)


def px_to_deg(pixels, zoom):
    return pixels * 2 ** (21 - zoom)


def points_to_coords(point_a, point_b):
    lat = sorted([point_a[0], point_b[0]], key=abs, reverse=True)
    lon = sorted([point_a[1], point_b[1]], key=abs, reverse=True)
    return lat, lon


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3959 * 5280  # radius in feet

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def calculate_dimensions_in_ft(lat, lon, width_px, height_px):
    x1_px = lon_to_px(lon[1])
    x2_px = x1_px + width_px
    x1 = lon[1]
    x2 = px_to_lon(x2_px)
    width = distance((lat[1], x1), (lat[1], x2))

    y1_px = lat_to_px(lat[1])
    y2_px = y1_px + height_px
    y1 = lat[1]
    y2 = px_to_lat(y2_px)
    height = distance((y1, lon[1]), (y2, lon[1]))

    return width, height
