# Setting Up AWSM for a Brand New Basin

## Setup
To setup a new basin for AWSM tends to be an iterative process. To follow this
guide you will need:
  * Docker/ Docker-compose installed
  * An internet connection
  * Pour points
  * URLS for downloading dem data

## Getting Started
We have written a generic makefile as a starting place for you to use.

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
