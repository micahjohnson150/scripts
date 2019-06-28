from netCDF4 import Dataset
import sys
import matplotlib.pyplot as plt



ds1 = Dataset(sys.argv[1])
ds0 = Dataset(sys.argv[2])

hdr = "{0:<10}{1:<10}{2:<10}{3:<10}{4:<10}".format("Name","Mean","STD", "Max","Min")
print(hdr)
print("=" * len(hdr))

msg = "{0:<10}{1:<10.5f}{2:<10.5f}{3:<10.5f}{4:<10.5f}"

for v in ["x","y",'time','latitude','longitude']:
    diff = ds1.variables[v][:] - ds0.variables[v][:]

    mean = diff.mean()
    std = diff.std()
    vmin = diff.min()
    vmax = diff.max()
    if v in ["latitude",'longitude']:
        plt.imshow(diff)

        plt.title("{} Difference".format(v))
        plt.colorbar()
        plt.show()

    print(msg.format(v,mean,std,vmax,vmin))
