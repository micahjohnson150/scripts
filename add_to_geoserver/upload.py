import json
from geoserver.catalog import Catalog
import argparse
import sys


def gsconnect(cred_json):
    """
    Returns a geoserver Catalog

    Args:
        cred_json: protected JSON file containing url,username,password for the
                   geoserver
    """
    with open(cred_json) as fp:
        cred = json.load(fp)
        fp.close()

    cat = Catalog(cred['url'], cred[ "username"], cred['password'])

    return cat


def upload(fname):
    """
    Upload a netcdf to the user on the instance, then move it to our data drive

    Args:
        fname: path to a file to move
    """
    pass


def exists(cat, name, type):
    """
    Checks the geoserver if the object type by name already exists

    Args:
        name: name of object
        cat: catalog instance from the geoserver
        type: must be workspace, store, layer
    """
    if type == 'workspace':
        names = [w.name for w in cat.get_workspaces()]
    elif type == 'store':
        names = [s.name for s in cat.get_stores()]
    elif type == 'layer':
        names = [w.name for w in cat.get_workspaces()]
    else:
        raise ValueError("Invalid entry for type, must be workspace, store, layer")

    if name in names:
        return True
    else:
        return False

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


def create(cat, path, workspace, store=None, layer=None):
    """
    Prompts user to create a new workspace, store or layer if they do not exists.

    Args:
        cat: Geoserver catalog object
        workspace: name of the workspace also basin name
        path: Path to file to be uploaded
        store: name of the data store
        layer: name of the layer
    """

    if store == None and layer == None:
        obj = 'Workspace'
        name = workspace
        workspace = "GeoServer"

    elif store != None and layer == None:
        obj = 'Datastore'
        name = store

    elif store != None and layer != None:
        obj = 'Layer'
        name = layer

    else:
        print("You must use store with layer.")
        sys.exit()

    msg = ("{} {} does not exist in the {},\n Do you want to create it?"
                                                "".format(obj, name, workspace))
    if workspace == "GeorServer":
        workspace = name

    response = ask_user(msg)

    if response == True:

        print("Creating new {} named {} in {}".format(obj, name, workspace))

        # New workspace
        if obj.lower() == 'workspace':
            gs_obj = cat.create_workspace(name,uri= name.replace(' ','_'))
            gs_obj.enabled = True
            gs_obj.save()

        # Datastores for hold netcdf
        if obj.lower() == 'datastore':
            gs_obj = cat.create_coveragestore(name, path=path,
                                                    workspace=workspace,
                                                    type='NetCDF',
                                                    create_layer=False)
        # WMS Layer
        if obj.lower() == 'layer':
            gs_obj = cat.create_wmslayer(workspace, store, layer)


    else:
        print("Not creating anything, exiting...")
        sys.exit()

    return gs_obj


def publish_data(cat, path, basin):
    """
    Finalizes and publishes the data on to the geoserver. The file must be on the
    instance already in the data folder that the geoserver sees. The filename
    must be the path to the file on the server instance, not the local.

    Args:
        server_fname: Server side path to the data to add
    """
    name = 'test'
    workspace = basin
    if not exists(cat, basin, type='workspace'):
        print("Checking if basin {} exists...".format(workspace))
        gs_obj = create(cat, path, basin)

    print("Checking if datastore {} in {} exists...".format(name,workspace))
    if exists(cat, name, type='store'):
        print("Datastore {} already exists, use a different datastore name"
                                                                "".format(name))
        sys.exit()

    else:
        gs_obj = create(cat, path, basin, store=name)



def main():
    # Parge command line arguments
    p = argparse.ArgumentParser(description="Submits either a lidar flight,"
                                            " AWSM/SMRF topo image, or AWSM "
                                            " modeling results to a geoserver")

    p.add_argument('-f','--netcdf', dest='netcdf',
                    required=True,
                    help="Path to a netcdf containing either a lidar flight,"
                    "AWSM/SMRF topo image, or AWSM modeling results"
                    )

    p.add_argument('-b','--basin', dest='basin',
                    required=True,
                    help="Basin name to submit to which is also the geoserver"
                         " workspace name")

    p.add_argument('-c','--credentials', dest='credentials',
                    default='./geoserver.json',
                    required=False,
                    help="JSON containing geoserver credentials for logging in")

    args = p.parse_args()


    cat = gsconnect(args.credentials)
    publish_data(cat, args.netcdf, args.basin)


if __name__ =='__main__':
    main()
