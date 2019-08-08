# Pseudo Code for how NASDE models are used in SMRF

## Preface
This is written to describe in detail how smrf calculate the new accumulated
snow density. This describes how it was performed as of May 30, 2017.

The issue is that has occurred is that the model was written with the intent
of using storm precipitation mass with hourly dew point temperature, however as
of April 2, 2019 we realized the `distributeMarks2017` in precipitation.py is
not passing storm mass as of May 30, 2017 but is instead passing the class
attribute `self.precip` which is hourly precipitation that is distributed.

Source code (05-30-2017): https://github.com/USDA-ARS-NWRC/smrf/tree/7eebba6569bca8700a91fac936d7352578913d49
Commit that broke it: https://github.com/USDA-ARS-NWRC/smrf/commit/7eebba6569bca8700a91fac936d7352578913d49

NASDE Equation Description: https://smrf.readthedocs.io/en/latest/smrf.envphys.html#smrf.envphys.snow.marks2017
NASDE Marks2017 Source: https://github.com/USDA-ARS-NWRC/smrf/blob/7eebba6569bca8700a91fac936d7352578913d49/smrf/envphys/snow.py#L229


## SMRF Framework


### PSEUDO CODE

``` python

storms = Calculate_Storms(precip_time_series)

storm_totals = Sum_Storm_mass(precip_time_series)

corrected_precip = Correct_Precip(precip_time_series)


for time in run_hours:

    Distribute_air_temp(air_temp_time_series)

    Distribute_vapor_pressure(vapor_pressure_time_series)

    Calculate_Dew_point(vapor_pressure_image)

    Distribute_precip(corrected_precip)

    if time in storms:

      distribute_storm_total(storm_totals[time], corrected_precip)

    if minimum(dew_point_image) < 2.0 and in_storming_period:

      # Note this was the mistake discovered  should be storm_total_image here not precip_image
      percent_snow, density calc_phase_and_density(dew_point_image, precip_image)

```

### Explanation

1. Calculate Storm definitions basin wide using vector precip timeseries.
2. Correct the precip time series so no precip is outside of the storm definitions.
3. Distribute air temp.
4. Distribute vapor pressure
5. Calculate the dew point.
6. Distribute the Corrected precip
7. If were at the start of new storm, distribute storm total
8. If its cold enough calculate the percent snow and snow density everytimestep (in out case hours)

## NASDE Model Marks2017

The code in the source for the model is fairly clear, please read it to understand
in greater detail.

### Highlights:

1. New snow density and percent snow is estimated from a linearized table.
2. The new snow density is then compacted using metamorphic and overburden processes as they are described in the density paper.
3. It is also compacted from liquid water using a ratio of percent snow.
