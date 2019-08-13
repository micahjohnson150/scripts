from  os import listdir, walk, system
from os.path import isfile, isdir, basename, abspath, expanduser, split, getsize
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
        ops_f  = osjoin(r,"topo.nc")
        dev_f = osjoin(dev_dir,basin_name, "model_setup", "basin_setup", "topo.nc")
        ops = Dataset(ops_f)
        dev = Dataset(dev_f)
        out.msg("Checking extents of {}...".format(basin_name))

        problems_prev = problems
        for v in ["x", "y"]:

            # Check extents
            for op in ["min", "max"]:
                mo = getattr(ops.variables[v][:], op)()
                md = getattr(dev.variables[v][:], op)()

                if mo != md:
                    out.warn("\ttopo minimum in {0} direction is not the same."
                    "\n\t{1} in {0} direction off by {2} (dev - ops)"
                    "".format(v, op.title(), md-mo))
                    print("\n")
                    problems += 1

            # Check resolution
            res_diff = (dev.variables[v][0] - dev.variables[v][1]) - \
                (ops.variables[v][0] - ops.variables[v][1])

            if res_diff != 0:
                out.warn("\tCell size is not the same, off by {} (dev-ops)".format(basin_name, res_diff))
                problems +=1

        # Check for mismatching variables
        total_vars = list(ops.variables.keys()) + list(dev.variables.keys())
        missing_in_ops = [v for v in dev.variables.keys() if v not in ops.variables.keys()]
        missing_in_dev = [v for v in ops.variables.keys() if v not in dev.variables.keys()]
        if len(missing_in_ops) != 0:
            out.warn("Ops topo does not contain variable(s) - {} which were found in the dev topo.".format(", ".join(missing_in_ops)))
        if len(missing_in_dev) != 0:
            out.warn("Dev topo does not contain variable(s) - {} which were found in the ops topo.".format(", ".join(missing_in_dev)))

        # Check file size (aka datatypes)
        s = getsize(dev_f) - getsize(ops_f)
        s_p = s/getsize(ops_f)
        if s != 0:
            out.warn("\tFilesize is not the same, off by {:0.4f}Mb ({:0.2f}%)(dev-ops)".format(s/1000000, s_p*100.0))
            problems+=1
            for vz, data in ops.variables.items():
                if vz != "projection":
                    ops_type = data[:].dtype
                    dev_type = dev.variables[vz][:].dtype

                    #if ops_type != dev_type:
                    print("\t\tVariable {}: Dev type = {}, Ops type = {}".format(vz, dev_type, ops_type))
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
