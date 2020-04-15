sudo sh -c 'echo "deb https://qgis.org/ubuntugis  xenial main" >> /etc/apt/sources.list'
sudo sh -c 'echo "deb-src https://qgis.org/ubuntugis xenial main" >> /etc/apt/sources.list'
sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable

wget -O - https://qgis.org/downloads/qgis-2019.gpg.key | gpg --import
gpg --fingerprint CAEB3DC3BDF7FB45
gpg --export --armor CAEB3DC3BDF7FB45 | sudo apt-key add -

sudo apt-get update
sudo apt-get update && sudo apt-get install qgis python-qgis qgis-plugin-grass
sudo apt-get upgrade
