from subprocess import Popen


cmd = "guds -f snow.nc -t modeled -b kaweah -m ../../basin_ops/kaweah/topo/topo.nc -y -d -e 32611"
s = Popen(cmd,shell=True)
s.wait()
