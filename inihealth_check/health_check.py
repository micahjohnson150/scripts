"""
Create a series of checks that will analyze past AWSM runs and raise issues
including missing output files, files that are too small, etc
"""

from datetime import datetime
import sys
import os
import glob
from collections import OrderedDict
import netCDF4 as nc

def check_missing_file(pattern, file):
    """
    Find all directories matching the pattern that are missing the file

    Args:
        pattern:    Directory pattern with path to file location
        file:       File name

    Returns:
        missing:    List of directories missing the file name
    """
    # path to file with pattern
    pf = os.path.join(pattern, file)
    # find list of directories matching pattern
    d_dir = sorted(glob.glob(pattern), key=os.path.getmtime)
    d_dir.sort(key=lambda f: os.path.splitext(f))
    # find list of directories that have the file
    d_fp = sorted(glob.glob(pf), key=os.path.getmtime)
    d_fp.sort(key=lambda f: os.path.splitext(f))
    d_fp = [os.path.dirname(d) for d in d_fp]
    # find differences in the lists
    missing = [d for d in d_dir if d not in d_fp]
    # return the directories missing the file
    return missing


def check_min_file_size(pattern, file, min_size = 1000.0):
    """
    Check the size of all files matching pattern and filename and compare
    against a minimum file size in kB

    Args:
        pattern:    Directory pattern with path to file location
        file:       File name
        min_size:   Minimum file size in kB

    Returns:
        too_small:    List of snow files that are smaller than threshold
    """
    # path to file with pattern
    pf = os.path.join(pattern, file)
    d_fp = sorted(glob.glob(pf), key=os.path.getmtime)
    d_fp.sort(key=lambda f: os.path.splitext(f))

    #sz = [os.path.getsize(d) for d in d_fp]
    # find the files that don't meet the minimum size requirements
    too_small = [d for d in d_fp if os.path.getsize(d)/min_size < min_size]

    return too_small


def check_missing_vars(pattern, file, vars):
    """
    Check netcdf files for variables that should be present. Return
    ordered dictionary of files and their missing variables

    Args:
        pattern:    Directory pattern with path to file location
        file:       File name
        vars:       List of vars to check

    Returns:
        incomplete:     Ordered dictionary of files and their missing variables
    """

    # path to file with pattern
    pf = os.path.join(pattern, file)
    d_fp = sorted(glob.glob(pf), key=os.path.getmtime)
    d_fp.sort(key=lambda f: os.path.splitext(f))

    # empty dictionary
    incomplete = OrderedDict()

    for idd, d in enumerate(d_fp):
        # read in the netcdf and get variables
        ds = nc.Dataset(d, 'r')
        keys = ds.variables.keys()
        ds.close()

        # checks keys against list of vars
        mv = [v for v in vars if v not in keys]
        if len(mv) > 0:
            incomplete[d] = mv

    return incomplete


if __name__ == '__main__':

    ### Inputs ###
    dir_pattern = '/data/blizzard/tuolumne/devel/wy2017/local_gradient/runs/run*'
    file = 'snow.nc'
    min_size = 1000.0
    vars = ['thickness', 'snow_density', 'specific_mass', 'liquid_water',
            'temp_surf', 'temp_lower', 'temp_snowcover', 'thickness_lower',
            'water_saturation']

    ### Done with inputs ###
    missing = check_missing_file(dir_pattern, file)

    too_small = check_min_file_size(dir_pattern, file, min_size=min_size)

    incomplete = check_missing_vars(dir_pattern, file, vars)

    print('\nDirectories missing {} file:'.format(file))
    for li in missing:
        print(li)

    print('\nFiles where {} file is less than {} kB:'.format(file, min_size))
    for li in too_small:
        print(li)

    print('\nFiles where {} is missing vars:'.format(file))
    for k, v in incomplete.items():
        print(k, '\t\t', v)
