# FAQ

## HLE Error

When you run snobal/isnobal you may run into the following error:

```bash

snobal: ERROR:
	Error at record 51
	(IPW error is: hle1 did not converge)

```

Here is what you need to know:

hle - sensible and latent heat from data at 1 height

In Danny Marks (the author of this function) thesis:

H = rho C_p K_11 (Ta - Tg)
