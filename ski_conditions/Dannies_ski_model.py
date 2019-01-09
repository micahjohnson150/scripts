from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
# Minimum of depth

def determine_good_skiing(ski_quality, density, delta_t):
    rho = [0, 200]
    delta_depth = [0.010, 0.025] #cm

    rho_ind = (density > rho[0]) & (density < rho[1])
    depth_ind = (delta_t > delta_depth[0]) & (delta_t < delta_depth[1])
    ind = (rho_ind)& (depth_ind)
    ski_quality[ind] = 3
    print("Great:{}".format(len(ind)))

    return ski_quality


def determine_medium_skiing(ski_quality, density, delta_t):
    # Medium Skiing
    rho = [200, 300]
    delta_depth = [0.025, 0.050]
    rho_ind = (density > rho[0]) & (density < rho[1])

    rho_ind = (density > rho[0]) & (density < rho[1])
    depth_ind = (delta_t > delta_depth[0]) & (delta_t < delta_depth[1])
    ind =  (rho_ind)& (depth_ind)
    ski_quality[ind] = 2

    return ski_quality

def main():
    f = '/home/micahjohnson/projects/basins/reynolds_mountain/output/rme/devel/wy1984/storm_bug_fixed/runs/run0001_3648/snow.nc'

    ds = Dataset(f,'r')

    #  Create the output
    out = Dataset('./ski_quality.nc', mode = 'w')

    for d,dimension in ds.dimensions.items():
        out.createDimension(d)
        out.dimensions[d] = dimension

    for v in ['x','y','time']:
        out.createVariable(v,np.int16,v)
        out.variables[v] = ds.variables[v]

    out.createVariable('ski_quality', np.int16, ('time','y','x'))

    for t in range(1,len(ds.variables['time'][1:])):
        density = ds.variables['snow_density'][t]
        delta = ds.variables['thickness'][t] - \
                ds.variables['thickness'][t-1]

        ski_quality = np.ones(density.shape)
        ski_quality = determine_good_skiing(ski_quality, density, delta)
        ski_quality = determine_medium_skiing(ski_quality, density, delta)

        out.variables['ski_quality'][t] = ski_quality
    ds.close()
    out.sync()
    out.close()

if __name__ =='__main__':
    main()
