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
################# INPUTS ##################
days = 8#"max_days"
swi_f = './swi.nc'
########### SETUP ################

# Create the grid from the netcdf
swi_ds = Dataset(swi_f, mode ='r')

# Make output
out = Dataset('surface_water.nc', mode = 'w',format='NETCDF4')
for d,dimension in swi_ds.dimensions.items():
    out.createDimension(d,(len(dimension) if not dimension.isunlimited() else None ))
    out.dimensions[d] = dimension

for name,var in swi_ds.variables.items():
    if name.lower() in ['time','x','y']:
        out.createVariable(name, var.datatype, var.dimensions)
    if name.lower() in ['x','y']:
        out.variables[name] = var[:]

out.createVariable('surface_water__depth','f8',("time","y","x"))
out.createVariable('surface_water__discharge','f8',("time","y","x"))

dx = abs(swi_ds.variables['x'][0] - swi_ds.variables['x'][1])
dem = swi_ds.variables['dem'][:]
pp = swi_ds.variables['SWI'][:]

# Landlab has issues with C types this ensures we have the right type
z = np.ones(dem.shape, dtype=np.float64)
z = z*dem

# Create a blank grid of the right size
print("Making a new grid of {} at {}m spacing...".format(z.shape, dx))
rmg = RasterModelGrid(z.shape, (dx,dx))


# DEM assignment
rmg['node']['topographic__elevation'] = z
# plt.imshow(z)
# plt.show()

write_netcdf('ll_topo.nc', rmg,
names=['topographic__elevation'])


rmg.add_zeros('node', 'surface_water__depth')
rmg.add_zeros('node', 'surface_water__discharge')

# Assign the outlet and boundary conditions
print("Setting Boundary Conditions...")
# print(out_id)
rmg.set_closed_boundaries_at_grid_edges(True, True, True, False)
#out_id = rmg.set_watershed_boundary_condition(z.flatten(), -9999.,True)                                        #True)

outlet_id = rmg.core_nodes[np.argmin(rmg.at_node['topographic__elevation'][rmg.core_nodes])]

rmg.set_watershed_boundary_condition_outlet_id(outlet_id,z.ravel())

# Flow Routing
print("Processing DEM for routing...")

sf = SinkFiller(rmg, routing='D4', apply_slope=True, fill_slope=1.e-5)
# print(rmg.at_node['flow__sink_flag'][rmg.core_nodes].sum())
#print("Filling pits")
#sf.fill_pits()


# Preparing Outputs
#
############### Flow Sim ########################
print("Running Simulation of overland flow...")
elapsed_time = 0.0
if days == 'max_days':
    days = len(pp[:,0,0])

model_run_time = 86400*days

print('======== SIM Details ==========')
print("run_time = {} days".format(model_run_time/86400.0))

hydrograph_time = []
discharge_at_outlet = []
bar = pb.ProgressBar(max_value= int(model_run_time)+86400.0)

of = OverlandFlow(rmg, mannings_n=0.03, steep_slopes=True)

pp_t = 115
iteration = 0
precip = (pp[pp_t,:]/86400.0)/1000.0

while elapsed_time < model_run_time:

    of.dt = of.calc_time_step()     # Adaptive time step

    if elapsed_time > pp_t * 86400.0:
        pp_t += 1
        precip = (pp[pp_t,:]/86400.0)/1000.0

        #print("New Precip event: {}mm".format(np.mean(precip)*of.dt*1000))

    rmg.at_node['surface_water__depth'] += np.ravel(precip) * of.dt

    of.overland_flow()

    rmg.at_node['surface_water__discharge'] = of.discharge_mapper(of.q, convert_to_volume=True)

    hydrograph_time.append(elapsed_time / 3600.) # convert seconds to hours
    discharge_at_outlet.append(np.abs(of.q[outlet_id]) * rmg.dx) # append discharge i
    elapsed_time += of.dt

    if elapsed_time > iteration*3600.0:
        iteration+=1
        out.variables['time'][iteration] = elapsed_time
        out.variables['surface_water__discharge'][iteration] = rmg.at_node['surface_water__discharge']
        out.variables['surface_water__depth'][iteration] = rmg.at_node['surface_water__depth']

    bar.update(elapsed_time)
# Clean up
swi_ds.close()
out.close()


imshow_grid(rmg, 'surface_water__depth', plot_name='Water depth at time = {0} hours'.format(elapsed_time/3600.0),
    var_name='Water Depth', var_units='m', grid_units=('m', 'm'), cmap='Blues')
plt.show()

imshow_grid(rmg, 'surface_water__discharge', plot_name='Water discharge at time = {0} hours'.format(elapsed_time/3600.0),
    var_name='Water cms', var_units='m', grid_units=('m', 'm'), cmap='Blues')
plt.show()
