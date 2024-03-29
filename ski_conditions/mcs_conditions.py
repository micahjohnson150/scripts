"""
Script plotting snotels. Highlights
rain on snow and colors with density
"""
import argparse
import dateparser
import matplotlib.pyplot as plt
from matplotlib.cm import jet
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase
from metloom.pointdata import SnotelPointData, CDECPointData
from enum import Enum


class Stations(Enum):
    CSSL = "428:CA:SNTL", "CSSL", SnotelPointData
    MCS = "637:ID:SNTL", "Mores Creek Summit", SnotelPointData
    BNR = "312:ID:SNTL", "Banner Summit", SnotelPointData
    TUM = 'TUM', "Tuolumne Meadows", CDECPointData
    GIN = 'GIN', "Gin Flat", CDECPointData
    KIB = 'KIB', "Lower Kibbie", CDECPointData
    WHW = 'WHW', "White Wolf", CDECPointData

    @property
    def name(self):
        return self.value[1]
    @property
    def code(self):
        return self.value[0]
    @property
    def network_class(self):
        return self.value[2]
    @classmethod
    def from_name(cls, name):
        result = None
        for v in cls:
            if v.name == name:
                result = v
                break

        return result

    @classmethod
    def from_code(cls, code):
        result = None
        for v in cls:
            if v.code == code:
                result = v
                break

        return result


def plot_station(df, depth_name='SNOWDEPTH'):
    # Plot the snow depth
    df = df.reset_index().set_index('datetime')
    fig, ax = plt.subplots(1)

    if depth_name in df.columns:
        df[depth_name] = df[depth_name].mul(2.54)  # inches to cm
        ax = df[depth_name].plot(ax=ax, color='black')

        df['Density'] = df['SWE'].mul(25.4) / df[depth_name].div(100)
        ax.set_ylabel('Snow Depth [CM]')

        # Plot the density under it.
        normalize = Normalize(vmin=0, vmax=500)
        # loop and fill
        for idx in range(len(df.index[:-1])):
            d = [df[depth_name].iloc[idx], df[depth_name].iloc[idx + 1]]
            dates = [df.index[idx], df.index[idx + 1]]
            ax.fill_between(dates, d, color=jet(normalize(df['Density'].iloc[idx])))

        cbax = fig.add_axes([0.90, 0.11, 0.05, 0.77])
        cb = ColorbarBase(cbax, cmap=jet, norm=normalize, orientation='vertical')
        cb.set_label("Mean Daily Density [kg/m^3]", rotation=270, labelpad=20)

    else:
        depth_name = 'SWE'
        df[depth_name] = df[depth_name].mul(25.4)
        ax = df[depth_name].plot(ax=ax, color='black')
        ax.set_ylabel('SWE [mm]')

    # Plot rain on snow events
    y2 = ax.get_ylim()[1]
    ind = (df['AIR TEMP'] > 35) & (df['PRECIPITATION'] > 0.2) & (df['SWE'] > 2)
    delta = df.index[1] - df.index[0]

    ax.fill_between(df.index, df[depth_name] + 3, y2*1.1, facecolor="lightskyblue", hatch="..", edgecolor="k",
                    linewidth=0.0, where=ind, interpolate=False)
    ax.set_ylim(0, y2)
    return ax


def main():
    parser = argparse.ArgumentParser(description='Plot data at Snotel')
    parser.add_argument('station', metavar='station', type=str,
                        help='station to look at', default='Mores Creek Summit')
    parser.add_argument('--start_date', type=str, default='3 weeks ago',
                        help='Start date for dateparser')
    parser.add_argument('--end_date', type=str, default='yesterday',
                        help='End date for dateparser')
    args = parser.parse_args()
    stn = Stations.from_name(args.station)
    Point_Class = stn.network_class

    if stn is not None:
        station_point = Point_Class(stn.code, stn.name)
    else:
        station_point = Point_Class(args.station, args.station)

    variables = [station_point.ALLOWED_VARIABLES.SWE, station_point.ALLOWED_VARIABLES.PRECIPITATION,
                 station_point.ALLOWED_VARIABLES.TEMP, station_point.ALLOWED_VARIABLES.SNOWDEPTH]

    start = dateparser.parse(args.start_date).date()
    end = dateparser.parse(args.end_date).date()
    print(f"Pulling data for {station_point.name} between {start} to {end}")
    df = station_point.get_daily_data(start, end, variables)

    ax = plot_station(df)
    ax.set_title(f"{station_point.name.title()} ({station_point.metadata.z} ft)")
    plt.show()



if __name__ == '__main__':
    main()
