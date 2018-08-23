from netCDF4 import Dataset
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Plot up the runoff")
parser.add_argument(dest='surface_water',
                    help='Path to a netcdf file that has surface_water discharge')
parser.add_argument(dest='runoff', help='Path to measured runoff')

parser.add_argument(dest='swi',
                    help='Path to a netcdf file that has swi')

args = parser.parse_args()

# Read actual runnoff
df = pd.read_csv(args.runoff,parse_dates=True, index_col=0, header=17)

# Open our modeled
ds  = Dataset(args.surface_water)
array_shape = ds.variables['surface_water__discharge'][0,:].shape

# Look with our modeled swi
swi_ds  = Dataset(args.swi)

swi = []
for t in range(int(len(ds.variables['surface_water__discharge'])/24)):
    ind = swi_ds.variables['SWI'][t,:] > 0
    swi.append(np.sum(swi_ds.variables['SWI'][t][ind])/1000000)


dt = pd.DatetimeIndex(freq='D',start = '10-01-1983 00:00:00', periods = len(swi))
s = pd.Series(swi, index = dt)

# Figure out the outlet
indices = np.unravel_index(2615,array_shape)
# plt.imshow(ds.variables['surface_water__discharge'][-1,:])
# plt.plot(indices[1],indices[0],'r.')
# plt.show()

# Make our datetime index
dt = pd.DatetimeIndex(freq='H',start = '10-01-1983 00:00:00', periods = len(ds.variables['surface_water__discharge']))
q = pd.Series(ds.variables['surface_water__discharge'][:,indices[0],indices[1]], index = dt)
df['modeled'] = q
ind = df.index >= dt[0]

plt.plot(df.index,df['modeled'],label='modeled')
plt.plot(df.index[ind],df['qcms'][ind],label='meas')
plt.plot(s.index,s.values)
plt.legend()
plt.show()
