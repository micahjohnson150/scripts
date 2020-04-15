'''
This script looks at the changes occurred from implementing
https://github.com/USDA-ARS-NWRC/smrf/issues/100
https://github.com/USDA-ARS-NWRC/smrf/issues/97

Which remove config items and retrieve them from the topo.
Unfortunatley this affected the net_solar Gold file. So here is the diff

To evaluate:
1. Run the new code, copy the files to compare, also grab the new lat long in the log
2. Checkout to the master branch, run it there unmodified, copy files for comparison
3. Modify the config file in master to what it is now, run copy and compare.

'''

from os.path import abspath, join, expanduser
from glob import glob


from goldmeister.compare import GoldGitBranchCompare, GoldFilesCompare

repo = abspath(expanduser('~/projects/smrf'))

gold_dir = join(repo, 'tests', 'RME', 'gold')
compare_dir = join(repo, 'tests', 'RME', 'output')

gf = glob(gold_dir + '/*.nc')
cf = glob(compare_dir + '/*.nc')

# gc = GoldGitBranchCompare(repo_path='~/projects/smrf',
#                     gold_files=gf,
#                     old_branch='master',
#                     new_branch='projections_update')

gc = GoldFilesCompare(gold_files=gf, compare_files=cf, file_type='netcdf')
results = gc.compare()
gc.plot_results(results, plot_original_data=True)

# # Inputs
# repo = abspath(expanduser('~/projects/smrf/'))
# work_dir = join(repo,'tests','RME')
# results_dir = join(work_dir, 'output')
# config = join(work_dir, 'config.ini')
#
# run_smrf_cmd = 'run_smrf {}'.format(config)
# tmp = 'tmp'
# analysis_dirs = ['master', 'modified_master', 'new']
#
# # Put it all under the tmp dir
# analysis_dirs = [join(tmp,d) for d in analysis_dirs]
#
# # Remove any pre-exisiting files
# clean_up_dirs(tmp)
#
# # Make the analysis strucuture
# for d in analysis_dirs:
#     # Make it
#     os.mkdir(join(tmp, d))
#
# # Run Original Master as of 4-6-2020 and copy files over
# checkout_branch(repo, '4a1e5243066f29a05a957159e28a91fafe930850')
# install_pypackage(repo, run_clean_first=True)
# run_cmd(run_smrf_cmd)
# copy_netcdfs(results_dir,analysis_dirs[0])
#
# # Go to the new branch and run
# checkout_branch(repo, 'projections_update')
# install_pypackage(repo, run_clean_first=True)
# run_cmd(run_smrf_cmd)
# copy_netcdfs(results_dir, analysis_dirs[2])
