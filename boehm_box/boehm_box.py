import geopandas as gpd
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate

import matplotlib.pyplot as plt


point_frame_size = 1 # m
fname = './LTVM_PointFrame_wDirection.shp'
df = gpd.read_file(fname)
result = df.copy()

def box_it(row,frame_size=1):
    x0 = row['geometry'].x
    y0 = row['geometry'].y

    x1 = x0 + point_frame_size
    y1 = y0 + point_frame_size
    direction = row['Direction']

    return rotate(Polygon([(x0,y0),(x1,y0),(x1,y1),(x0,y1)]), direction, origin=Point(x0,y0))

print(result.crs)

# Create a box from each point
result['frame'] = df.apply(box_it, axis=1)
# Rotate the box according to direction
result = gpd.GeoDataFrame(result, geometry='frame')
del result['geometry']
result.crs = df.crs
result.to_file("./test.shp")
