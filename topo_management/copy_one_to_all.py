from make_all_topos import find_basin_paths
import os

"""
Copies a file to all the basin folders, Originally designed for docker-compose
files
"""

basins_dir = "~/projects/basins"
copy_file = "~/projects/basins/tuolumne/model_setup/docker-compose.yml"


copy_file = os.path.expanduser(copy_file)
basins_dir = os.path.expanduser(basins_dir)

paths = find_basin_paths(basins_dir, indicator_folder="model_setup",
                                     indicator_file="Makefile")
print("Copying file to {} locations...".format(len(paths)))

for r in paths:
    print("Copying {} to {}".format(os.path.basename(copy_file), r))
    os.system("cp {} {}".format(copy_file, r))
