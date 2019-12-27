# User ID as defined by your local machine
uid:=1001

# Local path to your input data which will be mapped to docker_input_dir (must be absolute)
local_input_dir:=/home/micahjohnson/projects/scripts/running_snobal

# Docker side directory which will be a copy of local_input_dir (must be absolute)
docker_input_dir:=/data

# IPW docker image name to use
ipw_image:=usdaarsnwrc/ipw:latest

# Arguments for snobal e.g. snobal <args>
snobal_args:=-z 2061 -t 60 -h inheight.txt -p ppt.txt -i input_data.txt -s snow_properties.txt -o snobal.txt -c -O normal

# Runs snobal by executing the shell script run_snobal with the correct directories mapped
run:
	docker run -u $(uid) -w $(docker_input_dir)	 --entrypoint snobal -v $(local_input_dir):$(docker_input_dir) $(ipw_image) $(snobal_args)



# Runs docker interactively with the directories mapped to use ipw commands live
interactive:
	docker run -it -u $(uid) -v $(local_input_dir):$(docker_input_dir) $(ipw_image)

# Use the python script to create the plot
plot:
	python plot.py
