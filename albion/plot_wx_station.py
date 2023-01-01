from datetime import datetime

import numpy as np
from metloom.pointdata import MesowestPointData
import matplotlib.pyplot as plt 
import click 


@click.command()
@click.argument("variable", type=click.Choice([v.value for v in MesowestPointData.ALLOWED_VARIABLES]))
def main(variable):
    pnt = MesowestPointData("ITD45", "CONNOR SUMMIT")

    for i, yr in enumerate([2018, 2019, 2021]):
        print(yr)
        df = pnt.get_daily_data(
            datetime(yr, 1, 1), datetime(yr, 12, 30),
            [pnt.ALLOWED_VARIABLES.TEMP]
        )

        df = df.reset_index()
        df = df.resample('D', on='datetime').mean()
        print(df)

        #df = df.resample('D')
        tz = df.index[0].tzinfo
        jan1 = datetime(yr, 1, 1, 0, 0, 0, tzinfo=tz)

        df['AIR TEMP'] = df['AIR TEMP'] * (9/5) + 32
        if i == 0:
            mean_air_temp = df['AIR TEMP']
        else:
            mean_air_temp += df['AIR TEMP'].values
            mean_air_temp/=2

        plt.plot((df.index - jan1).days, df['AIR TEMP'], alpha=0.25, label=yr)
        plt.legend()

    plt.plot((df.index - jan1).days, mean_air_temp, label='mean')
    print(mean_air_temp.max())
    print(mean_air_temp.min())

    plt.show()


if __name__ == '__main__':
    main()
