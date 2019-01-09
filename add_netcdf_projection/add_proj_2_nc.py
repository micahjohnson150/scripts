from netCDF4 import Dataset
import argparse
import os.path
from urllib.request import urlopen
import re


def strip_chars(edit_str, bad_chars='[(){}<>,"_]=\nns'):
    result = ''.join([s for s in edit_str if s not in bad_chars])
    print(result)
    return result


def gather_utm_meta(epsg_str,epsg):
    """
    Use if the EPSG data is associated to UTM
    Gathers the data and returns a dictionary of data and attributes that need
    to be added to the netcdf based on
    https://www.unidata.ucar.edu/software/thredds/current/netcdf-java/reference/StandardCoordinateTransforms.html

    """
    meta = epsg_str.lower()

    map_meta = {
                    "grid_mapping_name": "universal_transverse_mercator",
                    "utm_zone_number": None,
                    "semi_major_axis": None,
                    "inverse_flattening": None,
                    'spatial_ref':epsg_str,
                    "_CoordinateTransformType": "projection",
                    "_CoordinateAxisTypes": "GeoX GeoY"}

    # Assign the zone number
    zone_str = meta.split('zone')[1]
    map_meta['utm_zone_number'] = float((strip_chars(zone_str.split(',')[0])).strip()[-2:])

    # Assign the semi_major_axis
    axis_string = meta.split('spheroid')[1]
    map_meta['semi_major_axis'] = float(axis_string.split(',')[1])

    # Assing the flattening
    map_meta["inverse_flattening"] = float(strip_chars(axis_string.split(',')[2]))

    return map_meta


def copy_nc(infile, outfile, exclude=None):
    """
    Copies a netcdf from one to another exactly.

    Args:
        infile: filename you want to copy
        outfile: output filename
        toexclude: variables to exclude

    Returns the output netcdf dataset object for modifying
    """
    if type(exclude) != list:
        exclude = [exclude]

    dst = Dataset(outfile, "w")

    with Dataset(infile) as src:

        # copy global attributes all at once via dictionary
        dst.setncatts(src.__dict__)

        # copy dimensions
        for name, dimension in src.dimensions.items():
            dst.createDimension(
                name, (len(dimension) if not dimension.isunlimited() else None))

        # copy all file data except for the excluded
        for name, variable in src.variables.items():
            if name not in exclude:
                dst.createVariable(name, variable.datatype, variable.dimensions)
                dst[name][:] = src[name][:]

                # copy variable attributes all at once via dictionary
                dst[name].setncatts(src[name].__dict__)
    return dst


def add_proj(nc_obj,epsg):
    """
        Adds the appropriate attributes to the netcdf for managing projection info

        Args:
        nc_obj: netCDF4 dataset object needing the projection information
        epsg:   projection information to be added
        Returns:
        nc_obj: the netcdf object modified
    """
    # function to generate .prj file information using spatialreference.org
    # access projection information
    try:
        wkt = urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg))
    except:
        wkt = urlopen("http://spatialreference.org/ref/sr-org/{0}/prettywkt/".format(epsg))

    # remove spaces between charachters
    remove_spaces = ((wkt.read()).decode('utf-8')).replace(" ","")
    # Add in the variable for holding coordinate system info
    map_meta = parse_wkt(remove_spaces,epsg)

    nc_obj.createVariable("projection","S1")
    nc_obj["projection"].setncatts(map_meta)

    for name,var in nc_obj.variables.items():

        # Assume all 2D+ vars are the same projection
        if 'x' in var.dimensions and 'y' in var.dimensions:
            print("Adding Coordinate System info to {0}".format(name))
            nc_obj[name].setncatts({"grid_mapping":"projection"})

        elif name.lower() in ['x','y']:
            # Set a standard name, which is required for recognizing projections
            nc_obj[name].setncatts({"standard_name":"projection_{}_coordinate"
            "".format(name.lower())})
            # Set the units
            nc_obj[name].setncatts({"units":"meters"
            "".format(name.lower())})


    return nc_obj


def parse_wkt(epsg_string,epsg):
    """
    """
    map_meta = {}
    wkt_data = (epsg_string.lower()).split(',')

    if 'utm' in epsg_string.lower():
        map_meta = gather_utm_meta(epsg_string,epsg)
    print(" Meta information to be added...\n")
    for k,v in map_meta.items():
        print(k,repr(v))
    return map_meta


def main():
    p = argparse.ArgumentParser(description= "Add projection information to a"
                                             " netcdf based on filename and "
                                             " epsg code. Makes it readable for"
                                             " geoserver")

    p.add_argument('-f','--netcdf', dest='netcdf',
                        required=True,
                        help="Path to a netcdf you want to add projection "
                        "information to")

    p.add_argument('-o','--output', dest='output',
                        required=False,
                        default='output.nc',
                        help="Path to output your netcdf containing projection info"
                        "")

    p.add_argument('-e','--epsg', dest='epsg',
                        required=True,
                        type=str,
                        help="EPSG value representing the projection information to"
                        "add to the netcdf")

    args = p.parse_args()


    infile = os.path.abspath(args.netcdf)
    outfile = os.path.abspath(args.output)
    outds = copy_nc(infile, outfile)
    outds = add_proj(outds,args.epsg)
    outds.sync()
    outds.close()

if __name__ =='__main__':
    main()
