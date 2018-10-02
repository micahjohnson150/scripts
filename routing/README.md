To use the scripts use crop.py to prep the required files.

```
python crop.py examples/topo.nc examples/em.nc -m "mask tollgate" -o "examples/swi.nc"
```

Run the model for two days
```
 python rout.py examples/swi.nc -d 2
 ```
