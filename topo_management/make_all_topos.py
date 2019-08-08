from  os import listdir, walk, system
from os.path import isfile, isdir, basename
from subprocess import check_output
import sys

count = 0
make_cmd = sys.argv[1]
basins_attempted = 0

# Get all the folders and stuff just one level up
for r, d, f in walk("../"):
    topo_attempt = False
    if basename(r) == "model_setup":
        if "Makefile" in f:
            print("Building Topo for {}".format(os.split(r))[-2])
            system("cd {} && make {}".format(r, make_cmd))
            topo_attempt = True
    if topo_attempt:
        basins_attempted += 1

print("Attempted to build {} topos".format(basins_attempted))
