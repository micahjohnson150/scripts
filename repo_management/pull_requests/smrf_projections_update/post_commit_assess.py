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
import shutil
from goldmeister.compare import GoldGitBranchCompare
import sys


def produce_comparison(repo, gold_dir, results='output'):
    """
    """

    gf = glob(gold_dir + '/*.nc')
    gc = GoldGitBranchCompare(repo_path=repo,
                              gold_files=gf,
                              old_branch='master',
                              new_branch='projections_update',
                              file_type='netcdf',
                              output_dir=results,
                              only_report_nonzero=True)

    results = gc.compare()
    gc.plot_results(results, plot_original_data=False, include_hist=True, show_plots=False)
    del gc

def main():
    repo = abspath(expanduser('~/projects/smrf'))

    # Setup the location of the model run data to check
    gold_dir = join(repo, 'tests', 'RME', 'gold')
    hrrr_gold_dir = join(repo, 'tests', 'RME', 'gold_hrrr')

    print("\nAnalyzing Stations differences...")
    produce_comparison(repo, gold_dir, results='station_results')

    print("\nAnalyzing HRRR differences...")
    produce_comparison(repo, hrrr_gold_dir, results='hrrr_results')


if __name__ == '__main__':
    main()
