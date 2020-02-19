'''
Confirms that the gold config produces matching netcdfs as to what is in
the repo
'''
import subprocess as sp
import sys
from netCDF4 import Dataset
from os.path import join, abspath, expanduser

project = 'awsm'

# Location to the gold files and config
project_dir = abspath(expanduser('~/projects/{}/tests/RME/gold'.format(project)))

# Output location where snow and em file lives
output = join(project_dir, 'output/rme/devel/wy1986/rme_test/runs/run3337_3344')

for f in ['em.nc','snow.nc']:
    fname = join(output, f)
    gfname = join(project_dir, f)
    diff_f = join(project_dir, 'diff.nc')
    diff_cmd = 'ncdiff -O {} {} {}'.format(fname, gfname, diff_f)
    print('\n\n' + diff_cmd)
    sp.check_output(diff_cmd, shell=True)

    ds = Dataset(diff_f)
    print("Opening {}".format(diff_f))

    for v in [v for v in ds.variables.keys() if v not in ['x','y','time','projection']]:
        print("\tEvaluating {}".format(v))
        cmd = 'nc_stats {} {}'.format(diff_f, v)
        out = sp.check_output(cmd, shell=True)
        print(out.decode('utf-8'))
    ds.close()
