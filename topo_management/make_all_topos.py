from  os import listdir, walk, system
from os.path import isfile, isdir, basename, abspath, expanduser, split
from subprocess import check_output, Popen
import sys

def find_basin_paths(directory, indicator_folder="model_setup", indicator_file="Makefile"):
    """
    Walks through all the folder in directory looking for a directory called
    model setup, then checks to see if there is a Makefile, if there is then append
    that path to a list and return it
    """
    paths = []
    directory = abspath(expanduser(directory))

    # Get all the folders and stuff just one level up
    for r, d, f in walk(directory):
        if basename(r) == indicator_folder:

            if indicator_file in f:
                paths.append(r)

    return paths


if __name__ == "__main__":

    # Grab a command passed in
    make_cmd = sys.argv[1]

    # Director of interest
    basins_dir = "~/projects/basins"

    count = 0
    basins_attempted = 0
    failures = 0


    print("Looking in {} for basins with makefiles...".format(basins_dir))

    for r in find_basin_paths(basins_dir, indicator_folder="model_setup", indicator_file="Makefile"):
        topo_attempt = False
        try:
            cmd = "cd {} && make {}".format(r, make_cmd)
            print(cmd)
            s = Popen(cmd, shell=True)
            s.wait()
            topo_attempt = True

        except Exception as e:
            raise e

        if topo_attempt:
            basins_attempted += 1
        else:
            failures +=1
        #input("press enter to continue")
    print("Attempted to build {} topos".format(basins_attempted + failures))
    print("Failed to build {} topos".format(failures))
