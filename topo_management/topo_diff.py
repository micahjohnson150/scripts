from make_topos import find_basin_paths
import os
from os.path import split
import matplotlib.pyplot as plt
import subprocess as sp
from netCDF4 import Dataset
import datetime
from shutil import rmtree

"""
After running make_all_topos topo use this script to examine changes that
occurred; creating diff.nc, figures of non-zero mean results.
This script will overwrite the results everytime it is ran.

"""

def path_split(path):
    path = os.path.normpath(path)
    path = path.split(os.sep)
    return path

if __name__ == "__main__":
    # Location where new topos were made
    new_topos_dir = "~/projects/basins"
    experimental_dirs = find_basin_paths(new_topos_dir, indicator_folder="basin_setup", indicator_file="topo.nc")

    # Locations of topos we want to check against
    topo_dirs = "~/projects/basin_ops"
    original_dirs = find_basin_paths(topo_dirs, indicator_folder="topo", indicator_file="topo.nc")

    # built on the structure of basin_ops repo
    for original in original_dirs:

        basin_name = path_split(original)[-2]
        print("Working on {}".format(basin_name))

        orig_topo = os.path.join(original,"topo.nc")
        potential_experimentals = [d for d in experimental_dirs if basin_name in d]

        # watchout for multiple or zero matches
        if len(potential_experimentals) > 1:
            print("Warning multiple new topos were found for {}, skipping".format(basin_name))
            print("\n\t".join(potential_experimentals))

        elif len(potential_experimentals) == 0:
            print("No experimental topos were found for {}.".format(basin_name))

        else:
            # Nail down the file name were differencing, and output location
            exp_topo = os.path.join(potential_experimentals[0],"topo.nc")
            output = os.path.join((os.sep).join(path_split(exp_topo)[0:-3]),"analysis","topo_changes")

            if os.path.isdir(output):
                print("Removing preexisting data...")
                rmtree(output)

            os.makedirs(output)
            diff_f = os.path.join(output,"topo_diff.nc")

            cmd = "ncdiff -O {} {} {}".format(exp_topo,orig_topo,diff_f)
            print("Creating difference topo...")
            #print(cmd)
            try:
               s = sp.check_output(cmd, shell=True)
               broke = False
               print("Difference successful!")
            except Exception as e:
               print(e)
               broke = True


            # Perform stats and plots
            if not broke:
                ds = Dataset(diff_f)
                for v, data in ds.variables.items():
                    if v not in ['time','x','y', 'projection']:

                        # Calculate some stats
                        stats = {"mean":None,"min":None,"max":None,"std":None}
                        for stat in stats.keys():
                            #print("Calculating {} on {} for {}".format(stat,v,basin_name))
                            stats[stat] = getattr(data[:], stat)()

                        if stats["mean"] != 0:
                            print("Non-zero mean found on the difference for {}!".format(v))
                            plt.figure(figsize=(8,8))
                            plt.imshow(data[:])
                            plt.suptitle("Topo Diff for {} on {} performed {}"
                                         "".format(basin_name, v, datetime.datetime.today().date()),
                                         y=0.980, fontsize=15)

                            plt.title(" Mean = {:0.3f}, Min = {:0.3f}, Max = {:0.3f}, STD = {:0.3f}"
                                      "".format(stats["mean"],
                                                stats["min"],
                                                stats["max"],
                                                stats["std"]),
                                                fontsize=12)
                            plt.colorbar()
                            plt.tight_layout()
                            fig_f = "{}_{}_topo_diff.png".format(basin_name,
                                                                     v)
                            fig_f = os.path.join(output, fig_f).replace(" ","_")
                            print("Outputting results to {}".format(fig_f))
                            plt.savefig(fig_f)
                            plt.close()
        print("\n")
