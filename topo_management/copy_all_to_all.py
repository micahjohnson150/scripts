from make_topos import find_basin_paths
import os
import sys
from topo_diff import path_split

"""
Copies a file using one pattern and to the same file to another pattern.

"""
fname = sys.argv[1]

exp_basins_dir = "~/projects/basins"
final_basins_dir = "~/projects/basin_ops"


exp_basins_dir = os.path.expanduser(exp_basins_dir)
final_basins_dir = os.path.expanduser(final_basins_dir)

if fname == "topo.nc":
    indicator_folder = "basin_setup"
else:
    indicator_folder = "model_setup"

from_paths = find_basin_paths(exp_basins_dir, indicator_folder=indicator_folder,
                                     indicator_file=fname)
to_paths = find_basin_paths(final_basins_dir, indicator_folder="topo",
                                     indicator_file="topo.nc")
print("Copying all {} in {} to {}...".format(fname, exp_basins_dir, final_basins_dir))

count = 0

for r in to_paths:
    basin_name = path_split(r)[-2]
    print("Copying file for {}".format(basin_name))
    to_f = os.path.join(r,fname)
    potential_experimentals = [d for d in from_paths if basin_name in d]

    # watchout for multiple or zero matches
    if len(potential_experimentals) > 1:
        print("Warning! Multiple new {}s were found for {}, skipping".format(fname, basin_name))
        print("\n\t".join(potential_experimentals))

    elif len(potential_experimentals) == 0:
        print("No new {} were found for {}.".format(fname, basin_name))

    else:

        from_f = os.path.join(potential_experimentals[0],fname)

        print("Copying {} to {}".format(from_f, to_f))
        os.system("cp {} {}".format(from_f, to_f))
        count+=1
    print("\n")
print("Copied {} {} files to {} from {}".format(count, fname, final_basins_dir, exp_basins_dir))
