import pandas as pd
from collections import OrderedDict


def convert_mass(mass_series, cutter_vol, tare):
    """
    Converts pandas series of mass in gramsto a density
    given a density cutter volume in cubic centimeters and a tare
    weight.

    Args:
        mass_series: Pandas series of mass
        cutter_vol:  Kelly cutter volume
        tare: Weight to subtract from masses to account for cutter
    Returns:
        result: Pandas Series of density
    """
    mass = (mass_series - tare) / 1000  # snow g -> kg
    vol = cutter_vol * 1e-6  # CC -> M^3
    result = mass / vol
    return result


def convert_depth_datum(depth_series, HS):
    """
    Converts a snow surface datum to a ground datum
    Args:
        depth_series: Positions in the snow counting positively from the surface downward
        HS: Total snow height

    Returns:
        result: Vertical positions in the snow using the ground as zero.
    """
    result = depth_series * -1 + HS
    return result


def write_snowex_like_file(df, header, out_file):
    """
    Writes results to a file with Snowex like format

    Args:
        df: dataframe to write to file
        header: Header info prepend to file
    """
    # Invert the depth so we use a ground based datum

    with open(out_file, 'w+') as fp:
        for k, v in header.items():
            fp.write(f"# {k.title()}, {v}\n")
    df.to_csv(out_file, mode='a', float_format='%0.0f', index=False)


def pit1(cols):
    f = 'mass_pit_1.csv'
    df = pd.read_csv(f, header=3)
    df['Density A (kg/m3)'] = convert_mass(df['Mass A (g)'], 250, 161.5)
    df['Density B (kg/m3)'] = convert_mass(df['Mass B (g)'], 250, 161.5)
    df['Top (cm)'] = convert_depth_datum(df['Top (cm)'], 200)
    df['Bottom (cm)'] = convert_depth_datum(df['Bottom (cm)'], 200)

    # Output data
    header = OrderedDict()
    header["location"] = "Mores Creek Summit Idaho"
    header["Date/Local Time"] = "2023-01-19T12:10"
    header["Aspect"] = "NE"
    header["Elevation"] = "2172m"
    header["UTM Zone"] = "11U"
    header["Easting"] = "595338"
    header["Northing"] = "5532952"
    header["Cutter"] = "250CC"
    header["Observers"] = "Micah Johnson, Mark Robertson, Micah Sandusky"
    out_file = 'MCS_20230119_pit1_density_v01.csv'
    write_snowex_like_file(df[cols], header, out_file)


def pit2(cols):
    f = 'mass_pit_2.csv'
    df = pd.read_csv(f, header=3)
    df['Density A (kg/m3)'] = convert_mass(df['Mass A (g)'], 250, 161.5)
    df['Density B (kg/m3)'] = convert_mass(df['Mass B (g)'], 250, 161.5)
    df['Top (cm)'] = convert_depth_datum(df['Top (cm)'], 200)
    df['Bottom (cm)'] = convert_depth_datum(df['Bottom (cm)'], 200)

    # Output data
    header = OrderedDict()
    header["location"] = "Mores Creek Summit Idaho"
    header["Date/Local Time"] = "2023-01-19T14:15"
    header["Aspect"] = "SW"
    header["Elevation"] = "2389m"
    header["UTM Zone"] = "11U"
    header["Easting"] = "605723"
    header["Northing"] = "4867785"
    header["Cutter"] = "250CC"
    header["Observers"] = "Micah Johnson, Mark Robertson"
    out_file = 'MCS_20230119_pit2_density_v01.csv'
    write_snowex_like_file(df[cols], header, out_file)


def main():
    """
    Convert the masses recorded for the pits to densities
    """
    cols = ['Top (cm)', 'Bottom (cm)', 'Density A (kg/m3)', 'Density B (kg/m3)']
    pit1(cols)
    pit2(cols)


if __name__ == "__main__":
    main()
