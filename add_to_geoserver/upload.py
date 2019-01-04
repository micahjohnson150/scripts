import json
import argparse
import sys
import requests
from urllib.parse import urljoin
from shutil import copyfile
import os
from netCDF4 import Dataset


class AWSM_Geoserver(object):
    def __init__(self, fname):

        with open(fname) as fp:
            cred = json.load(fp)
            fp.close()

        self.password = cred['password']
        self.username = cred['username']
        self.url = cred['url']
        self.credential = (self.username, self.password)

    def pushf(self, resource, filename):
        """
        Attaches file to the store

        """

        headers = {"content-type": "application/zip",
                   "Accept": "application/json"}

        request_url = urljoin(self.url, resource)
        request_url = urljoin(request_url,os.path.basename(filename))

        with open(filename, 'rb') as f:
            r = requests.put(
                request_url,
                data=f,
                headers=headers,
                auth=self.credential
            )
        return r.json()


    def make(self, resource, payload):

        headers = {'content-type' : 'application/json'}
        request_url = urljoin(self.url, resource)

        r = requests.post(
            request_url,
            headers=headers,
            data=json.dumps(payload),
            auth=self.credential
        )

        return r.raise_for_status()

    def put(self, resource, payload):

        headers = {'content-type' : 'application/json'}
        request_url = urljoin(self.url, resource)

        r = requests.put(
            request_url,
            headers=headers,
            data=json.dumps(payload),
            auth=self.credential
        )

        return r.raise_for_status()

    def get(self, resource):
        """
        Use for getting information from geoserver
        """
        headers = {'Accept' : 'application/json'}
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

        """
        bname =  os.path.basename(fname)
        final_name = ('/home/micahjohnson/projects/nwrc_geoserver/data/{}/{}'
                      ''.format(basin, bname))

        print("Copying {} to geoserver {}".format(bname, final_name))
        copyfile(os.path.abspath(fname), final_name)

        return final_name

    def exists(self, basin, store=None, layer=None, upload_type='modeled'):
        """
        Checks the geoserver if the object type by name already exists

        Args:

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

                if upload_type != 'shapefile':
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

                # Shapefile type
                else:
                    print("Shapefiles not developed yet!")
                    sys.exit()
                    # # Grab info on datastores (vector data)
                    # ds_dict = self.get(ws_dict['workspace']['dataStores'])
                    #
                    # # Check if there are any coverage stores
                    # if ds_dict['dataStores']:
                    #     # Check for matching name in the dataStores
                    #     for ds in ds_dict['dataStores']['dataStore']:
                    #         if store == ds['name']:
                    #             store_exists = True
                    #
                    #             # Grab info about this existing shapfiles store
                    #             lyr_dict = self.get(ds['href'])
                    #             break

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

    def create_coveragestore(self, basin, store, filename):
        """
        Create a data store for raster data
        """
        bname = os.path.basename(filename)
        if not self.exists(basin, store):
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
        Create a layer
        """
        title = "{} {}".format(basin, layer).replace("_"," ")
        lyr_name = layer.lower().replace(" ","_")
        print("Adding layer {}".format(layer))
        resource = 'workspaces/{}/coveragestores/{}/coverages.json'.format(basin, store)
        payload = {"coverage":{"name":lyr_name,
                               "nativeName":lyr_name,
                               "nativeCoverageName":layer.replace(" ","_"),

                               "store":{"name": "{}:{}".format(basin, store)},
                                #"nativeFormat":"NetCDF",
                                "enabled":True,
                            #    "supportedFormats":{"string":["GEOTIFF","GIF","PNG","JPEG","TIFF"]},
                            #    "namespace":{"name":basin,
                            #                "href":"{}/namespaces/{}.json".format(self.url,basin)},
                                "title":title.capitalize(),

                                }
                            }
        rjson = self.get(resource)
        response = self.make(resource, payload)
        print("Layer: {} Response: {}".format(layer,response))

    def create_basin(self, basin):
        """
        Handles creating all the necessary stuff in the geoserver
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
                                    # 'uri':basin.replace(' ','_'),
                                     'enabled':True}}

            rjson = self.make('workspaces', payload)

    def upload(self, basin, filename, upload_type='modeled'):
        """
        Generic upload function to redirect to specific uploading
        """
        # Ensure that this workspace exists
        if not self.exists(basin):
            self.create_basin(basin)

        # Copy users data up to the remote location
        remote_fname = self.copy_data(filename, basin)

        # Check for the upload type which determines the filename, and store type
        if upload_type == 'topo':
            self.upload_topo(remote_fname, basin)
        elif upload_type == 'flight':
            pass
        elif upload_type == 'modeled':
            pass
        elif upload_type == 'shapefile':
            pass
        else:
            raise ValueError("Invalid upload type!")

    def upload_topo(self, filename, basin):
        """
        Uploads the basins topo images which are static. These images include:
        * dem
        * basin mask
        * subbasin masks
        * vegetation images relating to types, albedo, and heights
        """
        # Always call store names the same thing, <basin>_topo
        store_name = "{}_topo".format(basin)

        # Check to see if the store already exists...
        if self.exists(basin, store=store_name):
            print("Data store {} exists...".format(store_name))

        self.create_coveragestore(basin, store_name, filename)

        self.create_layers_from_netcdf(filename, basin, store_name)

    def create_layers_from_netcdf(self, filename, basin, store, layers=None):
        """
        Since I am unable to figure out how geoserver sees the individual layers,
        I am going to add them using the names locally and link them to the store
        """

        with Dataset(filename) as ds:
            for name, var in ds.variables.items():
                if name.lower() not in ['x','y','time','projection']:
                    if self.exists(basin, store, name):
                        print("Layer {} from store {} in the {} exists...".format(name, store, basin))
                    else:
                        print("Adding {} from {} to the {}".format(name, store, basin))
                        self.create_layer(basin, store, name)
            ds.close()

def ask_user(msg):
    """
    Asks the user yes no questions
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


    gs = AWSM_Geoserver(args.credentials)
    gs.upload(args.basin,args.filename, upload_type=args.upload_type)


if __name__ =='__main__':
    main()
