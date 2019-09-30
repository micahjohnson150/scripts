###########################################################################
# Script for comparing the extents of a netcdf with a kown extent.        #
#                                                                         #
# Usage:                                                                  #
# python compare_extents.py topo.nc 283992.7 4050545.0 381092.7 4120045.0 #
#                                                                         #
###########################################################################

import sys
from netCDF4 import Dataset
from basin_setup.basin_setup import parse_extent, Messages

out = Messages()


# Providea  file and check it against a provided extent
if len(sys.argv) != 6:
    out.error("Usage is netcdf and lower left and upper right extents to compare")
    sys.exit()


order = ["xmin","ymin","xmax","ymax"]
my_exts = [float(v) for v in sys.argv[2:]]

extents = parse_extent(sys.argv[1])

msg = "{0:<10}{1:<10}"
hdr = msg.format("Item","Difference")
msgs = []
msgs.append(hdr)
msgs.append("=" * len(hdr))

for i,e in enumerate(extents):
    diff = my_exts[i] - e
    print([order[i], my_exts[i], e, diff])
    if diff != 0:
        msgs.append(msg.format(order[i], diff))

if len(msgs) == 0:
    out.respond("No Differences found between the file and the provided extents")
else:
    for m in msgs:
        out.msg(m)
