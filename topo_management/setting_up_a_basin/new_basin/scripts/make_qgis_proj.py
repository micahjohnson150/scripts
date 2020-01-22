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

        self.legend = (
        '\t\t<legendlayer drawingOrder="-1" open="true" checked="Qt::Checked" name="[NAME]" showFeatureCount="0">\n'
        '\t\t\t\t<filegroup open="true" hidden="false">\n'
        '\t\t\t\t\t<legendlayerfile isInOverview="0" layerid="[NAME][ID]" visible="1"/>\n'
        '\t\t\t\t</filegroup>\n'
        '\t\t</legendlayer>\n')

        # Create an order entry which is getting added to the layers order
        self.order = "\t\t\t<item>[NAME][ID]</item>\n"

        # Create the name from the filename or the variable name
        name = basename(path).split('.')[0]

        # Grab file extension
        self.ext = path.split('.')[-1]

        # Assign a provider and layer_template based on the file ext
        if self.ext == 'shp':
            self.ftype = 'shapefile'
            provider = 'ogr'

            # line
            if "net_thresh" in path:
                line_type = 'Line'
                template = './scripts/stream_template.xml'

            # Polygon
            else:
                line_type = 'Polygon'
                template = './scripts/shapefile_template.xml'

            self.replacements = {"PATH": path,
                                "NAME": name,
                                "EPSG": str(epsg),
                                "ID": self.str_now,
                                "LINETYPE":line_type,
                                "PROVIDER":provider}

        elif self.ext == 'tif':
            self.ftype = 'geotiff'
            ftype = 'geotiff'
            provider = 'gdal'
            template = './scripts/raster_template.xml'

            self.replacements = {"PATH": path,
                                "NAME": name,
                                "EPSG": str(epsg),
                                "ID": self.str_now,
                                "PROVIDER":provider}

        # Netcdf
        elif self.ext == 'nc':
            self.ftype = 'netcdf'
            provider = 'gdal'
            template = './scripts/netcdf_template.xml'

            self.declaration = (
                '\t\t<layer-tree-layer expanded="1" providerKey="gdal"'
                'checked="Qt::Checked" id="NETCDF__[NAME]__[VARIABLE][ID]" '
                'source="NETCDF:&quot;[PATH]&quot;:[NC_VAR]" name="NETCDF:'
                '&quot;[NAME]&quot;:[VARIABLE]">\n'
                '\t\t\t<customproperties/>\n'
                '\t\t</layer-tree-layer>\n')

            self.replacements = {"PATH": path,
                                "NAME": name,
                                "VARIABLE":kwargs['variable'],
                                "EPSG": str(epsg),
                                "ID": self.str_now,
                                "PROVIDER":provider}
        else:
            raise ValueError("Unrecognized file format {}".format(self.ext))

        # Assign colors/colormaps
        self.replacements['COLOR'] = self.choose_color_scheme()

        # Retrieve the template for a layer
        print("\tUsing layer template {}".format(template))
        with open(template) as fp:
            self.layer_template = "".join(fp.readlines())

            fp.close()

    def choose_color_scheme(self):
        """
        Whether it is a shapefile or raster or netcdf, this function is able
        to manipulate the replacement dictionary to produce the necessary
        color decisions

        Returns:
            color: string to be used to replace the keyword color in the templates
        """

        # String we are searching for kw to decide on colors
        if self.ftype == 'netcdf':
            # Search the variable name for the kewords
            search_str = self.replacements['VARIABLE'].lower()
        else:
            #Search the path
            search_str = self.replacements['PATH'].lower()

        ###### Universally choose colors ############

        # Use simple gray scale for hillshade rasters
        if 'hillshade' in search_str:
            color = './colormaps/hillshade.qml'

        # Use Custom dem colrmap for the elevation rasters
        elif 'dem' in search_str:
            color = './colormaps/dem_colormap.qml'

        # Use Custom dem colrmap for the elevation rasters
        elif 'veg_type' in search_str:
            color = './colormaps/veg_colormap.qml'

        # streams
        elif "net_thresh" in search_str:
            # Dark blue for streams
            color = "0,50,78,0"

        # Basin/subbasin
        elif 'basin' in search_str:
            # Charcoal
            color = "41,41,41,0"

        else:
            color = ''

        # If we have a colormap file use it only if it is a raster
        if color:
            if self.replacements['PROVIDER']=='gdal':
                # parse the colormap and inject it in to the qgis project
                with open(color) as fp:
                    lines = fp.readlines()
                    fp.close()

                    # Find the index in the colormap where pipe is an self.extract between the two of them
                    idx = [i for i,l in enumerate(lines) if 'pipe' in l]
                    lines = lines[idx[0] + 1:idx[1]]
                    color = "\t\t".join(lines)

        return color

    def generate_strs(self):
        """
        Produces the final three sets of strings to go in the project file
        """
        print("\tProcessing strings for a {}".format(self.ftype))
        declaration = str_swap(self.declaration, self.replacements)
        order = str_swap(self.order, self.replacements)
        layer_def = str_swap(self.layer_template, self.replacements)
        legend = str_swap(self.legend, self.replacements)

        return declaration, order, layer_def, legend

def create_layer_strings(files, epsg, variables=[], declarations='', order='', layers='', legends=''):
    """
    Create three strings to insert in to the qgis project

    Args:
        files: List of paths to georeferences tifs or shapefiles, all files should be in the EPSG projection
        epsg: EPSG value for the project (just for search replace, no reprojections occur)
        variables: Switch to netcdf type and loop over variables
        declarations: String for adding on to provided to force the order of a layer if need be
        order: String for adding on to provided to force the order of a layer if need be
        layers: String for adding on to provided to force the order of a layer if need be

    Returns:
        declarations: String representing layer declarations
        order: String representing order string in the project file
        layers: String representing the layer definitions
    """
    if type(files) != list:
        files = [files]

    if variables:
        loop_list = variables
        is_nc = True

    else:
        loop_list = files
        is_nc = False

    # Loop over either files or variables
    for vf in loop_list:
        if is_nc:
            print('Adding {} from {}'.format(vf, files[0]))
            qgs = QGISLayerMaker(files[0], epsg, variable=vf)
        else:
            print('Adding {}'.format(vf))
            qgs = QGISLayerMaker(vf, epsg)

        strs = qgs.generate_strs()
        declarations += strs[0]
        order += strs[1]
        layers += strs[2]
        legends += strs[3]

    return declarations, order, layers, legends

def main():

    parser = argparse.ArgumentParser(description='Build a qgis project for '
                                    'setting up a basin')
    parser.add_argument('-t','--geotiff', dest='tifs', nargs='+',
                        help='Paths to the geotifs to add, specifically looking'
                             ' for a hillshade and dem')
    parser.add_argument('-s','--shapefiles', dest='shapefiles', nargs='+',
                        help='Paths to the shapefiles')
    parser.add_argument('-n','--netcdf', dest='netcdf',
                        help='Path to the input topo file for AWSM')
    parser.add_argument('-v','--variables', dest='variables', nargs='+',
                        help='Variable names in the netcdf to add to the'
                             ' project')

    args = parser.parse_args()
    epsg = 32611

    ######## INPUTS ########
    print("\n\nAdding shapefiles to the project...")
    declarations, order, layers, legends = create_layer_strings(args.shapefiles, epsg)

    print("\n\nAdding variables from a netcdf to the project...")
    declarations, order, layers, legends = create_layer_strings(args.netcdf, epsg,
                                                    variables=args.variables,
                                                    declarations=declarations,
                                                    order=order,
                                                    layers=layers,
                                                    legends=legends)

    print("\n\nAdding geotiffs to the project...")
    declarations, order, layers, legend = create_layer_strings(args.tifs, epsg,
                                                        declarations=declarations,
                                                        order=order,
                                                        layers=layers,
                                                        legends=legends)
    # Populate replacement info
    replacements = \
    {
    "DECLARATIONS":declarations,
    "ORDER": order,
    "LAYERS": layers,
    "LEGEND": legend,
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
