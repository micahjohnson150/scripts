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
from subprocess import check_output
from inicheck.tools import get_user_config
import pygit2
import shutil
from goldmeister.compare import GoldGitBranchCompare, GoldFilesCompare
import sys


def change_branch(repo, branch):
    '''
    Use py git to change branches and install the latest version
    '''

    print("Changing git repo {} to {}".format(repo, branch))
    git_repo = pygit2.Repository(abspath(expanduser(repo)))
    git_branch = git_repo.branches[branch]

    if not git_branch.is_checked_out():
        git_repo.checkout(git_branch)
    else:
        print("Branch already in {}".format(branch))

    check_output('cd {} && python setup.py install'.format(repo), shell=True)


def produce_comparison(ucfg, gold_dir, cfg_mods={}, results='output'):
    """
    """
    for s in cfg_mods.keys():
        for i , v in cfg_mods[s].items():
            print(s,i,v)
            ucfg.cfg[s][i] = v

    # Run smrf with the new config file
    from smrf.framework.model_framework import run_smrf
    run_smrf(ucfg)
    gf = glob(gold_dir + '/*.nc')
    cf = glob(ucfg.cfg['output']['out_location'] + '/*.nc')

    gc = GoldFilesCompare(gold_files=gf, compare_files=cf, file_type='netcdf',
                          only_report_nonzero=True, output_dir=results)
    results = gc.compare()
    gc.plot_results(results, plot_original_data=False, include_hist=True, show_plots=False)

    shutil.rmtree(ucfg.cfg['output']['out_location'])


def main():
    repo = abspath(expanduser('~/projects/smrf'))

    branch = sys.argv[1]
    # Compare the full RME run test with station data gold files
    print('\nAnalyzing gold file differences in the {} branch...'.format(branch))
    print('=======================================================')
    # Change to the master branch
    change_branch(repo, branch)

    # Setup the location of the model run data to check
    gold_dir = join(repo, 'tests', 'RME', 'gold')
    hrrr_gold_dir = join(repo, 'tests', 'RME', 'gold_hrrr')

    # Config file modifications
    cfg = {'output':{'out_location':'run_output'},
          'system':{'log_file':'log.txt'},
          }

    if branch == 'master':
        print("changing topo config section")
        cfg['topo'] = {'basin_lat':43.06475,
                     'basin_lon':-116.75395} # From the new calculation

    # Run the model, analyze the results
    import smrf

    ucfg = get_user_config(join(gold_dir,'gold_config.ini'), modules='smrf')
    produce_comparison(ucfg, gold_dir, cfg_mods=cfg, results='{}_station_results'.format(branch))

    ucfg = get_user_config(join(hrrr_gold_dir,'gold_config.ini'), modules='smrf')
    produce_comparison(ucfg, hrrr_gold_dir, cfg_mods=cfg, results='{}_hrrr_results'.format(branch))

    # # Compare the full RME run test with station data gold files
    # print('\nAnalyzing gold file differences in the projections branch...')
    # print('=======================================================')
    # # Change to the branch
    # change_branch(repo, 'projections_update')
    #
    # # Setup the location of the model run data to check
    # gold_dir = join(repo, 'tests', 'RME', 'gold')
    # hrrr_gold_dir = join(repo, 'tests', 'RME', 'gold_hrrr')
    #
    # # Config file modifications
    # adj_cfg = {'output':{'out_location':'run_output'},
    #       'system':{'log_file':'/home/micahjohnson/projects/scripts/pull_requests/smrf_projections_update/log.txt'}}
    #
    # # Run the model, analyze the results
    # ucfg = get_user_config(join(gold_dir, 'gold_config.ini'), modules='smrf')
    # print(ucfg.cfg['topo'])
    # produce_comparison(ucfg, gold_dir, cfg_mods=adj_cfg, results='projections_update_station_results')
    # produce_comparison(ucfg, hrrr_gold_dir, cfg_mods=adj_cfg, results='projections_update_hrrr_results')




if __name__ == '__main__':
    main()
