import json
import argparse
import sys
import requests
from urllib.parse import urljoin, urlparse
from shutil import copyfile
import os
from netCDF4 import Dataset
from subprocess import check_output

class AWSM_Geoserver(object):
    def __init__(self, fname):

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


    def make(self, resource, payload):
        """
        wrapper for post request.

        Args:
            resource: Relative location from the http root
            payload: Dictionary containing data to transfer.

        Returns:
            string: request status
        """

        headers = {'content-type' : 'application/json'}
        request_url = urljoin(self.url, resource)
        r = requests.post(
            request_url,
            headers=headers,
            data=json.dumps(payload),
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

        r = requests.get(
            request_url,
            headers=headers,
            auth=self.credential
        )
        return r.json()

    def copy_data(self, fname, basin):
        """
        Data for the geoserver has to be in the host location for this. We
        working locally for now so we will create a mock function to move data
        then upgrade to scp of sorts.

        Copies data from users location to geoserver/data/<basin>/

        Args:
            fname: String path to a local file.
            basin: String name of the targeted basin/workspace to put the file in

        Returns:
            final_fname: The remote path to the file we copied
        # """

        bname =  os.path.basename(fname)
        final_fname = os.path.join(self.data, basin, bname)

        # files = {'file': open(fname, 'rb')}
        # print(files['file'])
        # headers = {"Content-Type": "application/zip",
        #             "Accept": "application/json"}
        #
        # # Use rest api to add a new resource
        # location_url = urljoin(self.url, "resource/{}/{}".format(basin, bname))
        # print("Copying {} to geoserver {}".format(bname, location_url))
        # r = requests.put(location_url, files=files, headers=headers)
        # print(r)
        s = check_output("scp -i {} {} ubuntu@{}:{}".format(self.pem,
                                                            fname,
                                                            self.base_url,
                                                            final_name))

        return final_name

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

        if len(truth) == len(expected):
            return True
        else:
            return False

    def create_basin(self, basin):
        """
        Creates a new basin on the geoserver. Important to note that this script
        treats the names of workspaces as the same name as the basin.

        Args:
            basin: String name of the new basin/workspace
        """

        create_ws = ask_user("You are about to create a new basin on the"
                             " geoserver called: {}\n Are you sure you want"
                             " to continue?".format(basin))
        if not create_ws:
            print("Aborting creating a new basin. Exiting...")
            sys.exit()

        else:
            print("Creating a new basin on geoserver...")
            payload = {'workspace': {'name':basin,
                                     'enabled':True}}

            rjson = self.make('workspaces', payload)

    def create_coveragestore(self, basin, store, filename):
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
            print("Coverage store {} exists...".format(store_name))

        resource = 'workspaces/{}/coveragestores.json'.format(basin)

        payload = {"coverageStore":{"name":store,
                                    "type":"NetCDF",
                                    "enabled":True,
                                    "_default":False,
                                    "workspace":{"name":basin},
                                    "configure":"all",
                                    "url":"file:{}/{}".format(basin,
                                                              bname)}}

        create_cs = ask_user("You are about to create a new geoserver"
                             " coverage store called: {} in the {}\n Are "
                             " you sure you want to continue?"
                             "".format(store, basin))
        if not create_cs:
            print("Aborting creating a new coverage store. Exiting...")
            sys.exit()
        else:
            print("Creating a new coverage on geoserver...")
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

        title = ("{} {}".format(basin, layer)).replace("_"," ").title()
        lyr_name = layer.lower().replace(" ","_")

        payload = {"coverage":{"name":lyr_name,
                               "nativeName":lyr_name,
                               "nativeCoverageName":layer.replace(" ", "_"),
                               "store":{"name": "{}:{}".format(basin, store)},
                               "enabled":True,
                               "title":title
                                }
                            }
        response = self.make(resource, payload)

    def create_layers_from_netcdf(self, filename, basin, store, layers=None):
        """
        Opens a netcdf locally and adds all layers to the geoserver that are in
        the entire image if layers = None otherwise adds only the layers listed.

        Args:
            filename: Path of a local netcdf.
            basin: String name of the targeted basin/workspace
            store: String name of a targeted netcdf coverage store
            layers: List of layers to add, if none add all layers except x,y,
                    time, and projection
        """

        ds = Dataset(filename)

        undesired = ['x','y','time','projection']
        if layers != None:
            for name, var in ds.variables.items():
                if name not in layers:
                    undesired.append(name)

        with Dataset(filename) as ds:
            for name, var in ds.variables.items():
                if name.lower() not in ['x','y','time','projection']:
                    if self.exists(basin, store, name):
                        print("Layer {} from store {} in the {} exists..."
                              "".format(name, store, basin))
                    else:
                        print("Adding {} from {} to the {}".format(name,
                                                                   store,
                                                                   basin))
                        self.create_layer(basin, store, name)

    def upload(self, basin, filename, upload_type='modeled'):
        """
        Generic upload function to redirect to specific uploading of special
        data types, under development, currently only topo images work. Requires
        a local filepath which is then uploaded to the geoserver.

        Args:
            basin: string name of the basin/workspace to upload to.
            filename: path of a local to the script file to upload
            upload_type:
        """
        # Ensure that this workspace exists
        if not self.exists(basin):
            self.create_basin(basin)

        # Copy users data up to the remote location
        remote_fname = self.copy_data(filename, basin)

        # Check for the upload type which determines the filename, and store type
        if upload_type == 'topo':
            self.upload_topo(remote_fname, basin)

        elif upload_type == 'modeled':
            self.upload_modeled(remote_fname, basin)

        elif upload_type == 'flight':
            print("Uploading flights is undeveloped")

        elif upload_type == 'shapefile':
            print("Uploading shapefiles is undeveloped")

        else:
            raise ValueError("Invalid upload type!")

    def upload_topo(self, filename, basin):
        """
        Uploads the basins topo images which are static. These images include:
        * dem
        * basin mask
        * subbasin masks
        * vegetation images relating to types, albedo, and heights

        Args:
            filename: Remote path of a netcdf to upload
            basin: Basin associated to the topo image
        """
        # Always call store names the same thing, <basin>_topo
        store_name = "{}_topo".format(basin)

        self.create_coveragestore(basin, store_name, filename)

        self.create_layers_from_netcdf(filename, basin, store_name)

    def upload_modeled(self, filename, basin):
        """
        Uploads the basins modeled data. These images include:
        * density
        * specific_mass

        Args:
            filename: Remote path of a netcdf to upload
            basin: Basin associated to the topo image
        """

        # Always call store names the same thing, <basin>_snow_<date>
        store_name = "{}_snow_{}".format(basin, date)

        self.create_coveragestore(basin, store_name, filename)

        self.create_layers_from_netcdf(filename, basin, store_name,
                                       layers=['snow_density','specific_mass'])


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
            print("Unrecognized answer, please use (y, yes, n, no)")
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
                    required=True,
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

    args = p.parse_args()

    # Get an instance to interact with the geoserver.
    gs = AWSM_Geoserver(args.credentials)

    # Upload a file
    gs.upload(args.basin,args.filename, upload_type=args.upload_type)


if __name__ =='__main__':
    main()
