'''
This script looks at the changes occurred from implementing
https://github.com/USDA-ARS-NWRC/smrf/issues/100
https://github.com/USDA-ARS-NWRC/smrf/issues/97

Which remove config items and retrieve them from the topo.
Unfortunatley this affected the net_solar Gold file. So here is the diff
'''
from subprocess import check_output

from commands import * 
def checkout_branch(branch_name):
    '''
    Run git checkout to switch branches.
    '''
    cmd =
# First checkout master today (04-06-2020)

cmd 'run_smrf ~/projects/smrf/tests/RME/config.ini'
