from osgeo import ogr
import os




input_dir = "/home/micahjohnson/projects/basins/"
driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
out_fname = 'centroids.shp'
# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(out_fname)

outDataSource = outDriver.CreateDataSource(out_fname)
layer = outDataSource.CreateLayer("centroids", geom_type=ogr.wkbPoint)
field_name = ogr.FieldDefn("name", ogr.OFTString)
field_name.SetWidth(24)
layer.CreateField(field_name)

layer.CreateField(ogr.FieldDefn("SWE", ogr.OFTReal))

for root, directories, filenames in os.walk(input_dir):
    for f in filenames:
        if "delineation" in root.lower():
            if f.split(".")[-1] == 'shp' and "basin" in f:
                name = 
                # Open the file
                dataSource = driver.Open(fname, 0)
                linelyr = dataSource.GetLayer()
                f = linelyr.GetFeature(0)
                g = f.geometry()
                g.GetPoint()
                c = g.Centroid()

                # Add data
                feature = ogr.Feature(layer.GetLayerDefn())
                feature.SetField("name", "test")
                feature.SetGeometry(centroid)
                layer.CreateFeature(feature)

                feature.Destroy()

data_source.Destroy()
