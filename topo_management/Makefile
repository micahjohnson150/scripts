SOURCES := check_topos.py make_topos.py


install:
	# Link the python script so edits are reflected in realtime
	make uninstall
	for f in $(SOURCES); do \
		filename=$$(basename $$f .py) ; \
		echo $("Installing $$filename") ; \
		chmod +x $$f ; \
		ln $$f /usr/local/bin/$$filename ;\
		done


uninstall:
	# Remove the python script from the bin
	for f in $(SOURCES); do \
		filename=$$(basename $$f .py) ; \
		echo "Uninstalling $$filename" ; \
		rm -f /usr/local/bin/$$filename ; \
		done
