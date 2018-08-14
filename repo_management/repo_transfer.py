#!/usr/bin/env python

"""
Used for transferring repos from gitlab to github

"""


import sys
import os
import subprocess

repo_name = sys.argv[1]

p = subprocess.Popen('git clone --mirror git@gitlab.com:ars-snow/{0}.git'.format(repo_name),shell=True)
p.wait()
os.chdir('{0}.git'.format(repo_name))

d = subprocess.Popen('git push --no-verify --mirror git@github.com:USDA-ARS-NWRC/{0}.git '.format(repo_name),shell=True)
d.wait()
