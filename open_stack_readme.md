# How to create OpenStack instance from GUI

## Log in

1. Go to 10.200.28.50/dashboard
2. Use domain "default"
3. Use your username and password

## Start an instance

1. Click on "Compute" tab
2. Click on "Instances"
3. Click on "Launch Instance"
  1. Enter name for instance
4. Click on "Source"
  1. Click the arrow on the right side of "Ubuntu 16.04"
  2. Select "Yes" on "Delete Volume on Instance Delete"
5. Click on "Flavor"
  1. Select the most appropriate flavor for you needs
6. Click on "Networks"
  1. Select NWRCNET
7. Click on "Key Pair"
  1. Create or import a key pair if you do not have one
  2. Make sure this is stored on your computer for use
  logging in.
  3. This part can be done later if needed
8. Click "Launch Instance"

## Associate IP

1. Click on "Associate Floating IP" from drop down on right side of your new instance
2. Select an IP Address from drop down box if available
3. Create a floating IP Address using the "+" if previous step didn't work

## Create and attach Volume

1. Click on "Volumes" tab
2. Click on "Volumes"
3. Click "Create Volume"
  1. Enter Volume Name
  2. Type up a nice description
  3. Leave "Volume Source" as "No source"
  4. Select the size you need. This is your storage volume
  5. Click "Create Volume"
4. Click back to Compute -> Instances
5. Click "Attach Volume" from drop down box on right side of
your instance
6. Select your Volume and hit "Attach Volume"

## Log into new instance
1. Use "ssh -i (file containing your key pair) ubuntu@10.200.28.(last two of your ip address)"
