# Remove an google earth install
sudo apt remove google-earth-*

# Remove any old ppa repos
sudo rm -i /etc/apt/sources.list.d/*-earth*

# Download the last link available from google earth
sudo apt-get install gdebi -y

# Download the correct deb and install it
wget https://dl.google.com/linux/earth/deb/pool/main/g/google-earth-pro-stable/google-earth-pro-stable_7.1.8.3036-r0_amd64.deb /tmp/google-earth-pro-stable_7.1.8.3036-r0_amd64.deb
sudo gdebi -n /tmp/google-earth-pro-stable_7.1.8.3036-r0_amd64.deb
