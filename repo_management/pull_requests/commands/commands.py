from subprocess import check_output
from os.path import abspath, expanduser

def checkout_branch(git_repo, branch_name):
    '''
    Move to the git repo, checkout the desired branch name
    and cd back.

    Args:
        git_repo: Path to a valid git tracked repository
        branch_name: Valid branch name in that repository
    '''
    repo_dir = abspath(expanduser(git_repo))
    cmd = 'cd {} && git checkout {} && cd -'.format(repo_dir, branch)
    print(cmd)
    s = check_output(cmd, shell=True)
    print(s)

def run_cmd(cmd):
    '''
    Execute a command on the command line via python
    '''
    print(cmd)
    s = check_output(cmd, shell=True)
    print(s)

def clean_up(dirs):
    '''
    Removes a list of directories
    '''

    # Clean up any comparison files
    for d in output_dirs:
        # Remove it
        shutil.rmtree(d)

def copy_netcdfs(from_dir, to_dir, append_name=None):
    '''
    Copy all netcdfs in the from_dir and copy them to the to_dir. If an
    append_name is used the resulting file will have a string appended to the
    front of the name

    Args:
        from_dir: Directory containing netcdfs
        to_dir: Directory to copy netcdfs to
        append_name: String to add to the name of the existing file name
    '''
    from_dir = abspath(expanduser(from_dir))
    to_dir =  abspath(expanduser(to_dir))

    copy_cmd = 'cp {} {}'
    for f in os.listdir(from_dir):
        if f.split('.')[-1] == 'nc':
            fname = join(from_dir, f)

            if append_name != None:
                out_f = append_name + f
            else:
                out_f = f
            out_f = join(to_dir, out_f)

            run_cmd(copy_cmd.format(fname, out_f))
