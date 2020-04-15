'''
Confirms that the gold config produces matching netcdfs as to what is in
the repo
'''
import subprocess as sp
import sys
from netCDF4 import Dataset
from os.path import join, abspath, expanduser
import os
import argparse

__version__ = '0.1.0'

parser = argparse.ArgumentParser(
description='Checks for differences in gold files and develop files.')

parser.add_argument('dev_dir', metavar='dev_dir', type=str,
help='Path a directory containing a set of netcdfs that are in development')

parser.add_argument('gold_dir', metavar='gold_dir', type=str,
help='Path a directory containing a set of netcdfs that are considered gold files')

parser.add_argument('-d', dest='debug', action='store_true',
help='Whether to clean up files or not')
args = parser.parse_args()

hdr = 'Gold File Checker v{}'.format(__version__)
banner = '=' * len(hdr)
print(banner)
print(hdr)
print(banner)

# Location to the gold files and config
dev_dir = abspath(expanduser(args.dev_dir))
gold_dir = abspath(expanduser(args.gold_dir))

# List all the files in the locations, filter on netcdf

dev_files = os.listdir(dev_dir)
gold_files = os.listdir(gold_dir)

common_netcdfs = [f for f in dev_files if f in gold_files and f.split('.')[-1]=='nc']

for f in common_netcdfs:
    fname = join(dev_dir, f)
    gfname = join(gold_dir, f)
    diff_f = join(dev_dir, 'diff.nc')
    diff_cmd = 'ncdiff -O {} {} {}'.format(fname, gfname, diff_f)
    print('Executing:')
    print('\n' + diff_cmd)
    sp.check_output(diff_cmd, shell=True)

    cmd = 'nc_stats {} -p 8'.format(diff_f)
    out = sp.check_output(cmd, shell=True)
    print(out.decode('utf-8'))

if not args.debug:
    print('Cleaning up files...')
    cmd = 'rm {}'.format(diff_f)
    sp.check_output(cmd, shell = True)
