import imod
import numpy as np
import pandas as pd
import xarray as xr

# Discretization
nrow = 1
ncol = 80
nlay = 40

dz = 1.0  # 0.0125
dx = 1.0  # 0.0125
dy = -dx

# setup ibound
bnd = xr.DataArray(
    data=np.full((nlay, nrow, ncol), 1.0),
    coords={
        "y": [0.5],
        "x": np.arange(0.5 * dx, dx * ncol, dx),
        "layer": np.arange(1, 1 + nlay),
        "dx": dx,
        "dy": dy,
    },
    dims=("layer", "y", "x"),
)

bnd.plot()

# Defining constant heads
bnd[31, :, 0] = -1
bnd.plot(y="layer", yincrease=False)

# Defining tops and bottoms
top1D = xr.DataArray(
    np.arange(nlay * dz, 0.0, -dz), {"layer": np.arange(1, nlay + 1)}, ("layer")
)

bot = top1D - dz
top = nlay * dz

# Define WEL data
weldata = pd.DataFrame()
weldata["x"] = np.full(1, 0.5 * dx)
weldata["y"] = np.full(1, 0.5)
weldata["q"] = 0.28512  # positive, so it's an injection well

# Define icbund
icbund = xr.full_like(bnd, 1)

# Define starting concentrations
sconc = xr.DataArray(
    data=np.full((nlay, nrow, ncol), 0.0),
    coords={
        "y": [0.5],
        "x": np.arange(0.5 * dx, dx * ncol, dx),
        "layer": np.arange(1, nlay + 1),
    },
    dims=("layer", "y", "x"),
)

sconc[:, :, 41:80] = 35.0
sconc.plot(y="layer", yincrease=False)

# Finally, we build the model
m = imod.wq.SeawatModel("VerticalInterface")
m["bas"] = imod.wq.BasicFlow(ibound=bnd, top=top, bottom=bot, starting_head=0.0)
m["lpf"] = imod.wq.LayerPropertyFlow(
    k_horizontal=86.4, k_vertical=86.4, specific_storage=0.0
)
m["btn"] = imod.wq.BasicTransport(
    icbund=icbund, starting_concentration=sconc, porosity=0.1
)
m["adv"] = imod.wq.AdvectionTVD(courant=1.0)
m["dsp"] = imod.wq.Dispersion(longitudinal=0.0, diffusion_coefficient=0.0)
m["vdf"] = imod.wq.VariableDensityFlow(density_concentration_slope=0.71)
m["wel"] = imod.wq.Well(
    id_name="wel", x=weldata["x"], y=weldata["y"], rate=weldata["q"]
)
m["pcg"] = imod.wq.PreconditionedConjugateGradientSolver(
    max_iter=150, inner_iter=30, hclose=0.0001, rclose=0.1, relax=0.98, damp=1.0
)
m["gcg"] = imod.wq.GeneralizedConjugateGradientSolver(
    max_iter=150,
    inner_iter=30,
    cclose=1.0e-6,
    preconditioner="mic",
    lump_dispersion=True,
)
m["oc"] = imod.wq.OutputControl(save_head_idf=True, save_concentration_idf=True)
m.time_discretization(times=["2000-01-01", "2000-01-02"])

# Now we write the model, including runfile:
m.write()


# You can run the model using the comand prompt and the iMOD SEAWAT executable

# Results

# head = imod.idf.open("VerticalInterface/results/head/*.idf")
# head.plot(yincrease=False)
# conc = imod.idf.open("VerticalInterface/results/conc/*.idf")
# conc.plot(levels=range(0, 35, 5), yincrease=False)
