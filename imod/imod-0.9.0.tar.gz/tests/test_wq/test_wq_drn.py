import pathlib

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from imod.wq import Drainage


@pytest.fixture(scope="function")
def drainage():
    layer = np.arange(1, 4)
    y = np.arange(4.5, 0.0, -1.0)
    x = np.arange(0.5, 5.0, 1.0)
    elevation = xr.DataArray(
        np.full((3, 5, 5), 1.0),
        coords={"layer": layer, "y": y, "x": x, "dx": 1.0, "dy": -1.0},
        dims=("layer", "y", "x"),
    )
    conductance = elevation.copy()

    drn = Drainage(elevation=elevation, conductance=conductance)
    return drn


def test_render(drainage):
    drn = drainage
    directory = pathlib.Path(".")

    compare = """
    elevation_p?_s1_l1 = elevation_l1.idf
    elevation_p?_s1_l2 = elevation_l2.idf
    elevation_p?_s1_l3 = elevation_l3.idf
    cond_p?_s1_l1 = conductance_l1.idf
    cond_p?_s1_l2 = conductance_l2.idf
    cond_p?_s1_l3 = conductance_l3.idf"""

    assert drn._render(directory, globaltimes=["?"], system_index=1) == compare


def test_render_with_time(drainage):
    drn = drainage.copy()
    directory = pathlib.Path(".")
    elev = drn["elevation"]
    datetimes = pd.date_range("2000-01-01", "2000-01-02")

    elev_transient = xr.concat(
        [elev.assign_coords(time=t) for t in datetimes], dim="time"
    )
    drn["elevation"] = elev_transient

    compare = """
    elevation_p1_s1_l1 = elevation_20000101000000_l1.idf
    elevation_p1_s1_l2 = elevation_20000101000000_l2.idf
    elevation_p1_s1_l3 = elevation_20000101000000_l3.idf
    elevation_p2_s1_l1 = elevation_20000102000000_l1.idf
    elevation_p2_s1_l2 = elevation_20000102000000_l2.idf
    elevation_p2_s1_l3 = elevation_20000102000000_l3.idf
    cond_p?_s1_l1 = conductance_l1.idf
    cond_p?_s1_l2 = conductance_l2.idf
    cond_p?_s1_l3 = conductance_l3.idf"""

    assert drn._render(directory, globaltimes=datetimes, system_index=1) == compare


def test_render_with_timemap__elevation(drainage):
    drn = drainage
    directory = pathlib.Path(".")
    elev = drn["elevation"]
    datetimes = pd.date_range("2000-01-01", "2000-01-03")

    elev_transient = xr.concat(
        [elev.assign_coords(time=t) for t in datetimes[:-1]], dim="time"
    )
    drn["elevation"] = elev_transient
    timemap = {datetimes[-1]: datetimes[0]}
    drn.add_timemap(elevation=timemap)

    compare = """
    elevation_p1_s1_l1 = elevation_20000101000000_l1.idf
    elevation_p1_s1_l2 = elevation_20000101000000_l2.idf
    elevation_p1_s1_l3 = elevation_20000101000000_l3.idf
    elevation_p2_s1_l1 = elevation_20000102000000_l1.idf
    elevation_p2_s1_l2 = elevation_20000102000000_l2.idf
    elevation_p2_s1_l3 = elevation_20000102000000_l3.idf
    elevation_p3_s1_l1 = elevation_20000101000000_l1.idf
    elevation_p3_s1_l2 = elevation_20000101000000_l2.idf
    elevation_p3_s1_l3 = elevation_20000101000000_l3.idf
    cond_p?_s1_l1 = conductance_l1.idf
    cond_p?_s1_l2 = conductance_l2.idf
    cond_p?_s1_l3 = conductance_l3.idf"""

    actual = drn._render(directory, globaltimes=datetimes, system_index=1)
    assert actual == compare

    # Conductance does not depend on time, therefore cannot have a timemap
    with pytest.raises(ValueError):
        drn.add_timemap(conductance=timemap)


@pytest.mark.parametrize("varname", ["conductance", "elevation"])
def test_render__timemap(drainage, varname):
    drn = drainage
    directory = pathlib.Path(".")
    da = drn[varname]
    datetimes = pd.date_range("2000-01-01", "2000-01-03")
    da_transient = xr.concat(
        [da.assign_coords(time=t) for t in datetimes[:-1]], dim="time"
    )
    drn[varname] = da_transient

    timemap = {datetimes[-1]: datetimes[0]}
    drn.add_timemap(**{varname: timemap})
    actual = drn._render(directory, globaltimes=datetimes, system_index=1)
