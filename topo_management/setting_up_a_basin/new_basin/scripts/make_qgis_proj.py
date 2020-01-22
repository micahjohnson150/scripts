import datetime
import argparse
from os.path import basename, split
import pprint

def str_swap(str_raw, replace_dict):
    """
    Goes through a str using the replacement dictionary and looks for the
    keys in brackets and replaces them with the values

    Args:
        str_raw: Original string to replace keywords in using the replace_dictionary
        replace_dict: dictionary containing keywords to replace with full strings from the values

    Returns:
        info: string with keywords that are populated with values
    """

    info = str_raw

    for k,v in replace_dict.items():
        search_str = '[{}]'.format(k)

        info = info.replace(search_str,v)

    return info

def get_now_str():
    """
    Retrieves an iso format of the timestamp for now and returns it with all
    formatting removed e.g. 2020-01-10 10:08.26 -> 20200118100826

    To be used an UID for QGIS.

    Returns:
        str_now: String representing the datetime now for use as a UID
    """

    # QGIS appends an identifier to each so construct it here
    str_now = datetime.datetime.now().isoformat()
    str_now = "".join([c for c in str_now if c not in '-:T.'])

    return str_now

class QGISLayerMaker(object):
    def __init__(self, path, epsg, **kwargs):
        """
        Adds a layer to a QGIS project in a hacky XML copy and paste way
        This class is meant to be inherited from with modifications to the
        declaration strings
        """
        # Grab a UID for layer
        self.str_now = get_now_str()

        # Template declaration for a layer. Is inserted near the top of project
        self.declaration =(
        '\t\t<layer-tree-layer expanded="1" providerKey="[PROVIDER]" '
        'checked="Qt::Checked" id="[NAME][ID]" source="[PATH]" name="[NAME]">\n'
        '\t\t\t<customproperties/>\n'
        '\t\t</layer-tree-layer>\n')

        # Create an order entry which is getting added to the layers order
        self.order = "\t\t\t<item>[NAME][ID]</item>\n"

        name = basename(path).split('.')[0]

        # Grab file extension
        ext = path.split('.')[-1]
        # Assign a provider and layer_template based on the file ext
        # shapefile
        if ext == 'shp':

            # line
            if "net_thresh" in path:
                # Dark blue for streams
                color = "0,50,78,0"
                line_type = 'Line'
                template = './scripts/stream_template.xml'
            # Polygon
            else:
                # Charcoal
                color = "41,41,41,0"
                line_type = 'Polygon'
                template = 'scripts/shapefile_template.xml'

            self.ftype = 'shapefile'
            provider = 'ogr'
            template = 'scripts/shapefile_template.xml'


            self.replacements = {"PATH": path,
                                "NAME": name,
                                "EPSG": str(epsg),
                                "ID": self.str_now,
                                "COLOR":color,
                                "LINETYPE":line_type,
                                "PROVIDER":provider}

        # geotiff
        elif ext == 'tif':
            self.ftype = 'geotiff'
            ftype = 'geotiff'
            provider = 'gdal'
            template = 'scripts/raster_template.xml'

            if 'hillshade' in path.lower():
                colormap = './colormaps/hillshade.qml'
            elif 'dem' in path.lower():
                colormap = './colormaps/dem_colormap.qml'
            else:
                colormap = ''

            # If we have a colormap file use it
            if colormap:
                # parse the colormap and inject it in to the qgis project
                with open(colormap) as fp:
                    lines = fp.readlines()
                    fp.close()

                # Find the index in the colormap where pipe is an extract between the two of them
                idx = [i for i,l in enumerate(lines) if 'pipe' in l]
                lines = lines[idx[0] + 1:idx[1]]
                colormap = "\t\t".join(lines)



            self.replacements = {"PATH": path,
                                "NAME": name,
                                "EPSG": str(epsg),
                                "ID": self.str_now,
                                "COLOR_MAP":colormap,
                                "PROVIDER":provider}

        # netcdf
        elif ext == 'nc':
            ftype = 'netcdf'
            provider = 'gdal'
            template = 'scripts/netcdf_template.xml'

        else:
            raise ValueError("Unrecognized file format {}".format(ext))

        # Retrieve the template for a layer
        with open(template) as fp:
            self.layer_template = "".join(fp.readlines())
            fp.close()

    def generate_strs(self):
        """
        Produces the final three sets of strings to go in the project file
        """
        print("Processing strings for a {}".format(self.ftype))
        print("Populating keywords with:")
        pprint.pprint(self.replacements)
        declaration = str_swap(self.declaration, self.replacements)
        order = str_swap(self.order, self.replacements)
        layer_def = str_swap(self.layer_template, self.replacements)

        return declaration, order, layer_def


def create_tiff_strings(paths):
    """
    Creates the strings in qgis to make a single layter for a tiff image
    """
    ras_declaration = ''
    ras_order = ''
    ras_layer = ''
    ras_colors = ''

    declaration = ('\t\t<layer-tree-layer expanded="1" providerKey="gdal" checked="Qt::Checked" id="[NAME][ID]" source="[PATH]" name="[NAME]">\n'
        '\t\t\t<customproperties/>\n'
        '\t\t</layer-tree-layer>\n')


def create_netcdf_str(netcdf_path, variables, str_now, template='./scripts/nc_template.xml'):
    """
    Builds the declarations and layer defs for a qgis project using a netcdf
    """
    nc_declaration = ''
    nc_order = ''
    nc_layer = ''
    nc_colors = ''

    # Build the declaration
    declaration = (
        '\t\t<layer-tree-layer expanded="1" providerKey="gdal"'
        'checked="Qt::Checked" id="NETCDF__[RASTER_NAME]__[VAR_NAME][ID]"'
        'source="NETCDF:&quot;[RASTER_PATH]&quot;:[NC_VAR]" name="NETCDF:&quot;[RASTER_NAME]&quot;:[NC_VAR]">\n'
        '\t\t\t<customproperties/>\n'
        '\t\t</layer-tree-layer>\n')

    # Generic entry for declaring drawing order
    order = "\t\t\t<item>{}{}</item>\n"

    # RASTER NAME is the base name of the file
    name = basename(netcdf_path).split('.')[0]

    # Cycle thouh all the variables in the netcdf and build their strings
    for var_name in variables:

        # Variables to replace
        replacements = {"RASTER_PATH":p,
                        "RASTER_NAME":name,
                        "NC_VAR": var_name,
                        "ID":str_now,
                        }
    nc_declarations += declaration.format(name, str_now, sb)
    nc_order += order.format(name, str_now)
    nc_layers += str_swap(layer_template, shp_replace)


def create_layer_strings(files, epsg, declarations='', order='', layers=''):
    """
    Create three strings to insert in to the qgis project
    """

    for f in files:
        print('\nAdding {}'.format(f))
        qgs = QGISLayerMaker(f, epsg)
        strs = qgs.generate_strs()
        declarations += strs[0]
        order += strs[1]
        layers += strs[2]

    return declarations, order, layers


def main():

    parser = argparse.ArgumentParser(description='Build a qgis project for setting up a basin')
    parser.add_argument('-t','--geotiff', dest='tifs', nargs='+', help='Paths to the geotifs to add, specifically looking for a hillshade and dem')
    parser.add_argument('-s','--shapefiles', dest='shapefiles', nargs='+', help='Paths to the shapefiles')

    args = parser.parse_args()
    epsg = 32611
    ######## INPUTS ########


    print("\n\nAdding shapefiles to the project...")
    shp_declarations, shp_order, shp_layers = create_layer_strings(args.shapefiles, epsg)

    print("\n\nAdding geotiffs to the project...")
    ras_declarations, ras_order, ras_layers = create_layer_strings(args.tifs, epsg)


    # Populate replacement info
    replacements = \
    {
    "RASTER_DECLARATIONS":ras_declarations,
    "RASTER_ORDERS": ras_order,
    "RASTER_LAYERS": ras_layers,
    "SHAPEFILE_DECLARATIONS":shp_declarations,
    "SHAPEFILE_ORDERS": shp_order,
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
