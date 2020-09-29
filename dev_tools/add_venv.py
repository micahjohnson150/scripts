##!/usr/bin/env python3

'''
Given a folder, this script creates bash aliases designed to add all my
virtualenv aliases which are always stored in the same format under my
venv folder. Run this script when you source your .bashrc to get auto aliases
created.
'''
from os.path import expanduser, abspath, join, basename
from subprocess import check_output
import glob

venv_dir = '~/projects/venv'

# Only grab folders with env in the name
envs = glob.glob(join(abspath(expanduser(venv_dir)), '*env'))

cmd = ['alias',"{}='source {}/bin/activate'"]

for env in envs:
    name = basename(env)

    cmd = "alias {}='source {}/bin/activate'".format(name, env)
    print(cmd)
