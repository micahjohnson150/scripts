import argparse
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description="Plot streams in a manner that "
                                             "easy to see")
parser.add_argument(dest='filename', type=str,
                    help='Path to a netcdf file that has surface water discharge')
parser.add_argument('--threshold','-t', dest='threshold', type=float, default= 0.05,
                    help='threshold used to create plot')

args = parser.parse_args()

ds = Dataset(args.filename)

streams = np.zeros(ds.variables['surface_water__discharge'][0,:].shape)

for t in range(len(ds.variables['surface_water__discharge'][:])):
    ind = ds.variables['surface_water__discharge'][t,:] >= args.threshold
    streams[ind==True] = 0.5

plt.pcolor(np.flipud(streams))
plt.colorbar()
plt.show()
ds.close()
