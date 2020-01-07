import datetime
import argparse
from os.path import basename


def create_shapefile_str(shapefiles, epsg, str_now, template='shapefile_template.xml'):
    """
    Create three strings to insert in to the qgis project
    """
    # Add shapefile info in 3 places
    shp_declarations = ''
    shp_order = ''
    shp_layers = ''

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
        name = basename(sb).split('.')[0]
        shp_replace = {"SHAPEFILE_PATH": sb,
                        "SHAPEFILE_NAME": name,
                        "EPSG": str(epsg),
                        "ID": str_now}

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

    shp_declarations, shp_order, shp_layers = create_shapefile_str(["../delineation/basin_outline.shp"],32611,str_now)

    # Populate replacement info
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
    "SHAPEFILE_DECLARATATION":shp_declarations,
    "SHAPEFILE_ORDER": shp_order,
    "SHAPEFILE_LAYERS": shp_layers
    }

    # Open the template
    fname = 'template.xml'

    with open(fname,'r') as fp:
        lines = fp.readlines()
        fp.close()

    info = "".join(lines)

    info = str_swap(info, replacements)

    out = "test.qgs"

    with open(out,'w+') as fp:
        fp.write(info)
        fp.close()

if __name__ == '__main__':
    main()
