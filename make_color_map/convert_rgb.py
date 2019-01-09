import argparse
import numpy as np
# Parge command line arguments
p = argparse.ArgumentParser(description="Remaps a RGB colormap to values")

p.add_argument('-f','--file', dest='filename',
                required=True,
                help="rgb file")

p.add_argument('-m','--max', dest='max',type=int, required=True,help="max value")
p.add_argument('-l','--low', dest='low', required=False, type=int, default=0.0,
                help="minimum value")
p.add_argument('-i','--increment', dest='increment', required=False, type=int,
                help="minimum value")
p.add_argument('-u','--units', dest='units',
                required=True,
                help="units for labeling")

args = p.parse_args()


with open(args.filename) as fp:
    lines = fp.readlines()
    fp.close()

if args.increment == None:
    args.increment = len(lines)
else:
    args.increment+=1

num = np.linspace(args.low,args.max,args.increment)

for i in range(args.increment):
    zz = int((i/args.increment)*len(lines))
    data = [ int(t) for t in lines[zz].split(',')]
    color = '#%02x%02x%02x' % (data[0],data[1],data[2])

    if i == 0:
        opacity = 0
    else:
        opacity = 1

    if args.max > 10:
        number = int(num[i])
    else:
        number = num[i]

    print('<ColorMapEntry color="{0}" quantity="{1:0.1f}" label="{1:0.1f} {2}" opacity="{3}"/>'
          ''.format(color, number, args.units, opacity))
