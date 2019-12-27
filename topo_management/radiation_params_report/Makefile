colormap:
	python scripts/make_veg_style.py

veg_layers:
	python scripts/gather_veg_values.py

histogram:
	python ../make_hist.py veg_type

doc:
	python scripts/make_preview.py
	pandoc veg_k_tau.md -o veg_k_tau.pdf
