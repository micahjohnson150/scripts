#!/usr/bin/env python3

from os import listdir, walk, system
from os.path import isfile, isdir, basename, abspath, expanduser, split
from subprocess import check_output, Popen
import argparse
from basin_setup.basin_setup import Messages

"""
Every basin in my basin folder has a make file and each is constructed similarly.
Thie script will go through all the basin topos with a make file and execute
make < arg >

The following executes all the topos makefiles via make topo in every basin folder
e.g.
    python make_topos.py topo


The following only runs the make topo command on tuolumne
e.g.
    python make_topos.py topo -kw tuolumne

"""
out = Messages()

def has_hidden_dirs(p):
    """
    Searches a string path to determine if there are hidden
    """
    has_hidden_paths = False
    for d in p.split('/'):
        if d:
            if d[0] == '.':
                has_hidden_paths = True
    return has_hidden_paths


def find_basin_paths(directory, indicator_folder="model_setup", indicator_file="Makefile"):
    """
    Walks through all the folder in directory looking for a directory called
    model setup, then checks to see if there is a Makefile, if there is then append
    that path to a list and return it
    """
    paths = []
    directory = abspath(expanduser(directory))

    # Allow for indicator files and dirs to be none
    no_ind_file = (indicator_folder == None and indicator_file != None)
    no_ind_dir = (indicator_folder != None and indicator_file == None)
    no_dir_or_file = (indicator_folder == None and indicator_file == None)

    # Get all the folders and stuff just one level up
    for r, d, f in walk(directory):

        # ignore hidden folders and the top level folder
        if not has_hidden_dirs(r) and r != directory:
            if (
               # If no indicator file or directories append the path
               no_dir_or_file or \

               # no indicatory file is available only check the indicator folder
               (no_ind_file and basename(r) == indicator_folder) or \

               # if no indicator folder is available only check file
               (no_ind_dir and indicator_file in f) or \

               # Look for both the indicator file and folder
               (basename(r) == indicator_folder and indicator_file in f)):

                paths.append(r)


    return paths


if __name__ == "__main__":

    # Director of interest
    basins_dir = "~/projects/basins"

    parser = argparse.ArgumentParser(description='Utilize makefiles to make '
                                                 'mass operations on basins.')
    parser.add_argument('command', metavar='cmd',
                        help='Pass a makefile command to execute on every basin')
    parser.add_argument('--keyword','-kw', dest='kw',
                        help='Filter basin_ops paths for kw e.g. tuolumne will'
                              'find only one topo to process')

    args = parser.parse_args()

    # Grab a command passed in
    make_cmd = args.command

    count = 0
    basins_attempted = 0

    out.msg("Looking in {} for basins with makefiles...".format(basins_dir))

    basin_paths = find_basin_paths(basins_dir, indicator_folder="model_setup",
                                               indicator_file="Makefile")

    if args.kw != None:
        out.msg("Filtering basin paths using keyword: {}".format(args.kw))
        basin_paths = [p for p in basin_paths if args.kw in p]

        # Warn user if no matches found
        if len(basin_paths) == 0:
            out.error('{} not found in any ops paths'.format(args.kw))


    for r in basin_paths:
        topo_attempt = False
        try:
            cmd = "cd {} && make {}".format(r, make_cmd)
            out.dbg(cmd)
            s = Popen(cmd, shell=True)
            s.wait()
            topo_attempt = True

        except Exception as e:
            raise e

        if topo_attempt:
            basins_attempted += 1

        #input("press enter to continue")
    out.msg("Attempted to build {} topos".format(basins_attempted))
