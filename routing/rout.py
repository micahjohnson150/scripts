from landlab.io.netcdf import read_netcdf, WITH_NETCDF4,write_netcdf
from landlab import RasterModelGrid
from landlab.components import FlowRouter, SinkFiller
from landlab.components.overland_flow import OverlandFlow
from landlab import FIXED_LINK, FIXED_GRADIENT_BOUNDARY
from landlab.plot.imshow import imshow_grid

from netCDF4 import Dataset
import numpy as np
import progressbar as pb
import matplotlib.pyplot as plt
import pandas as pd

################################# INPUTS #######################################
days = 21 #"max_days"
swi_f = './swi.nc'

################################# SETUP ########################################

# Create the grid from the netcdf
swi_ds = Dataset(swi_f, mode ='r')

# Make output netcdfs
out = Dataset('surface_water.nc', mode = 'w',format='NETCDF4')

# Add NC dimensions
for d,dimension in swi_ds.dimensions.items():
    out.createDimension(d,(len(dimension) if not dimension.isunlimited() else None ))
    out.dimensions[d] = dimension

# Add NC variables for outputting
for name,var in swi_ds.variables.items():
    if name.lower() in ['time','x','y']:
        out.createVariable(name, var.datatype, var.dimensions)
    if name.lower() in ['x','y']:
        out.variables[name] = var[:]

out.createVariable('surface_water__depth','f8',("time","y","x"))
out.createVariable('surface_water__discharge','f8',("time","y","x"))

# Calculate the grid size
dx = abs(swi_ds.variables['x'][0] - swi_ds.variables['x'][1])
dem = swi_ds.variables['dem'][:]
pp = swi_ds.variables['SWI'][:]

# Landlab has issues with C types this ensures we have the right type
z = dem

# Calculate run time
elapsed_time = 0.0
if days == 'max_days':
    days = len(pp[:,0,0])

model_run_time = 86400*days

print("Running Simulation of overland flow...")
print('\n======== SIM Details ==========\n')
print("run_time = {} days ({} hrs)\n".format(model_run_time/86400.0, model_run_time/3600.0))
# Create a blank grid of the right size
print("\tMaking a new grid of {} at {}m spacing...".format(z.shape, dx))
rmg = RasterModelGrid(z.shape, (dx,dx))

# DEM, depth, and discharge assignment
rmg['node']['topographic__elevation'] = z
rmg.add_zeros('node', 'surface_water__depth')
rmg.add_zeros('node', 'surface_water__discharge')

# Assign the outlet and boundary conditions
print("\tSetting Boundary Conditions...")

# If more than one outlet, errors out and show which outlets
# outlet_id = rmg.set_watershed_boundary_condition(z.flatten(), nodata_value=-9999, return_outlet_id=True)

outlet_id = 2615
rmg.set_watershed_boundary_condition_outlet_id(outlet_id,z.flatten())

# Object for managing the simulation
of = OverlandFlow(rmg, mannings_n=0.03, steep_slopes=True)

# Flow Routing
print("\tProcessing DEM for routing...")
sf = SinkFiller(rmg, routing='D4', apply_slope=False, fill_slope=1.e-5)

print("\tFilling pits...")
#sf.fill_pits()

print("\tOutputting topo from Landlab...")
write_netcdf('ll_topo.nc', rmg, names=['topographic__elevation'])


################################# FLOW SIM #####################################

# Show the user whats going on with the progress
print()
bar = pb.ProgressBar(max_value= (model_run_time/3600)+1)


pp_t = 87
iteration = 0
precip = ((pp[pp_t,:]/86400.0)/1000.0).flatten()

# Initial output
out.variables['time'][iteration] = elapsed_time

out.variables['surface_water__discharge'][iteration] = \
                                         rmg.at_node['surface_water__discharge']

out.variables['surface_water__depth'][iteration] = \
                                             rmg.at_node['surface_water__depth']

# TIME LOOP
while elapsed_time < model_run_time:

    # Adaptive time step
    of.dt = of.calc_time_step()

    if elapsed_time > pp_t * 86400.0:
        pp_t += 1

        # Convert to m/sec of precip
        precip = ((pp[pp_t,:] / 86400.0) / 1000.0).flatten()
        # print("New Precip event: {}mm".format(np.mean(precip)*of.dt*1000))

    # Add in any SWI
    rmg.at_node['surface_water__depth'] += precip * of.dt

    # Calculate overland
    of.overland_flow()

    elapsed_time += of.dt

    if of.dt > 3600.0:
        print(of.dt)
    # output nearly hourly
    if elapsed_time >= iteration*3600.0:

        # Output Netcdf stuff
        rmg.at_node['surface_water__discharge'] = of.discharge_mapper(of.q,
                                                         convert_to_volume=True)
        out.variables['time'][iteration] = elapsed_time

        out.variables['surface_water__discharge'][iteration] = \
                                         rmg.at_node['surface_water__discharge']

        out.variables['surface_water__depth'][iteration] = \
                                             rmg.at_node['surface_water__depth']
        iteration+=1


    bar.update(iteration)

# Clean up
swi_ds.close()
out.close()
