import datetime
import argparse
from os.path import basename
parser = argparse.ArgumentParser(description='Build a qgis project for setting up a basin')
parser.add_argument('dem', metavar='dem', help='Path to a full dem for your basin')
parser.add_argument('hillshade', metavar='hillshade', help='Path to a full hillshade for your basin')
parser.add_argument('colormap', metavar='colormap', help='Path to the custom colormap for the dem')

args = parser.parse_args()


######## INPUTS ########

# QGIS appends an identifier to each so construct it here
str_now = datetime.datetime.now().isoformat()
str_now = "".join([c for c in str_now if c not in '-:T.'])

# parse the colormap and inject it in to the qgis project
with open(args.colormap) as fp:
    lines = fp.readlines()
    fp.close()

# Find the index in the colormap where pipe is an extract between the two of them
idx = [i for i,l in enumerate(lines) if 'pipe' in l]
lines = lines[idx[0]+1:idx[1]]
colormap = "\t\t".join(lines)


# Parse projection info

replacements = \
{
"ID":str_now,
"DEM_NAME": basename(args.dem).split('.')[0],
"DEM_PATH": args.dem,
"HILLSHADE_NAME":basename(args.hillshade).split('.')[0],
"HILLSHADE_PATH":args.hillshade,
"EPSG":'32611',
# "PROJ4":,
"DEM_COLORMAP":colormap,
}

# Open the template
fname = 'template.xml'

with open(fname,'r') as fp:
    lines = fp.readlines()
    fp.close()

info = "".join(lines)

for k,v in replacements.items():
    info = info.replace("[{}]".format(k),v)

out = "test.qgs"

with open(out,'w+') as fp:
    fp.write(info)
    fp.close()
