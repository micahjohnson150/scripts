"""
This script makes the markdown file used for the meeting on topo and veg values

usage:
    python make_markdown.py

output:
    veg_k_tau.md
"""

import datetime
from os.path import abspath, expanduser, join
from tabulate import tabulate
import pandas as pd
from basin_setup import __version__, __veg_parameters__


def main():

    ## INPUTS ##
    output = "veg_k_tau.md"
    hist_out = "~/projects/basins/sierras/analysis/topo_veg_type_unique/veg_type_histogram.png"
    pixel_count = "~/projects/basins/sierras/analysis/topo_veg_type_unique/veg_type_count.csv"
    tau_k_table = "https://user-images.githubusercontent.com/7975741/64275442-c5631500-cf02-11e9-9481-a6a1a0e8ac18.png"
    basin_setup_table = __veg_parameters__


    ################################### WORK ###################################
    hist_out = abspath(expanduser(hist_out))
    pixel_count = abspath(expanduser(pixel_count))
    basin_setup_table = abspath(expanduser(basin_setup_table))
    sections = []

    # Grab the date to tag the document
    today = datetime.datetime.today().date().isoformat()

    ################################ background ################################
    intro =\
    ["# Evaluating the Vegetation Radiative Parameters",
    'The following document generated for discussing and evaluating the ',
    'vegetation values used in the AWSM modeling system.',
    '',
    '* Date generated: {}',
    '* Basin Setup Version: {}',
    '* Vegetation Source: Landfire',
    '* Prepared by: Micah Johnson'
    ]

    intro = make_doc_str(intro).format(today,__version__)
    sections = add_section(sections, intro)

    ############################### Application ################################

    application = [
    '## Application',
    'To adjust the solar radiation for vegetation effects, the AWSM modeling ',
    'system relies on values name Tau and K. These values are used in SMRF to ',
    'represent vegetation optical transmissivity (Tau) and vegetation ',
    'extinction coefficient (K). They are used to adjusts the cloud corrected',
    ' solar radiation for vegetation effects, following the methods developed',
    'by Link and Marks (1999) The direct beam radiation is corrected by:',
    '',
    '        R_b = S_b * exp( -K h / cos( theta ))',

    'where S_b is the above canopy direct radiation, K is the extinction '
    'coefficient, h is the canopy height, theta is the solar zenith angle,'
    'and R_b is the canopy adjusted direct radiation. Adjusting the diffuse ',
    'radiation is performed by:',
    '',
    '        R_d = tau * R_d',
    ' Read More at [SMRF:Solar on Read the Docs](https://smrf.readthedocs.io/en/latest/smrf.distribute.html#module-smrf.distribute.solar).',
    '',
    'SMRF also utilizes this information in generating the longwave radiation',
    'depending on the model selected. To view documentation on the models in ',
    'detail visit [SMRF:thermal on Read the Docs](https://smrf.readthedocs.io/en/latest/smrf.distribute.html#module-smrf.distribute.thermal)',
    ''
    'The vegetation values are brought into the modeling system through basin_setup',
    'through the topo.nc file provided to the modeling system as an input.'
    'Attached to the end of this document is a table of landfire vegetation'
    ' types and how basin_setup interprets them into vegetation Tau and K '
    'values. These are based qualitatively on table below. **NOTE Mu in the',
    'table is K in the modeling system**'
    '\n\n![Veg Tau and K table]({} "Table for Vegetation K and Tau")'.format(tau_k_table),
     '\n[Source: Link & Marks 1999](https://doi.org/10.1002/(SICI)1099-1085(199910)13:14/15%3C2439::AID-HYP866%3E3.0.CO;2-1)',

    ]

    application = make_doc_str(application).format(__version__)

    # Add in a table of basin_setup veg tau and K
    columns = ['tau','k','EVT_PHYS','EVT_CLASS']
    veg_data = pd.read_csv(__veg_parameters__, index_col=[0])
    veg_data = veg_data[columns]
    table = tabulate(veg_data, tablefmt="pipe", headers="keys")
    sections = add_section(sections, application)

    ################################# Impact ###################################
    impact =\
    ['## Impact',
     "Below is a histogram of pixels at the vegetation value for each basin.",
     '\n![Veg Type Hist]({} "Histogram of veg types")'.format(hist_out),
     'Below is a table all veg values that impact more than 1 % of the entire',
     'modeled domain.  of the pixels of each basin with the a specific '
     'vegetation value (far left). The percent coverage is the total coverage '
     'of the combined modeling domain.'
     ]

    # Add the table of veg values and their percent coverage
    print("Opening the veg pixel count file...")
    count = pd.read_csv(pixel_count, index_col=[0])

    # grab only veg types great the 1%
    ind = count['percent coverage'] > 1
    table = tabulate(count[ind], tablefmt="pipe", headers="keys")

    # Add the table and the doc str to the document
    impact = make_doc_str(impact)
    sections = add_section(sections, impact)
    sections = add_section(sections, table)

    ################################# Notes ###################################
    # notes =\
    # ['## Notes on Value Selection',
    # 'Selecting Tau and K values is a qualitatively process with minor guiding ',
    # 'principles.',
    # '1. Most shrub dominated areas are given 1 and 0',
    # '2. Consider '
    #
    # ]
    # appendix = make_doc_str(notes)
    # sections = add_section(sections, notes)

    ################################# Appendix ###################################
    appendix =\
    ['# Appendix',
    '## Vegetation K and Tau Interpretation Table'
    ]
    appendix = make_doc_str(appendix)
    sections = add_section(sections, appendix)
    table = tabulate(veg_data, tablefmt="pipe", headers="keys")
    sections = add_section(sections, table)

    ################################# FInal write ###############################

    # Write out the file
    md_str = ""
    with open(output,'w+') as fp:
        # Add all the sections to the string
        for s in sections:
            md_str += s

        # Write out the string of the whole document
        fp.write(md_str)
        fp.close()


def make_doc_str(lines_list):

    info = "\n".join(lines_list)
    info += "\n"
    return info

def add_section(sections, new):
    new+="\n"
    sections.append(new)
    return sections

if __name__ == "__main__":
    main()
