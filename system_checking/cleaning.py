#!/usr/bin/env python3
import os
from subprocess import check_output




def get_memory_use():
    result = {}
    s = check_output("du  --block-size M -d 1", shell=True).decode("utf-8")
    lines = s.split("\n")

    for line in lines:
        if line:
            v, k = line.split("\t")
            result[k] = float("".join([c for c in v if c.isnumeric()]))

    result = (sorted(result.items(), reverse=True, key = lambda kv:(kv[1], kv[0])))
    return result

print("Gathering Memory Data...")
mem = get_memory_use()
git_repos = [k for k in mem.keys() if os.path.isdir(os.path.join(k,".git"))]
print("")
