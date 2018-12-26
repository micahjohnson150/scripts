import json
import argparse
import sys
import requests
from urllib.parse import urljoin


class AWSM_Geoserver(object):
    def __init__(self, fname):

        with open(fname) as fp:
            cred = json.load(fp)
            fp.close()

        self.password = cred['password']
        self.username = cred['username']
        self.url = cred['url']
        self.credential = (self.username, self.password)

    def pushnc(self, resource, filename):

        headers = {"content-type": "application/zip",
                   "Accept": "application/json"}

        request_url = urljoin(self.url, resource)

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
        print(r)
        return r.json()

    def exists(self, basin, store=None, layer=None, upload_type='modeled'):
        """
        Checks the geoserver if the object type by name already exists

        Args:

        """
        store_exists = None
        lyr_exists = None

        # Does the workspace exist
        ws_exists = False

        # Does the workspace > datastore exist
        if store != None:
            store_exists = False

        # Does the workspace > datastore > layer exist
        if layer != None:
            lyr_exists = False

        rjson = self.get('workspaces')

        # Are there any workspaces?
        if rjson['workspaces']:
            ws_info = rjson['workspaces']

            # Check if the basin exists as a workspace
            for w in ws_info['workspace']:
                if basin.lower() == w['name']:
                    ws_exists = True

                    if store != None:
                        # Grab info about this existing workspace
                        ws_dict = self.get(w['href'])
                        if upload_type != 'shapefile':
                            # Grab info on rasters
                            cs_dict = \
                                self.get(ws_dict['workspace']['coverageStores'])

                            # Check if there are any coverage stores
                            if cs_dict['coverageStores']:
                                cs_info = cs_dict['coverageStores']
                                # Check for matching name in the coverages
                                for cs in cs_info['coverageStore']:
                                    print(self.get(cs['href']))

                                    if store == cs['name']:
                                        store_exists = True
                                        break

                        else:
                            # Grab info on datastores
                            ds_dict = self.get(ws_dict['workspace']['dataStores'])

                            # Check if there are any coverage stores
                            if ds_dict['dataStores']:
                                # Check for matching name in the dataStores
                                for ds in ds_dict['dataStores']['dataStore']:
                                    if store == ds['name']:
                                        store_exists = True

                                        # Grab info about this existing shapfiles store
                                        lyr_dict = self.get(ds['href'])
                                        break
            if layer != None:
                #rjson = self.get('layers')
                pass

        result = [ws_exists, store_exists, lyr_exists]
        expected = [r for r in result if r != None]
        truth = [r for r in result if r == True]

        if len(truth) == len(expected):
            return True
        else:
            return False

    def create_coveragestore(self, basin, store, filename, raster_type='topo'):
        """
        """

        if not self.exists(basin, store):
            if raster_type == 'topo':
                store_name = "{}_topo".format(basin)

                resource = 'workspaces/{}/coveragestores.json'.format(basin)

                payload = {"coverageStore":{"name":store_name,
                                            "type":"NetCDF",
                                            "enabled":True,
                                            "_default":False,
                                            "workspace":{"name":basin},
                                            "url":"file:{}".format(filename)}}

            elif raster_type == 'modeled':
                pass

            create_cs = ask_user("You are about to create a new geoserver"
                                 " coverage store called: {} in the {}\n Are "
                                 " you sure you want to continue?"
                                 "".format(store, basin))
            if not create_cs:
                print("Aborting creating a new datastore. Exiting...")
                sys.exit()
            else:
                print("Creating a new datastore on geoserver...")
                rjson = self.make(resource, payload)
                print(rjson)
                rjson = self.pushnc(resource, filename)

    def create_basin(self, basin):
        """
        Handles creating all the necessary stuff in the geoserver
        """

        if not self.exists(basin):
            create_ws = ask_user("You are about to create a new basin on the geoserver called:"
                     " {}\n Are you sure you want to continue?".format(basin))
            if not create_ws:
                print("Aborting creating a new basin. Exiting...")
                sys.exit()
            else:
                print("Creating a new basin on geoserver...")
                payload = {'workspace': {'name':basin}}

                rjson = self.make('workspaces', payload)


    def upload(self, basin, filename, upload_type='modeled'):
        """
        Generic upload function to redirect to specific uploading
        """
        if upload_type == 'topo':
            self.upload_topo(basin, filename)

        elif upload_type == 'flight':
            pass
        elif upload_type == 'modeled':
            pass
        elif upload_type == 'shapefile':
            pass
        else:
            raise ValueError("Invalid upload type!")


    def upload_topo(self, basin, filename):
        store_name = "{}_topo".format(basin)

        if not self.exists(basin, store=store_name):
            self.create_coveragestore(basin, store_name, filename, raster_type='topo')

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
