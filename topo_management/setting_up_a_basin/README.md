# Setting Up AWSM for a Brand New Basin
Currently this setup is only describing how to get data for the US. That really
only means that we have streamlined the data for the US and that there are some
extra modifications required for outside the US. This namely applies to vegetation data.

## Requirements
To setup a new basin for AWSM tends to be an iterative process. To follow this
guide you will need:
  * Docker/ Docker-compose installed
  * An internet connection
  * Pour points
  * URLS for downloading dem data

## Getting Started
We have written a generic makefile and project for you to use. The project
is a working example which should be edited to meet your projects needs.
Below is the high level overview of what to edit. These are followed by a
more info on each

The first step is to copy the folder new_basin and open it. Then:
1. Edit the file pour_points.bna
2. Edit the file dem_sources.txt
3. Edit the Makefile

## Add Pour Points (pour_points.bna)
Adding pour points will dictate big your basin is. There is not a limit to the
number of pour points used but there is a limitation on how many will be
represented based on the delineation threshold used. The name given to a pour
point is used to name the subbasin so name the pour point sensically.

## Getting DEM Data for the US (dem_source.txt)
* Go to https://viewer.nationalmap.gov/basic/
* Select Elevation Products
* Select 1/3 arc second-dem and under format select img data
* Zoom in on the map to approximately the area of interest.
* Select Find Products
* Under the Available products use the foot print link on each tile to see which tiles are necessary
* When you find a tile, add it to your shopping cart.
* When you are finished, Select Save as text.
* Move the file to this folder and rename to dem_sources.txt

## Makefile Inputs
The top of the Makefile has several inputs variables which can be edited without
much concern for raising errors. They are:

1. DEM_SOURCE - Text file containing URLS to dem tiles to download
2. BASIN_NAME - Name to use for naming files, and the proper name in the final topo
3. POUR_POINTS - BNA file containing names of pour points which is used to name subbasins, Coordinates must be in EPSG Coordinates
4. EPSG - EPSG code representing the projection information. Currently AWSM only supports UTM
5. MAX_EXTENT - Maximum extent to delineate on for the dem. Must be in same Coordinates as EPSG
6. DELINEATE_THRESHOLD - Number of cells draining into an area to constitute a subbasin (Bigger # == Bigger Subbasins)
7. DELINEATE_RESOLUTION - Cellsize resolution used for delineation (Meters)
8. NTHREADS - Number of processes to launch for delineating the basin

There are several make commands which can be used.

1. download_dem - Downloads the data in the dem_sources.txt
2. dem_process - Make the full reprojected DEM mosaic in the project dictated by EPSG
3. delineate - Delineate the basin using the full dem, pour points, and delineation threshold
4. topo - makes the static input netcdf for AWSM known as the topo.nc
5. gis_package - creates a zip file of all the shapefiles created in the delineation
6. qgis - Create a hillshade from the dem and make a colormap for it
7. clean_all - delete all the generated data, CAUTION: This deletes the downloads too.
