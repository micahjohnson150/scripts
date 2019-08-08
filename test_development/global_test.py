global debug
import sys

global debug
debug = False

def fn():
	if debug:
		print("Debug is on")

	else:
		print("Debug is off")


debug = True

fn()
