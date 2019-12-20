from make_all_topos import find_basin_paths
import numpy as np
import matplotlib.pyplot as plt
import sys
from os.path import abspath, expanduser
from os.path import join as pjoin
from basin_setup.basin_setup import Messages
from netCDF4 import Dataset
from topo_diff import path_split
import time
import pandas as pd
import os
import shutil


if __name__ == "__main__":
    s = time.time()
    out = Messages()
    var = sys.argv[1]

    # Directory of interest
    basin_dir = "~/projects/basins"
    basin_dir = abspath(expanduser(basin_dir))

    out_dir = "~/projects/basins/sierras/analysis/topo_{}_unique".format(var)
    out_dir = abspath(expanduser(out_dir))

    basin_paths = find_basin_paths(basin_dir, indicator_folder="basin_setup",
                                          indicator_file="topo.nc")
    if os.path.isdir("~/projects/basins/sierras/analysis"):
        shutil.rmtree(out_dir)

    out.msg("Making {} histograms for {} topo files..."
            "".format(var, len(basin_paths)))

    # Setup a dataframe with var as the index and baisns as the columns
    unique_var_all = []
    basins = [path_split(r)[-3] for r in basin_paths]
    total_cells = 0
    out.msg("Aggregating all unique {} values on {} topos".format(var, len(basin_paths)))

    for r in basin_paths:
        topo_f = pjoin(r, "topo.nc")
        ds = Dataset(topo_f)
        unique = np.unique(ds.variables[var][:])
        unique_var_all += list(unique)
        shape = ds.variables[var][:].shape
        basin_pixels = shape[0]*shape[1]
        total_cells += basin_pixels
        ds.close()

    unique = sorted(list(set(unique)))
    out.msg("{} unique {} values across all topos.".format(len(unique),var))
    df = pd.DataFrame(columns=basins, index=unique)
    pixels = {}
    
    for r in basin_paths:
        out.msg('Working on {}'.format(r))
        topo_f = pjoin(r, "topo.nc")
        ds = Dataset(topo_f)
        basin_name = path_split(r)[-3]
        basin_pixels = shape[0]*shape[1]
        pixels[basin_name] = basin_pixels
        for v in unique:
            df[basin_name].loc[v] = (ds.variables[var][:]==v).sum()

        ds.close()

    # Create the output dir.
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)

    os.mkdir(out_dir)

    # Export only the ops basins
    ops = ["merced","don_pedro","sanjoaquin","kings","kaweah"]
    df_ops = df[ops].copy()
    # df_ops = df_ops.div(total_cells)
    #ind = df_ops >= 0.01
    df_ops['total'] = df.sum(axis=1)
    df_ops = df_ops.sort_values(by="total")
    df_ops[ops].plot(kind='bar',figsize=(10,8), title="Histogram of {} in pixel count".format(var))


    out.msg("\nPercent of Pixels containing the vegtypes:")
    df_ops['percent coverage'] = (df_ops["total"].sort_values()/total_cells)*100.0

    # Make a percentage count

    plt.savefig(pjoin(out_dir, "{}_histogram.png".format(var)))

    df_ops.to_csv(pjoin(out_dir,"{}_count.csv".format(var)))

    out.msg("Complete! Elapsed {:0.0f}s".format(time.time()-s))
