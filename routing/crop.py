import netCDF4 as nc
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description="Crop a dem and associated data to"
                                            "a sub mask")
parser.add_argument(dest='topo',
                    help='Path to a netcdf file that has dem and the mask in it')

parser.add_argument(dest='em', help='Path to a netcdf file that has swi')

parser.add_argument('--output','-o', default= './out.nc', help='output filename')
parser.add_argument('--mask','-m', default= 'mask tollgate', help='mask name to use')

args = parser.parse_args()

input_f = args.topo
snow_f = args.em
f_out = args.output
mask = args.mask

print("\nCreating output file...")

# Topo image we want to emulate
img = nc.Dataset(input_f)

# Swi image we need to crop
snow_img = nc.Dataset(snow_f)

out = nc.Dataset(f_out, mode = 'w', format='NETCDF4')

out.description =' Cropped to {}.'.format(mask)

out.history = " Modified {0}".format(
                        (dt.datetime.now().strftime("%y-%m-%d %H:%M")))
# get the exents
mask = img.variables[mask][:]
ln = np.where(mask)
minx = np.min(ln[1])
maxx = np.max(ln[1])
miny = np.min(ln[0])
maxy = np.max(ln[0])
mask[mask==1] = True
mask[mask==0] = False
print("mask extents = ({},{}) x ({},{})".format(minx,miny,maxx,maxy))

# Asign time from snow, but x,y from topo
for d,dimension in snow_img.dimensions.items():
    # snag x,y from topo
    name = d.lower()

    if name == 'x':
        d_len = maxx - minx

    elif name =='y':
        d_len = maxy-miny

    elif name == 'time':
        d_len = len(dimension)

    out.createDimension(d, d_len if not dimension.isunlimited() else None)
    print("{} is {} long".format(d,d_len))


print("\nAdding variables to {0}...".format(f_out))

# Crop swi, assign snow time, assign topo x and y
for name,var in snow_img.variables.items():

    if name.lower() in ['x','y','time','swi']:
        if name.lower() != 'swi':
            out.createVariable(name, var.datatype, var.dimensions)
        else:
            out.createVariable(name, 'float64', var.dimensions)

        print("\t{0}".format(name))

        if name == 'x':
            out[name][:] = snow_img.variables[name][minx:maxx]

        elif name =='y':
            out[name][:] = snow_img.variables[name][miny:maxy]

        elif name == 'time':
            out[name][:] = snow_img.variables[name][:]

        elif name.lower() == 'swi':
            masked_data = snow_img.variables[name][:]*mask
            masked_data[:,mask==False] = -9999

            out[name][:] = np.flipud(masked_data[:,miny:maxy,minx:maxx])

print("Adding Dem...")
out.createVariable('dem', 'float64', img.variables['dem'].dimensions)
dem_data = img.variables['dem']*mask
dem_data[mask==False] = -9999

out['dem'][:] = dem_data[miny:maxy,minx:maxx]

out.sync()
img.close()
snow_img.close()
out.close()
