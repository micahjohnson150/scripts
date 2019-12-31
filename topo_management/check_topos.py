#!/usr/bin/env python3

from os import listdir, walk, system
from os.path import isfile, isdir, basename, abspath, expanduser, split, getsize
from os.path import join as osjoin
from subprocess import check_output, Popen
from basin_setup.basin_setup import Messages
from make_topos import find_basin_paths
from netCDF4 import Dataset
from topo_diff import path_split
import argparse


"""
Every basin in my basin folder which is of similar structure (<basin>/model_setup/Makefile)

This script will go through all the basin topos and check the extents and
projections compared to that in the basin_ops repo.

e.g.
    python check_all_topos.py

To run a single basin of a collection of basins, the script takes a string
arg and looks for it in the paths when theyre collected.

e.g.
    python check_all_topos.py tuolumne

"""



out = Messages()

if __name__ == "__main__":

    # Director of interest
    ops_dir = "~/projects/basin_ops"
    dev_dir = "~/projects/basins"


    parser = argparse.ArgumentParser(description="Compare our committed basin"
                                    " topos to the development topos.")
    parser.add_argument('--keyword','-kw', dest='kw',
                        help='Filter basin_ops paths for kw e.g. tuolumne will'
                             ' find only one topo to process')

    args = parser.parse_args()

    ops_paths = find_basin_paths(ops_dir, indicator_folder="topo",
                                          indicator_file="topo.nc")

    ops_dir = abspath(expanduser(ops_dir))
    dev_dir = abspath(expanduser(dev_dir))

    out.msg("Comparing topos in {} to topos in {}...".format(dev_dir, ops_dir))

    msg = "{0:<50}{1:<30}"
    hdr = msg.format("Warning","Difference (dev - ops)")
    border = "=" * len(hdr)

    # Check for basin name specifically by user
    if args.kw != None:
        ops_paths = [p for p in ops_paths if args.kw in p]

        # Wanr user if no matches found
        if len(ops_paths) == 0:
            out.error('{} not found in any ops paths'.format(args.kw))

    for r in ops_paths:
        basin_name = path_split(r)[-2]
        ops_f  = osjoin(r,"topo.nc")
        dev_f = osjoin(dev_dir,basin_name, "model_setup", "basin_setup", "topo.nc")
        ops = Dataset(ops_f)
        dev = Dataset(dev_f)
        out.msg("Checking extents of {}...".format(basin_name))

        warnings = []
        dimensional_issue = False

        for v in ["x", "y"]:

            # Check extents
            for op in ["min", "max"]:

                # Check the coordinates
                mo = getattr(ops.variables[v][:], op)()
                md = getattr(dev.variables[v][:], op)()

                if mo != md:
                    report = ("{0} in {1} direction is not the same."
                            "".format(op.title(), v.title()))
                    diff = "{:0.4f}".format(md-mo)
                    warnings.append(msg.format(report, diff))

            # Check number of cells
            dn = dev.variables[v].shape[0]
            on = ops.variables[v].shape[0]
            diff = dn - on

            if diff != 0:
                report = "n{} is not the same.".format(v)
                warnings.append(msg.format(report, diff))
                dimensional_issue = True

            # Check resolution
            res_diff = (dev.variables[v][0] - dev.variables[v][1]) - \
                (ops.variables[v][0] - ops.variables[v][1])

            if res_diff != 0:
                report = "Cell size is not the same."
                warnings.append(msg.format(report, res_diff))

        # Check for mismatching variables
        total_vars = list(ops.variables.keys()) + list(dev.variables.keys())
        missing_in_ops = [v for v in dev.variables.keys() if v not in ops.variables.keys()]
        missing_in_dev = [v for v in ops.variables.keys() if v not in dev.variables.keys()]

        # Grab all missing to avoid key errors
        missing_in_either = missing_in_dev + missing_in_ops

        # Report missing issues
        if len(missing_in_ops) != 0:
            report = "Ops topo does not contain Dev variable(s)"
            diff = ", ".join(missing_in_ops)
            warnings.append(msg.format(report, diff))

        if len(missing_in_dev) != 0:
            report = "Dev topo does not contain Ops variable(s)."
            diff = ", ".join(missing_in_dev)
            warnings.append(msg.format(report, diff))

        # Check file size/ datatypes (aka datatypes)
        s = getsize(dev_f) - getsize(ops_f)
        s_p = s/getsize(ops_f)

        if s != 0:
            report = "Filesize is not the same."
            diff = "{:0.4f}Mb ({:0.2f}%)".format(s/1000000, s_p * 100.0)
            warnings.append(msg.format(report, diff))

            for vz, data in ops.variables.items():
                if vz != "projection" and vz not in missing_in_either:

                    # Check data types
                    ops_type = data[:].dtype
                    dev_type = dev.variables[vz][:].dtype

                    if ops_type != dev_type:
                        report ="{} data type mismatch".format(vz)
                        diff = "Dev type = {}, Ops type = {}".format(dev_type, ops_type)
                        warnings.append(msg.format(report, diff))

                    # Check data differences on same sized domains
                    if vz not in ['x','y'] and not dimensional_issue:
                        diff = (dev.variables[vz][:] - ops.variables[vz][:]).mean()

                        if diff != 0:
                            report = "{} not the same.".format(vz)
                            diff = "{:0.5f} (mean)".format(diff)
                            warnings.append(msg.format(report, diff))


        if len(warnings) != 0:
            out.warn("{} differences found in {} topo.".format(len(warnings), basin_name))
            print(hdr)
            print("=" * len(hdr))
            for w in warnings:
                print(w)
            print("")
        else:
            out.respond("No differences found!")

        ops.close()
        dev.close()
        #input("press enter to continue")

    msg = "Checked {} basins".format(len(ops_paths))

    if len(ops_paths) == 0:
        out.warn(msg)
    else:
        out.msg(msg)
