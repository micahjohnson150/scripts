import geopandas as gpd
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate

def box_it(row,frame_size=1):
    x0 = row['geometry'].x
    y0 = row['geometry'].y

    # Point #2 should point north so the x dir is negative and go counter clockwise
    x1 = x0 - frame_size
    y1 = y0 + frame_size

    # Direction is the heading to the #2 point to the right of origin
    direction = -1 * row['Direction']

    p = Polygon([(x0,y0),(x0,y1),(x1,y1),(x1,y0)])

    return rotate(p, direction, origin=Point(x0,y0))
    #return p

def main():
    """
    This is the main function for running the script. This script processes
    points for veg framing. The point represents the bottom left of each frame.

    A shapefile should be provided that has the direction in degrees from North
    (Positive clockwise) when standing at the bottom left point and looking
    toward the lower right point of the frame.

    This script takes those points and creates a square with its BL at the point
    provided and rotated about BL the direction provided in the file. The final
    output is a single shapefile with many squares in it rotated accordingly.

    Designed for Alex Boehm at the USDA-ARS-NWRC

    Usage:
        python boehm_box.py

    Install:

    * python 3.5 +
    * pip install geopandas
    * download this file
    """

    # File name to shapefile containing points with a Direction attribute
    fname = './LTVM_PointFrame_wDirection.shp'

    # Square Frame Size Input
    frame_size = 1 # Size in meters

    # Output file name
    out_f = './test.shp'

    # Read in the shapefile as a dataframe, make a copy of it.
    df = gpd.read_file(fname)
    result = df.copy()

    # Create a boxes from each point
    result['frame'] = df.apply(box_it, axis=1, frame_size=frame_size)

    # Rotate the box according to direction
    result = gpd.GeoDataFrame(result, geometry='frame')

    # Remove the geometry since there can only be one when writing out
    del result['geometry']

    # Copy the projection of the original dataframe
    result.crs = df.crs

    # Output to filename
    result.to_file(out_f)

if __name__ == '__main__':
    main()
