#!/bin/bash
for REPO in $(ls ./)
	do
		if  [ $REPO != "pull.sh" ]
		then
			echo "WORKING ON: $REPO"
			cd $REPO
			git pull
		  cd ..
		fi
done
