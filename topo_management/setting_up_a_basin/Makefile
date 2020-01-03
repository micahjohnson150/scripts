# If using windos comment out
uid := $$(id -u)
dem_source:= dem_source.txt
dem_img := don_pedro_dem_UTM11_WGS84.tif
pour_points := pour_points_UTM11_WGS84.bna
full_dem_extent :=
compose := $(docker-compose run -u $(uid))

dem_download:
	# Make a directory and download data to it from the National Elevation Dataset
	mkdir -p dem
	@echo Downloading
	while read img ; do \
		@echo $$img ; \
		wget -P dem -nc $$img ; \
	done <./dem_source.txt

dem_process:
	# Unzip all the dems
	unzip -u -o 'dem/*.zip' -d dem
	# Merge all images to a single image
	docker-compose run -u $(uid) cmd -c "gdal_merge.py -o dem/full_dem.img dem/*.img"
	# Reproject the image and overwrite
	docker-compose run -u $(uid) cmd -c "gdalwarp \
														-overwrite \
														-t_srs EPSG:32611 \
														-tr 10.0 10.0 -r average \
														./dem/full_dem.img \
														./dem/full_dem_UTM11_WGS84.tif"
	# Cut the dem to avoid lengthy processing
	docker-compose run -u $(uid) cmd -c "gdal_translate \
														-projwin 192430.332406 4246668.72476 \
																		 308936.219094 4170968.50051 \
					 									-of GTiff \
														./dem/full_dem_UTM11_WGS84.tif \
														./dem/$(dem_img)"
	# Clean up some processing images
	rm ./dem/full_dem.img ./dem/full_dem_UTM11_WGS84.tif

delineate:
	# Delineate the Tuolumne Subbasin and Lower Don Pedro
	docker-compose run -u $(uid) delineate -p  $(pour_points) \
						 														 -d $(dem_img) \
																				 -t 10000000 \
																				 -n 2 \
																				 --rerun

	# Preserve the Tuolumne from being overwritten
	mv ./delineation/hetch_hetchy_subbasin.* ./
	mv ./delineation/don_pedro_*_subbasin.* ./

	# Re-delineate the Cherry, Eleanor, Clavey, NorthFork Subbasins
	docker-compose run -u $(uid) delineate -p  $(pour_points) \
						 														 -d $(dem_img) \
																				 -t 2000000 \
																				 -n 2 \
																				 -strm \
																				 --rerun \
																				 --debug

	# Replace the newly made tuolumne and don pedro with the first
	mv *_subbasin.* ./delineation/

	# merge the little subbasins in the middle to form confluence
	docker-compose run -u $(uid) cmd -c \
	"ogrmerge.py -single -field_strategy FirstLayer -overwrite_ds \
	-o ./delineation/confluence_subbasin.shp ./delineation/confluence_*_subbasin.shp"

  # merge the little subbasins in the middle to form lower don pedro
	docker-compose run -u $(uid) cmd -c \
	"ogrmerge.py -single -field_strategy FirstLayer -overwrite_ds \
	-o ./delineation/don_pedro_subbasin.shp  ./delineation/don_pedro_*_subbasin.shp"

	# Clean up
	rm ././delineation/confluence_*_subbasin.shp
	rm ././delineation/don_pedro_*_subbasin.shp

topo:
	# Basin Setup
	docker-compose run -u $(uid) basin_setup -f  delineation/basin_outline.shp \
																					 -bn Tuolumne River Basin \
																					 -sb delineation/*_subbasin.shp \
																					 -dm $(dem_img) \
																					 -apd 0 0 0 220 \
																					 -d /Downloads

gis_package:
	zip  tuolumne_basin_shapefiles.zip  ./delineation/*basin_outline.* ./delineation/*_subbasin.*
