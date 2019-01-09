from netCDF4 import Dataset, num2date, date2num
import os
import datetime as dt
import argparse
import numpy as np
import pandas as pd


def calculate_date_from_wyhr(wyhr, year):
    """
    Takes in the integer of water year hours and an integer year and
    returns the date
    """

    start = datetime.datetime(year=year-1, month=10, day=1)

    delta = datetime.timedelta(hours=wyhr)
    return start + delta


def subset_netcdf(infile, outfile, tstep=None, dim_exclude=None, exclude=None):
    """
    Copies a netcdf from one to another exactly.

    Args:
        infile: filename you want to copy or can also be instantiated dataset object
        outfile: output filename
        tstep: Time step to subset
        exclude: variables to exclude
        dim_exclude: Dimensions to exclude

    Returns the output netcdf dataset object for modifying
    """
    if type(exclude) != list:
        exclude = [exclude]

    dst = Dataset(outfile, "w")

    if type(infile) == str:
        src = Dataset(infile,'r')
    else:
        src = infile

    # Figure out the timestep
    t_index = src.variables['time'] == tstep

    # copy global attributes all at once via dictionary
    dst.setncatts(src.__dict__)

    # copy dimensions
    for name, dimension in src.dimensions.items():
        if name not in dim_exclude:
            dst.createDimension(name, (len(dimension) if not dimension.isunlimited() else None))

    # copy all file data except for the excluded
    for name, variable in src.variables.items():

        if name.lower() not in exclude and name.lower() not in dim_exclude:
            new_dims = [d for d in variable.dimensions if d not in dim_exclude]
            dst.createVariable(name, variable.datatype, new_dims)
            # Copy variable attributes all at once via dictionary
            dst.variables[name].setncatts(src.variables[name].__dict__)

            # Time series image data
            if len(variable.dimensions) == 3:
                dst.variables[name][:] = src.variables[name][t_index,:]

            elif 'projection' in name.lower():
                dst.variables[name] = src.variables[name]

            # 1D dimensional data
            else:
                dst.variables[name][:] = src.variables[name][:]

    return dst


def main():
    p = argparse.ArgumentParser(description="Splits a netcdf by date then writes"
                                             " a netcdf for each timestep")

    p.add_argument('-f','--netcdf', dest='netcdf',
                        required=True,
                        help="Path to a netcdf you want to split")

    p.add_argument('-o','--output', dest='output',
                        required=False,
                        default='output.nc',
                        help="Path to output your split netcdf files"
                        "")


    args = p.parse_args()

    src = Dataset(args.netcdf)
    dates = num2date(src.variables['time'][:],
                    units=src.variables['time'].units,
                    calendar=src.variables['time'].calendar)
    for i,v in enumerate(dates):
        fname = '{0}_{1}.nc'.format((args.netcdf).split('.')[0], v.strftime('%Y%m%dT%H%M'))
        print(fname)
        dst = subset_netcdf(src, fname, src.variables['time'][i], dim_exclude=['time'])
        dst.close()
# from geoserver.catalog import Catalog
# cat = Catalog("http://ubuntu@ec2-35-172-236-77.compute-1.amazonaws.com/8600/geoserver/rest", password='nwrc10')
# all_stores = cat.get_workspace('topo')
if __name__ == '__main__':
    main()
