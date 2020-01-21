import datetime
import argparse
from os.path import basename

def create_netcdf_str():
    pass

def create_shapefile_str(shapefiles, epsg, str_now, template='./scripts/shapefile_template.xml'):
    """
    Create three strings to insert in to the qgis project
    """
    # Add shapefile info in 3 places
    shp_declarations = ''
    shp_order = ''
    shp_layers = ''
    shp_colors = ''

    # Generic entry for declaring a single shapefile
    declaration =(
    '\t\t<layer-tree-layer expanded="1" providerKey="ogr" checked="Qt::Checked" id="{0}{1}" source="{2}" name="{0}">\n'
    '\t\t\t<customproperties/>\n'
    '\t\t</layer-tree-layer>\n')

    # Generic entry for declaring drawing order
    order = "\t\t\t<item>{}{}</item>\n"

    # Retrieve the template for a layer
    with open(template) as fp:
        layer_template = "".join(fp.readlines())
        fp.close()


    for sb in shapefiles:
        # Assign color using the name of the file
        if "net_thresh" in sb:
            color = "0,50,78,0"
            shp_type = 'Line'
        else:
            color = "41,41,41,0"
            shp_type = 'Polygon'

        name = basename(sb).split('.')[0]
        shp_replace = {"SHAPEFILE_PATH": sb,
                        "SHAPEFILE_NAME": name,
                        "EPSG": str(epsg),
                        "ID": str_now,
                        "SHAPEFILE_COLOR":color,
                        "SHAPEFILE_TYPE":shp_type}

        shp_declarations += declaration.format(name, str_now, sb)
        shp_order += order.format(name,str_now)
        shp_layers += str_swap(layer_template, shp_replace)

    return shp_declarations, shp_order, shp_layers


def str_swap(str_raw, replace_dict):
    """
    Goes through a str using the replacement dictionary and looks for the
    keys in brackets and replaces them with the values
    """
    info = str_raw

    for k,v in replace_dict.items():
        info = info.replace("[{}]".format(k),v)
    return info


def main():

    parser = argparse.ArgumentParser(description='Build a qgis project for setting up a basin')
    parser.add_argument('dem', metavar='dem', help='Path to a full dem for your basin')
    parser.add_argument('hillshade', metavar='hillshade', help='Path to a full hillshade for your basin')
    parser.add_argument('colormap', metavar='colormap', help='Path to the custom colormap for the dem')
    parser.add_argument('-s','--shapefiles', dest='shapefiles', nargs='+', help='Paths to the shapefiles')

    args = parser.parse_args()
    EPSG = 32611
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

    # Add the basin_outline, then the subbasins, then the stream network shpaeifles
    shp_declarations = ''
    shp_order = ''
    shp_layers = ''

    print("Adding shapefiles to the project...")
    for kw in ['outline','subbasin','net_thresh']:
        if kw == 'net_thresh':
            template = './scripts/stream_template.xml'
        else:
            template = './scripts/shapefile_template.xml'

        # Collect the shapefiles with the keyword
        basins_shps = [f for f in args.shapefiles if kw in f]
        print('Adding {}'.format(basins_shps))
        shps = create_shapefile_str(basins_shps, EPSG, str_now, template=template)
        shp_declarations += shps[0]
        shp_order += shps[1]
        shp_layers += shps[2]


    # Populate replacement info
    replacements = \
    {
    "ID":str_now,
    "DEM_NAME": basename(args.dem).split('.')[0],
    "DEM_PATH": args.dem,
    "HILLSHADE_NAME":basename(args.hillshade).split('.')[0],
    "HILLSHADE_PATH":args.hillshade,
    "EPSG":str(EPSG),
    # "PROJ4":,
    "DEM_COLORMAP":colormap,
    "SHAPEFILE_DECLARATATION":shp_declarations,
    "SHAPEFILE_ORDER": shp_order,
    "SHAPEFILE_LAYERS": shp_layers,
    }

    # Open the template
    fname = './scripts/template.xml'

    with open(fname,'r') as fp:
        lines = fp.readlines()
        fp.close()

    info = "".join(lines)

    info = str_swap(info, replacements)

    out = "setup.qgs"

    with open(out,'w+') as fp:
        fp.write(info)
        fp.close()

if __name__ == '__main__':
    main()
