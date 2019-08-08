import pandas as pd
import matplotlib.pyplot as plt

f_ernesto = "./Tollgate_SWI_timeseries_from_ernesto.csv"
f_swiflow = "swi_from_swiflow.csv"
f_swiflow_basin = "./basin_catchments.csv"

df_ernesto = pd.read_csv(f_ernesto, names=["datetime","1","3","5","7","9"],
                         header=2, parse_dates=[0])
df_ernesto.set_index("datetime", inplace=True)

df = pd.read_csv(f_swiflow, header=0, parse_dates=[0])
df.set_index("datetime", inplace=True)

# Parse the area from enerestos file
with open(f_ernesto, 'r') as fp:
    lines = fp.readlines()
    fp.close()

area_line = lines[1]
ids = [s.strip() for s in lines[0].split(',')]

for i,s in enumerate(area_line.split(",")):
    if i != 0:
        df_ernesto[ids[i]] = df_ernesto[ids[i]] / float(s)

# just compare the totals
df_ernesto["total"] = df_ernesto.sum(axis=1)
df["total"] = df.sum(axis=1)
diff = df['total'] - df_ernesto['total']
# print(diff)
# print("MEAN = {}".format(diff.mean()))
# print("Min = {}".format(diff.min()))
# print("Max = {}".format(diff.max()))
# print("STD = {}".format(diff.std()))

plt.plot(df.index, df['total'], label="Produced in SWIFlow")
plt.plot(df_ernesto.index, df_ernesto['total'], label="Produced from Eneresto")
plt.legend()
plt.title("Prep_swi tool VS with E.Tujillo swi aggregation script")
plt.savefig("swi_comparison.png")
plt.show()
