"""
Seek out the veg maps, create a dataframe of the unique veg values
Extract the veg params and create a mask to over lay on QGIS.


Usage:
    python gather_veg_values.py

output:
    * nccopy topos veg_type to a nearer location
    * veg_map_sierras.csv which is a unique list of veg data from the basins

"""

from os.path import isdir,join, dirname, expanduser, abspath, basename
import pandas as pd
from netCDF4 import Dataset
import os
from subprocess import check_output
import shutil


def main():
    basins = ['tuolumne', 'sanjoaquin']
    projects_path = "~/projects/m3works/basins"
    output = 'veg_masks'

    # Conlidate paths make them absolute
    projects_path = abspath(expanduser(projects_path))
    pbasins = [join(projects_path, b) for b in basins]

    search_file = 'veg_map.csv'
    setup_folder = 'topo'

    print("\nGathering veg maps for {}".format(", ".join(basins)))
    df = pd.DataFrame(columns=['VALUE','HEIGHT','CLASSNAME'])

    topo = {}

    for i,b in enumerate(pbasins):

        print("Working in {}".format(b))
        path = join(b, setup_folder, "basin_setup", search_file)
        tdf = pd.read_csv(path)
        new = set(tdf['VALUE'].values)
        old = set(df['VALUE'].values)
        missing = [v for v in new if v not in old]

        # Add the missing values to the collecting Dataframe
        ind = tdf['VALUE'].isin(missing)
        print("Adding {} veg values...".format(len(tdf[ind])))
        df = df.append(tdf[ind], ignore_index=True, sort=False)

        topo[basins[i]] = join(b, setup_folder, "basin_setup", "topo.nc")

    # Output the dataframe
    df.to_csv("veg_map_sierras.csv")


    # Manage output paths
    output = "veg_masks"
    temp = "temp"

    for d in [temp,output]:
        if isdir(d):
            print("Removing {}".format(d))
            shutil.rmtree(d)

        print("Creating {}".format(d))
        os.makedirs(d)

    # Extract the veg_type and convert to tif
    for basin, path in topo.items():
        out_f = join(output, "{}_topo.nc".format(basin))

        # Copy over only the veg_type
        cmd = "nccopy {} {} -V veg_type,projection,x,y".format(path, out_f)
        run(cmd)

    print("Complete!\n")

def run(cmd):
    """
    runs a cmd through the shel and prints it out
    """
    print(cmd)
    check_output(cmd, shell=True)

if __name__ == "__main__":
    main()
