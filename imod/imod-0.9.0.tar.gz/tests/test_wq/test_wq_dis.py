import textwrap

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from imod.wq import TimeDiscretization


@pytest.fixture(scope="module")
def discret():
    datetimes = pd.date_range("2000-01-01", "2000-01-05")
    timestep_duration = xr.DataArray(
        np.full(5, 1.0), coords={"time": datetimes}, dims=("time",)
    )

    dis = TimeDiscretization(
        timestep_duration=timestep_duration,
        n_timesteps=xr.full_like(timestep_duration, 1, dtype=np.int),
        transient=xr.full_like(timestep_duration, True),
        timestep_multiplier=xr.full_like(timestep_duration, 1.0),
        max_n_transport_timestep=xr.full_like(timestep_duration, 10, dtype=np.int),
        transport_timestep_multiplier=xr.full_like(timestep_duration, 1.0),
        transport_initial_timestep=0,
    )
    return dis


def test_render_dis(discret):
    dis = discret
    globaltimes = dis.time.values

    compare = """
    nper = 5
    perlen_p1 = 1.0
    perlen_p2 = 1.0
    perlen_p3 = 1.0
    perlen_p4 = 1.0
    perlen_p5 = 1.0
    nstp_p1 = 1
    nstp_p2 = 1
    nstp_p3 = 1
    nstp_p4 = 1
    nstp_p5 = 1
    sstr_p1 = tr
    sstr_p2 = tr
    sstr_p3 = tr
    sstr_p4 = tr
    sstr_p5 = tr
    tsmult_p1 = 1.0
    tsmult_p2 = 1.0
    tsmult_p3 = 1.0
    tsmult_p4 = 1.0
    tsmult_p5 = 1.0"""

    assert dis._render(globaltimes) == compare


def test_render_dis__notime(discret):
    dis = discret.isel(time=0).drop("time")
    globaltimes = ["?"]

    compare = """
    nper = 1
    perlen_p? = 1.0
    nstp_p? = 1
    sstr_p? = tr
    tsmult_p? = 1.0"""

    assert dis._render(globaltimes) == compare


def test_render_btn(discret):
    dis = discret.isel(time=0).drop("time")
    globaltimes = ["?"]

    compare = """
    tsmult_p? = 1.0
    dt0_p? = 0
    ttsmult_p? = 1.0
    mxstrn_p? = 10"""

    assert dis._render_btn(globaltimes) == compare
