"""
Generate a veg_style.qml that we can randomize the veg values assigned in a
repeatable way. This way each veg class has a unique color. The info here in the
hdr and footer variables was copied from a style that was generated from QGIS
12-19-2019 for QGIS V2.18

usage:
    python make_veg_style.py

output:
    a style file written to veg_style.qml

"""
import pandas as pd
import numpy as np
import random as rd

print("Creating a new colormap for QGIS based on the veg values found in the topos")
output = "./gis/veg_style.qml"
veg_values = './veg_map_sierras.csv'
alpha = 50

# Upper portion of the style file right up to the color ramp
hdr = """
<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.18.28" minimumScale="inf" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <pipe>
    <rasterrenderer opacity="0.490196" alphaBand="-1" classificationMax="4000" classificationMinMaxOrigin="User" band="1" classificationMin="3000" type="singlebandpseudocolor">
      <rasterTransparency/>
      <rastershader>
        <colorrampshader colorRampType="EXACT" clip="0">
"""

# lower portion of the style file right after the color ramp
footer = """
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
"""

color_entry = '          <item alpha="{0}" value="{1}" label="{1}" color="{2}"/>\n'



# Grab the veg values for all the modeling domains in the sierras
df = pd.read_csv(veg_values)

r = rd.Random()

with open(output,'w+') as fp:

    # Write the upper portion of the file
    fp.write(hdr)

    # iterate through all the veg values in the sierras
    for i,row in df.iterrows():
        rgb = []

        # form a random 3 digit rgb
        for zz in range(3):
            r.seed(i+zz)
            rgb.append(r.randint(0, 255))

        # Form the hex value
        hex_v = '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])

        # Grab the veg value
        value = row['VALUE']

        fp.write(color_entry.format(alpha, value, hex_v))

    print("Added {} discrete colors to represent veg type.".format(i))

    # Write the rest of the file
    fp.write(footer)
    fp.close()
print("Complete!")
