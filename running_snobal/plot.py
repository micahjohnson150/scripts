"""
Script for plotting snobal text file results. Format (L->R) is

    time_s       =   elapsed time since start of model run (hours)
    R_n          =   net allwave rad (W/m^2)
    H            =   sensible heat transfer (W/m^2)
    L_v_E        =   latent heat exchange (W/m^2)
    G            =   snow/soil heat exchange (W/m^2)
    M            =   advected heat from precip. (W/m^2)
    delta_Q      =   sum of e.b. terms for snowcover (W/m^2)
    G_0          =   heat exchange between snow layers (W/m^2)
    delta_Q_0    =   sum of e.b. terms for surface layer (W/m^2)
    cc_s_0       =   surface layer cold content (J/m^2)
    cc_s_l       =   lower layer cold content (J/m^2)
    cc_s         =   snowcover cold content (J/m^2)
    E_s          =   evaporation (kg/m^2)
    melt         =   melt (kg/m^2)
    ro_predict   =   predicted runoff (kg, or mm/m^2)
    [ro_error]   =   runoff error (kg, or mm/m^2)
    z_s_0        =   predicted depth of surface layer (m)
    z_s_l        =   predicted   "   of lower layer (m)
    z_s          =   predicted   "   of snowcover (m)
    rho          =   predicted average snow density (kg/m^3)
    m_s_0        =   predicted specific mass of surface layer (kg/m^2)
    m_s_l        =   predicted    "      "   of lower layer (kg/m^2)
    m_s          =   predicted    "      "   of snowcover (kg/m^2)
    h2o          =   predicted liquid H2O in snowcover (kg/m^2)
    T_s_0        =   predicted temperature of surface layer (C)
    T_s_l        =   predicted      "      of lower layer (C)
    T_s          =   predicted average temp of snowcover (C)


"""
import matplotlib.pyplot as plt
import pandas as pd


# Column names as brought in from IPW
columns =   ['time_s', 'R_n', 'H', 'L_v_E', 'G', 'M', 'delta_Q', 'G_0',
             'delta_Q_0', 'cc_s_0', 'cc_s_l', 'cc_s', 'E_s', 'melt',
             'ro_predict', 'z_s_0', 'z_s_l', 'z_s', 'rho', 'm_s_0', 'm_s_l',
             'm_s', 'h2o', 'T_s_0', 'T_s_l', 'T_s ']

# Read in the output data and assign the columns names from above
df  = pd.read_csv("snobal.txt", delimiter=" ", names=columns)

# Index by the time in whatever timestep we used
df = df.set_index("time_s")

# Plot snow depth for the first year.
df['z_s'].plot()
plt.show()
