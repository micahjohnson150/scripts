from  os import listdir, walk, system
from os.path import isfile, isdir, basename, abspath, expanduser, split
from os.path import join as osjoin
from subprocess import check_output, Popen
import sys
from basin_setup.basin_setup import Messages
from make_all_topos import find_basin_paths
from netCDF4 import Dataset
from topo_diff import path_split
"""
Every basin in my basin folder which is of similar structure (<basin>/model_setup/Makefile)

This script will go through all the basin topos and check the extents and
projections compared to that in the basin_ops repo.

e.g.
    python check_all_topos.py

"""


out = Messages()

if __name__ == "__main__":

    # Director of interest
    ops_dir = "~/projects/basin_ops"
    dev_dir = "~/projects/basins"

    ops_paths = find_basin_paths(ops_dir, indicator_folder="topo",
                                          indicator_file="topo.nc")

    ops_dir = abspath(expanduser(ops_dir))
    dev_dir = abspath(expanduser(dev_dir))
    problems = 0
    basin_problems = 0
    counts = 0
    out.msg("Comparing topos in {} to topos in {}...".format(dev_dir, ops_dir))

    for r in ops_paths:
        basin_name = path_split(r)[-2]
        ops = Dataset(osjoin(r,"topo.nc"))
        dev = Dataset(osjoin(dev_dir,basin_name,"model_setup","basin_setup","topo.nc"))
        out.msg("Checking extents of {}...".format(basin_name))

        # Check extents
        problems_prev = problems
        for op in ["min","max"]:
            for v in ["x","y"]:
                mo = getattr(ops.variables[v][:], op)()
                md = getattr(dev.variables[v][:], op)()
                if mo != md:
                    out.warn("{0} topo minimum in {1} direction is not the same."
                    "\n{2} in {1} direction off by {3} (dev - ops)"
                    "".format(basin_name, v, op.title(), md-mo))
                    print("\n")
                    problems += 1

        if problems_prev != problems:
            basin_problems += 1

        ops.close()
        dev.close()
        #input("press enter to continue")

    msg = "Checked {} basins".format(len(ops_paths))

    if len(ops_paths) == 0:
        out.warn(msg)
    else:
        out.msg(msg)
    out.msg("Encountered {} problems across {} basin(s)".format(problems,
                                                                basin_problems))
