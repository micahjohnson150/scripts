import os
import sys
from subprocess import check_output
import argparse
import time
import coloredlogs
import logging


def grib2nc(f_hrrr, output=None, external_logger=None):
	"""
	Converts grib files to netcdf using HRRR forecast data and the
	variables required by the SMRF.
	Uses the wgrib2 command to identify variable names and uses that to filter
	the output from the commandline.

	args:
		f_hrrr: Path to a HRRR grib file
		output: Path to output the resulting netcdf
		external_logger: External logger is desired

	"""
	start = time.time()
	if external_logger == None:
		fmt = "%(levelname)s: %(msg)s"
		log = logging.getLogger(__name__)
		coloredlogs.install(logger=log, fmt=fmt)


	msg = "GRIB2NC Converter Utility"
	log.info(msg)
	log.info("=" * len(msg))

	# criteria dictionary for extracting variables, CASE MATTERS
	criteria = {'air_temp': {
	            	'wgrib2 keys':[":TMP Temperature","2 m"]},

				'dew_point': {
				'wgrib2 keys':[":DPT","2 m"]},

				'relative_humidity': {
				'wgrib2 keys':[":RH Relative Humidity","2 m"]
	            },
	        'wind_u': {
				'wgrib2 keys':[":UGRD U-Component","10 m"]

	            },
	        'wind_v': {
				'wgrib2 keys':[":VGRD V-Component","10 m"]

	            },
	        'precip_int': {
				'wgrib2 keys':[":APCP Total Precipitation"]

	            },
	        'short_wave': {
				'wgrib2 keys':['Downward Short-Wave Radiation Flux', ':surface']
	            },
	        }

	# No output file name used, use the original plus a new extension
	if output == None:
		output = ".".join(os.path.basename(f_hrrr).split(".")[0:-1]) + ".nc"

	grib_vars = ""
	var_count = 0
	# Cycle through all the variables and export the grib var names
	for k,v in criteria.items():
		log.info("Attempting to extract grib name for {} ".format(k))

		cmd = "wgrib2 -v {} ".format(f_hrrr)

		# Add all the search filters
		for kw in v["wgrib2 keys"]:
			cmd += '| egrep "({})" '.format(kw)
		# Run the command

		#cmd += " -netcdf {}".format(output)
		s = check_output(cmd, shell=True).decode('utf-8')

		# Check if we only identify one variable based on line returns
		return_count = len([True for c in s if c == '\n'])

		if return_count != 1:
			log.warning("Found multiple variable entries for keywords "
						"associated with {}".format(k))
			var_count += return_count
		else:
			var_count += 1
		# Add the grib var name to our running string/list
		grib_vars += s

	log.info("Extracting {} variables and converting to netcdf...".format(var_count))
	log.info("Outputting to: {}".format(output))

	# Using the var names we just collected run wgrib2 for netcdf conversion
	cmd = 'echo "{}" | wgrib2 -i {} -netcdf {}'.format(grib_vars, f_hrrr, output)
	s = check_output(cmd, shell=True)

	log.info("Complete! Elapsed {:0.0f}s".format(time.time()-start))


def grib2nc_cli():
	p = argparse.ArgumentParser(description="Command line tool for converting"
								" HRRR grib files to netcdf using only the "
								" variables we want.")

	p.add_argument(dest="hrrr", help="Path to the HRRR file containing the"
	 								 " variables for SMRF")
	p.add_argument("-o", "--output", dest="output", required=False,
												default=None,
	            								help="Path to output the netcdf"
												" file if you don't want it"
												" renamed the same as the hrrr"
												" file with a different"
												" extension.")
	args = p.parse_args()
	grib2nc(args.hrrr, args.output)

if __name__ == "__main__":
	grib2nc_cli()
