#!/usr/bin/env python3

from os.path import basename, dirname, abspath, join, isdir
from inicheck.tools import get_user_config
from subprocess import check_output
from inicheck.output import generate_config
from shutil import rmtree
import argparse
import coloredlogs
import os
import logging
import pandas as pd


def find_section_item_start_stop(ucfg, possible_sections=["time","setup","run"]):
    """
    Searches out the start and stop in config and returns the section and items names
    """

    keywords = {"start":['start','begin'],
                "end": ['stop','end']}

    results = {"section":None, "start":None, "end":None}

    potential = [s for s in ucfg.cfg.keys() if s in possible_sections]

    for s in potential:
        for i in ucfg.cfg[s].keys():
            for k,v in keywords.items():
                # Look through the keywords and see if any are in the item name
                matches = [True for z in v if z in i]

                if matches:
                    results[k] = i
                    results['section'] = s

            # If None of the results are None break out
            if len([True for k,v in results.items() if v != None])==3:
                break

    return results


def set_dates(ucfg, wyr, section, start_name, end_name):
    """
    Reassign the water year in the config file. The start and end dates are
    assumed to ba static according to the config by the original designation of
    the month and day. Only the year is modified

    Args:
        ucfg: UserConfig object
        wyr: Water year to run
        section: Section name where the start and end date items live
        start_name: Item name of the start date in the config
        end_name: Item name of the start date in the config
    Returns:
        ucfg: UserConfig object with modfied dates
    """

    start = ucfg.cfg[section][start_name]
    end = ucfg.cfg[section][end_name]

    # Cycle through the start and ends
    for i in [start_name, end_name]:

        # Grab the date to be modified
        date = ucfg.cfg[section][i]

        # Determine the wateryear cut off time for water year-1 or water year
        split = pd.to_datetime("10-01-{}".format(date.year))

        # Is the date before the new year? The its probably the begining of WY
        if date >= split:
            date = date.replace(year=int(wyr) - 1)
        else:
            date = date.replace(year=int(wyr))

        ucfg.cfg[section][i] = date
    return ucfg


def main():
    """
    Runs a command that only takes a config. This was originally written to
    perform multiyear analysis on swiflows calibration commands.
    """
    p = argparse.ArgumentParser(description="Runs a command that takes a config"
                                            " file for mulitple years.")

    p.add_argument("cmd", help="Command to execute like cmd config.ini")

    p.add_argument("config", help="Config file containing all settings for"
                                  " running the cmd")

    p.add_argument("-wy", "--years", dest='years', required=True, nargs="+",
                        help="Water years to run by changing the start and end"
                        " times in the config, if not provided it will just run"
                        " the cmd, assumes the month and day assigned in the "
                        " config are constant")

    p.add_argument("-m", "--modules", dest='modules', required=False, nargs='+',
                        help="Python packages the config is associated to")
    p.add_argument("-o", "--output", dest='output', required=False,
                        default='./output',
                        help="Python packages the config is associated to")

    args = p.parse_args()

    # Manage the config paths and modules and grab the config
    orig_path = abspath(args.config)
    if args.modules:
        modules = args.modules
    else:
        modules = None

    ucfg = get_user_config(orig_path, modules=modules)

    # Setup output path
    output = abspath(args.output)
    if not isdir(output):
        os.makedirs(output)


    print("Running {} {} over {}...".format(args.cmd,args.config,
                                               ", ".join(args.years)))

    # Determine the dates to modify and report it
    results = find_section_item_start_stop(ucfg)
    sec_name = results['section']
    start_name = results['start']
    end_name = results['end']
    start = ucfg.cfg[sec_name][start_name]
    end = ucfg.cfg[sec_name][end_name]

    print("Found the modifiable start and stop dates in the config file...")
    print("Start in configs Section: {} Item: {}".format(sec_name, start_name))
    print("End in configs Section: {} Item: {}".format(sec_name, end_name))
    fmt = "%m-%d"
    print("Running {} year over {} - {}".format(len(args.years),
                                                   start.strftime(fmt),
                                                   end.strftime(fmt)))

    for wyr in args.years:
        print("Adjusting config for WY{} and running...".format(wyr))

        # Update the paths for modifying
        current_output = join(output, wyr)
        current_path = join(current_output, "config.ini")
        ucfg = set_dates(ucfg, wyr, sec_name, start_name, end_name)

        if not isdir(current_output):
            os.makedirs(current_output)
        else:
            print("WARN: WY{} has data in it, you could be overwriting"
                        " data...".format(wyr))

        # Write the config so we can run
        generate_config(ucfg, current_path)

        # Build the command
        cmd = "{} {}".format(args.cmd, current_path)

        s = check_output(cmd, shell=True)
        print(s.decode("utf-8"))

if __name__ == '__main__':
    main()
