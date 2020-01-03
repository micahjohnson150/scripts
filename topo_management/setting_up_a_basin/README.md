# Setting Up AWSM for a Brand New Basin
Currently this setup is only describing how to get data for the US. That really
only means that we have streamlined the data for the US and that there are some
extra modifications for outside the US.


## Getting Started
We have written a generic makefile and project for you to use. The project
is a working example which should be edited to meet your projects needs.

1. The first step is to copy the folder new_basin.
2. 


## Getting DEM Data for the US
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
Feel free to edit the contents of the variables at the top of the Makefile to
get the results desired.

1. DEM_SOURCE - Text file containing URLS to dem tiles to download
2. BASIN_NAME - Name to use for naming files, and the proper name in the final topo
3. POUR_POINTS - BNA file containing names of pour points which is used to name subbasins, Coordinates must be in EPSG Coordinates
4. EPSG - EPSG code representing the projection information. Currently AWSM only supports UTM
5. MAX_EXTENT - Maximum extent to delineate on for the dem. Must be in same Coordinates as EPSG
6. DELINEATE_THRESHOLD - Number of cells draining into an area to constitute a subbasin (Bigger # == Bigger Subbasins)
7. DELINEATE_RESOLUTION - Cellsize resolution used for delineation (Meters)
8. NTHREADS - Number of processes to launch for delineating the basin

## Setup
To setup a new basin for AWSM tends to be an iterative process. To follow this
guide you will need:
  * Docker/ Docker-compose installed
  * An internet connection
  * Pour points
  * URLS for downloading dem data
