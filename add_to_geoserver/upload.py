import json
import argparse
import sys
import requests
from urllib.parse import urljoin, urlparse
from shutil import copyfile
import os
from netCDF4 import Dataset, num2date
from subprocess import check_output
import logging
import coloredlogs
import certifi
from spatialnc.proj import add_proj
from spatialnc.utilities import copy_nc, mask_nc
from datetime import datetime as dt

__version__ = '0.1.0'

class AWSM_Geoserver(object):
    def __init__(self, fname, log=None, level="DEBUG"):

        # Setup external logging if need be
        if log==None:
            self.log = logging.getLogger(__name__)
        else:
            self.log = log

        # Assign some colors and formats
        coloredlogs.install(fmt='%(levelname)-5s %(message)s', level=level,
                                                               logger=self.log)

        self.log.info("\n=============================================\n"
                      "      Geoserver Upload Script v{}:\n"
                      "=============================================\n"
                      "".format(__version__))


        with open(fname) as fp:
            cred = json.load(fp)
            fp.close()
        self.password = cred['password']
        self.username = cred['username']
        self.url = urljoin(cred['url'], 'rest/')

        # Extract the base url
        self.base_url = urlparse(self.url).netloc
        self.credential = (self.username, self.password)
        self.pem = cred['pem']
        self.data = cred['data']

        # Names we want to remap
        self.remap = {'snow_density':'density',
                      'specific_mass':'SWE',
                      'thickness':'depth'}


    def make(self, resource, payload):
        """
        Wrapper for post request.

        Args:
            resource: Relative location from the http root
            payload: Dictionary containing data to transfer.

        Returns:
            string: request status
        """

        headers = {'content-type' : 'application/json'}
        request_url = urljoin(self.url, resource)
        self.log.debug("POST request to {}".format(request_url))
        r = requests.post(
            request_url,
            headers=headers,
            data=json.dumps(payload),
            verify=False,
            auth=self.credential
        )
        return r.raise_for_status()

    def get(self, resource):
        """
        Wrapper for requests.get function.
        Retrieves info from the resource and returns the dictionary from the
        json

        Args:
            resource: Relative location from the http root

        Returns:
            dict: Dictionary containing infor about the resource
        """

        headers = {'Accept':'application/json'}
        request_url = urljoin(self.url, resource)
        self.log.debug("GET request to {}".format(request_url))

        r = requests.get(
            request_url,
            verify=False,
            headers=headers,
            auth=self.credential
        )
        return r.json()

    def extract_data(self, fname, upload_type='modeled', espg=None, mask=None):
        """
        Args:
            fname: String path to a local file.
            upload_type: specifies whether to name a file differently
            espg: Projection code to use if projection information not found if
                  none, user will be prompted

        Returns:
            fname: New name of file where data was extracted.
        """

        # Check for netcdfs
        if fname.split('.')[-1] == 'nc':
            # AWSM related items should have a variable called projection
            ds = Dataset(fname, 'r')

            # Base file name
            bname = os.path.basename(fname)

            if upload_type=='modeled':

                # Add a parsed date to the string to avoid overwriting snow.nc
                self.log.info("Retrieving date from netcdf...")
                time = ds.variables['time']
                dates = num2date(time[:], units=time.units, calendar=time.calendar)
                self.date = dates[0].isoformat().split('T')[0]

                cleaned_date = "".join([c for c in self.date if c not in ':-'])[:-2]
                bname = bname.split(".")[0] + "_{}.nc".format(cleaned_date)
                fname = bname

                # Only copy some of the variables
                keep_vars = ['x','y','time','snow_density','specific_mass',
                                                           'thickness',
                                                           'projection']

                exclude_vars = [v for v in ds.variables.keys() if v not in keep_vars]
                mask_exlcude = []

            elif upload_type=='topo':
                self.date = dt.today().isoformat().split('T')[0]
                cleaned_date = "".join([c for c in date.isoformat() if c not in ':-'])[:-2]
                bname = bname.split(".")[0] + "_{}.nc".format(cleaned_date)
                fname = bname
                mask_exlcude = ['mask']

            # Create a copy nad mask
            self.log.info("Copying netcdf...")
            new_ds = copy_nc(ds, fname, exclude = exclude_vars)
            new_ds.close()

            self.log.info("Masking netcdf using {}...".format(mask))
            if mask == None:
                self.log.error("Please provide a netcdf containing a mask.")
                sys.exit()

            new_ds = mask_nc(fname, mask, exclude=mask_exlcude)

            # Check for missing projection
            if 'projection' not in new_ds.variables:
                self.log.info("Netcdf is missing projection information...")

                # Missing ESPG from args
                if espg == None:
                    espg = input("No projection detected. Enter the ESPG code for the data:\n")

                self.log.info("Adding projection information using ESPG code {}...".format(espg))
                new_ds = add_proj(new_ds, espg)


            new_ds.close()
            ds.close()

        return fname

    def copy_data(self, fname, basin, upload_type='modeled'):
        """
        Data for the geoserver has to be in the host location for this. We

        Copies data from users location to geoserver/data/<basin>/

        Args:
            fname: String path to a local file.
            basin: String name of the targeted basin/workspace to put the file in
            upload_type: specifies whether to name a file differently

        Returns:
            final_fname: The remote path to the file we copied
        """
        bname =  os.path.basename(fname)

        final_fname = os.path.join(self.data, basin, bname)
        self.log.info("Copying local data to remote, this may take a couple "
                      "minutes...")
        self.log.debug("SCP info:{} -----> {}".format(bname, final_fname))
        s = check_output(["scp", "-i", self.pem, fname, "ubuntu@{}:{}".format(
                                                            self.base_url,
                                                            final_fname)],
                                                            shell=False,
                                                            universal_newlines=True)

        return final_fname

    def exists(self, basin, store=None, layer=None):
        """
        Checks the geoserver if the object exist already by name. If basin
        store and layer are provided it will check all three and only return
        true if all 3 exist.

        Args:
            basin: String name of the targeted, this script assumes the basin
                   name and workspace are the same.
            store: String name of the data/coverage storage object.
            layer: String name of the layer

        Returns:
            bool: True if all non-None values of the basin,store,layer exists,
                  False otherwise
        """

        store_exists = None
        layer_exists = None

        # We always will check for the basins existance
        ws_exists = False

        # Does the workspace > datastore exist
        if store != None:
            store_exists = False

        # Does the workspace > datastore > layer exist
        if layer != None:
            layer_exists = False

        rjson = self.get('workspaces')

        # Are there any workspaces?
        if rjson['workspaces']:
            ws_info = rjson['workspaces']

            # Check if the basin exists as a workspace
            for w in ws_info['workspace']:
                if basin.lower() == w['name']:
                    ws_exists = True
                    break

            # Store existance requested
            if store != None:
                # Grab info about this existing workspace
                ws_dict = self.get(w['href'])

                # Grab info on rasters
                cs_dict = self.get(ws_dict['workspace']['coverageStores'])

                # Check if there are any coverage stores
                if cs_dict['coverageStores']:
                    cs_info = cs_dict['coverageStores']

                    # Check for matching name in the coverages
                    for cs in cs_info['coverageStore']:
                        if store == cs['name']:
                            store_exists = True
                            break

            # layer existance requested
            if layer != None:
                # Grab info about this existing store
                store_info = self.get(cs['href'])
                coverages = self.get(store_info['coverageStore']['coverages'])

                # Check to see if there any coverages at all
                if coverages['coverages']:
                    for cv in coverages['coverages']['coverage']:
                        if layer == cv['name']:
                            layer_exists = True

        result = [ws_exists, store_exists, layer_exists]
        expected = [r for r in result if r != None]
        truth = [r for r in result if r == True]

        msg = " > ".join([r for r in [basin, store, layer] if r !=None])

        if len(truth) == len(expected):
            self.log.debug("{} already exists on the geoserver.".format(msg))
            return True
        else:
            self.log.debug("{} doesn't exist on the geoserver.".format(msg))
            return False

    def create_basin(self, basin):
        """
        Creates a new basin on the geoserver. Important to note that this script
        treats the names of workspaces as the same name as the basin.

        Args:
            basin: String name of the new basin/workspace
        """

        create_ws = ask_user("You are about to create a new basin on the"
                             " geoserver called: {}\nAre you sure you want"
                             " to continue?".format(basin))
        if not create_ws:
            self.log.info("Aborting creating a new basin. Exiting...")
            sys.exit()

        else:
            self.log.info("Creating a new basin on geoserver...")
            payload = {'workspace': {'name':basin,
                                     'enabled':True}}

            rjson = self.make('workspaces', payload)

    def create_coveragestore(self, basin, store, filename, description=None):
        """
        Creates a coverage data store for raster type data on the geoserver.

        Args:
            basin: String name of the targeted basin/workspace
            store: String name of the new coverage data store
            filename: Netcdf to associate with store, must exist locally to geoserver

        """
        bname = os.path.basename(filename)

        # Check to see if the store already exists...
        if self.exists(basin, store=store):
            self.log.info("Coverage store {} exists...".format(store))
            sys.exit()
        else:
            resource = 'workspaces/{}/coveragestores.json'.format(basin)

            payload = {"coverageStore":{"name":store,
                                        "type":"NetCDF",
                                        "enabled":True,
                                        "_default":False,
                                        "workspace":{"name": basin},
                                        "configure":"all",
                                        "url":"file:basins/{}/{}".format(basin, bname)}}
            if description != None:
                payload['coverageStore']["description"] = description

            create_cs = ask_user("You are about to create a new geoserver"
                                 " coverage store called: {} in the {}\n Are "
                                 " you sure you want to continue?"
                                 "".format(store, basin))
            if not create_cs:
                self.log.info("Aborting creating a new coverage store. Exiting...")
                sys.exit()
            else:
                self.log.info("Creating a new coverage on geoserver...")
                self.log.debug(payload)
                rjson = self.make(resource, payload)

    def create_layer(self, basin, store, layer):
        """
        Create a raster layer on the geoserver

        Args:
            basin: String name of the targeted basin/workspace
            store: String name of the targeted data/coverage store
            layer: String name of the new layer to be made

        """
        resource = ("workspaces/{}/coveragestores/{}/coverages.json"
                   "".format(basin, store))

        native_name = layer.replace('_',' ')

        # Rename the isnobal stuff
        if native_name in ['snow_density','specific_mass','thickness']:
            name = self.remap[native_name]
        else:
            name = lyr_name

        # Human readable title for geoserver UI

        title = ("{} {} {}".format(basin,
                                   self.date,
                                   name)).replace("_"," ").title()

        # Add an associated Date to the layer
        if hasattr(self,'date'):
            name = "{} {}".format(name, self.date)

        lyr_name = layer.lower().replace(" ","_").replace('-','')

        payload = {"coverage":{"name":name,
                               "nativeName":lyr_name,
                               "nativeCoverageName":native_name,
                               "store":{"name": "{}:{}".format(basin, store)},
                               "enabled":True,
                               "title":title
                                }
                            }
        self.log.debug("Payload: {}".format(payload))
        response = self.make(resource, payload)

    def create_layers_from_netcdf(self, basin, store, layers=None):
        """
        Opens a netcdf locally and adds all layers to the geoserver that are in
        the entire image if layers = None otherwise adds only the layers listed.

        Args:
            basin: String name of the targeted basin/workspace
            store: String name of a targeted netcdf coverage store
            layers: List of layers to add, if none add all layers except x,y,
                    time, and projection
        """

        for name in layers:

            if self.exists(basin, store, name):
                self.log.info("Layer {} from store {} in the {} exists..."
                      "".format(name, store, basin))
                self.log.warning("Skipping layer {} to geoserver.".format(name))
            else:
                self.log.info("Adding {} from {} to the {}".format(name,
                                                           store,
                                                           basin))
                self.create_layer(basin, store, name)

    def upload(self, basin, filename, upload_type='modeled', espg=None, mask=None):
        """
        Generic upload function to redirect to specific uploading of special
        data types, under development, currently only topo images work. Requires
        a local filepath which is then uploaded to the geoserver.

        Args:
            basin: string name of the basin/workspace to upload to.
            filename: path of a local to the script file to upload
            upload_type: Determines how the data is uploaded
            mask: Filename of a netcdf containing a mask layer
        """
        self.log.info("Associated Basin: {}".format(basin))
        self.log.info("Data Upload Type: {}".format(upload_type))
        self.log.info("Source Filename: {}".format(filename))
        self.log.info("Mask Filename: {}".format(mask))

        # Ensure that this workspace exists
        if not self.exists(basin):

            self.create_basin(basin)

        # Reduce the size of netcdfs if possible return the new filename
        filename = self.extract_data(filename, upload_type=upload_type,
                                               espg=espg,
                                               mask=mask)

        # Copy users data up to the remote location
        remote_fname = self.copy_data(filename, basin, upload_type=upload_type)

        # Grab the layer names
        ds = Dataset(filename)
        layers = []
        for name, v in ds.variables.items():
            if name not in ['time','x','y','projection']:
                layers.append(name)

        if len(layers) == 0:
            self.log.error("No variables found in netcdf...exiting.")
            sys.exit()

        # Check for the upload type which determines the filename, and store type
        if upload_type == 'topo':
            self.submit_topo(remote_fname, basin, layers=layers)

        elif upload_type == 'modeled':
            self.submit_modeled(remote_fname, basin, layers=layers)

        elif upload_type == 'flight':
            self.log.error("Uploading flights is undeveloped")

        elif upload_type == 'shapefile':
            self.log.error("Uploading shapefiles is undeveloped")

        else:
            raise ValueError("Invalid upload type!")

    def submit_topo(self, filename, basin, layers=None):
        """
        Uploads the basins topo images which are static. These images include:
        * dem
        * basin mask
        * subbasin masks
        * vegetation images relating to types, albedo, and heights

        Args:
            filename: Remote path of a netcdf to upload
            basin: Basin associated to the topo image
            layers: Netcdf variables names to add as layers on GS
        """
        # Always call store names the same thing, <basin>_topo
        store_name = "{}_topo".format(basin)
        description = ("NetCDF file containing topographic images required for "
                       "modeling the {} watershed in AWSM.\n"
                       "Uploaded: {}").format(basin, self.date)
        self.create_coveragestore(basin, store_name, filename, description=description)

        self.create_layers_from_netcdf(filename, basin, store_name,
                                                 layers=layers)

    def submit_modeled(self, filename, basin, layers=None):
        """
        Uploads the basins modeled data. These images include:
        * density
        * specific_mass
        * depth

        Args:
            filename: Remote path of a netcdf to upload
            basin: Basin associated to the topo image
            layers: Netcdf variables names to add as layers on GS

        """

        # Always call store names the same thing, <basin>_snow_<date>
        store_name = "{}_{}".format(basin,
                                    os.path.basename(filename).split(".")[0])
        # Create Netcdf store
        description = ("NetCDF file containing modeled snowpack images from "
                       "the {} watershed produced by AWSM.\n"
                       "Model Date: {}"
                       "Date Uploaded: {}").format(basin,
                                       self.date,
                                       dt.today().isoformat().split('T'))

        self.create_coveragestore(basin, store_name, filename,
                                                     description=description)

        # Create layers density, specific mass, thickness
        self.create_layers_from_netcdf(basin, store_name, layers=layers)


def ask_user(msg):
    """
    Asks the user yes no questions

    Args:
        msg: question to display

    Returns:
        response: boolean indicating whether to proceed or not.
    """

    acceptable = False
    while not acceptable:
        ans = input(msg+' (y/n)\n')

        if ans.lower() in ['y','yes']:
            acceptable = True
            response = True

        elif ans.lower() in ['n','no']:
            acceptable = True
            response = False
        else:
            self.log.info("Unrecognized answer, please use (y, yes, n, no)")
    return response


def main():
    # Parge command line arguments
    p = argparse.ArgumentParser(description="Submits either a lidar flight,"
                                            " AWSM/SMRF topo image, or AWSM "
                                            " modeling results to a geoserver")

    p.add_argument('-f','--filename', dest='filename',
                    required=True,
                    help="Path to a file containing either a lidar flight,"
                    "AWSM/SMRF topo image, or AWSM modeling results or shapefiles"
                    )

    p.add_argument('-b','--basin', dest='basin',
                    required=True, choices=['brb', 'kaweah', 'kings', 'lakes', 'merced', 'sanjoaquin'],
                    help="Basin name to submit to which is also the geoserver"
                         " workspace name")

    p.add_argument('-c','--credentials', dest='credentials',
                    default='./geoserver.json',
                    required=False,
                    help="JSON containing geoserver credentials for logging in")

    p.add_argument('-t','--upload_type', dest='upload_type',
                    default='modeled',
                    choices=['flight','topo','shapefile','modeled'],
                    required=False,
                    help="Upload type dictates how some items are uploaded.")

    p.add_argument('-e','--espg', dest='espg',
                    type=int, default=None,
                    help="espg value representing the projection information to"
                    "add to the netcdf")

    p.add_argument('-m','--mask', dest='mask',
                    type=str, default=None,
                    help="Netcdf containing a mask layer")

    args = p.parse_args()

    # Get an instance to interact with the geoserver.
    gs = AWSM_Geoserver(args.credentials)

    # Upload a file
    gs.upload(args.basin,args.filename, upload_type=args.upload_type,
                                        espg=args.espg,
                                        mask=args.mask)


if __name__ =='__main__':
    main()
