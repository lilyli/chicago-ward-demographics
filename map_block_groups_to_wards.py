import shapely.ops as ops
from shapely.geometry import shape
import fiona
import pyproj
from functools import partial
import json
import csv
# need to import shapely first or program will crash
# see https://github.com/Toblerity/Shapely/issues/553


COOK_IL_COUNTYFP = '031'

def map_block_groups_to_wards():
    bg_to_ward_mapping = {}

    # read in chicago wards shapefile
    wards = {} # dict mapping ward ids to shapes

    with open('data/ward_boundaries.geojson') as f:
        wards_data = json.load(f)
    # from https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2017&layergroup=Block+Groups

    for feat in wards_data['features']:
        ward_id = feat['properties']['ward']
        ward_geom_1 = shape(feat['geometry'])
        # polygon consists of lat, long coord
        # transform the polygon to projected equal area coordinates to derive accurate area calculations
        ward_geom = ops.transform(
            partial(
                pyproj.transform,
                pyproj.Proj(init = 'EPSG:4326'),
                pyproj.Proj(
                    proj = 'aea',
                    lat1 = ward_geom_1.bounds[1],
                    lat2 = ward_geom_1.bounds[3])),
            ward_geom_1)
        wards[ward_id] = ward_geom

    # read in il block groups shapefile, map block groups to wards
    with fiona.open("data/block_group_shapefiles/tl_2017_17_bg.shp") as il_block_groups:
        # il_block_groups.schema
        for bg in il_block_groups:
            if bg['properties']['COUNTYFP'] == COOK_IL_COUNTYFP:
                bg_geom_1 = shape(bg['geometry'])
                bg_geom = ops.transform(
                    partial(
                        pyproj.transform,
                        pyproj.Proj(init = 'EPSG:4326'),
                        pyproj.Proj(
                            proj = 'aea',
                            lat1 = bg_geom_1.bounds[1],
                            lat2 = bg_geom_1.bounds[3])),
                    bg_geom_1)
                
                intersecting_wards = []
                # a bg may intersect w/ multiple wards due to imperfect boundaries,
                # so find all intersections and sort by largest % of bg
                for ward_id, ward_geom in wards.items():
                    if bg_geom.intersects(ward_geom):
                        intersecting_wards.append((ward_id, bg_geom.intersection(ward_geom).area / bg_geom.area * 100))

                if len(intersecting_wards) > 0:
                    intersecting_wards = sorted(intersecting_wards, key = lambda x: x[1], reverse = True)
                    bg_to_ward_mapping[bg['properties']['GEOID']] = intersecting_wards[0][0]

    return bg_to_ward_mapping


if __name__ == '__main__':
    bg_to_ward_mapping = map_block_groups_to_wards()

    with open('block_group_ward_mapping.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['bg_id', 'ward_id'])
        for bg_id, ward_id in bg_to_ward_mapping.items():
           writer.writerow([int(bg_id), int(ward_id)])

