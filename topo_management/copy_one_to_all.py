from make_topos import find_basin_paths
from os.path import expanduser, basename
from os import system
import argparse


"""
Originally written to copy a file to all the basin folders e.g. think
docker-compose.yml
"""

parser = argparse.ArgumentParser(
         description='Copies one file to every folder under the basins folder'
                     ' containing the indicator_folder and indicator_file ')
parser.add_argument('file', help='Filename to copy')
parser.add_argument('--basin','-b', dest='basins',default='~/projects/basins',
                    help='Directory to copy a file to every sub directory to.')
parser.add_argument('--ind_file','-if', dest='ind_f', default=None,
                    help='If this file name is in a sub director then its a '
                         'good candidate to copy the file to')
parser.add_argument('--ind_dir','-id', dest='ind_d', default=None,
                    help='If this director name is in a sub directory then its '
                         'a good candidate to copy the file to')
args = parser.parse_args()

basins_dir = expanduser(args.basins)
copy_file = expanduser(args.file)

paths = find_basin_paths(basins_dir, indicator_folder=args.ind_d,
                                     indicator_file=args.ind_f)
print("Copying file to {} locations...".format(len(paths)))

for r in paths:
    print("Copying {} to {}".format(basename(copy_file), r))
    system("cp {} {}".format(copy_file, r))
