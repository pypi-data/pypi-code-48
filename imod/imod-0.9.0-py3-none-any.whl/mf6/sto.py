import numpy as np

from imod.mf6.pkgbase import Package


class Storage(Package):
    """
    Storage Package.
    If the STO Package is not included for a model, then storage changes will
    not be calculated, and thus, the model will be steady state. Only one STO
    Package can be specified for a GWF model.
    The option to use a keyword to indicate that the SS array is read as storage
    coefficient rather than specific storage has not been implemented yet.
    https://water.usgs.gov/water-resources/software/MODFLOW-6/mf6io_6.0.4.pdf#page=57

    Parameters
    ----------
    specific_storage: array of floats (xr.DataArray)
        Is specific storage. Specific storage values must be greater than
        or equal to 0. (ss)
    specific_yield: array of floats (xr.DataArray)
        Is specific yield. Specific yield values must be greater than or
        equal to 0. Specific yield does not have to be specified if there are no
        convertible cells (convertible=0 in every cell). (sy)
    convertible: array of int (xr.DataArray)
        Is a flag for each cell that specifies whether or not a cell is
        convertible for the storage calculation. 0 indicates confined storage is
        used. >0 indicates confined storage is used when head is above cell top
        and a mixed formulation of unconfined and confined storage is used when
        head is below cell top. (iconvert)
    transient: ({True, False})
        Boolean to indicate if the model is transient or steady-state.
    """

    __slots__ = ("specific_storage", "specific_yield", "convertible", "transient")
    _pkg_id = "sto"
    _template = Package._initialize_template(_pkg_id)

    def __init__(self, specific_storage, specific_yield, transient, convertible):
        super(__class__, self).__init__()
        self["specific_storage"] = specific_storage
        self["specific_yield"] = specific_yield
        self["convertible"] = convertible
        self["transient"] = transient

    def render(self, directory, pkgname, globaltimes):
        d = {}
        for varname in ["specific_storage", "specific_yield", "convertible"]:
            d[varname] = self._compose_values(varname, directory)

        periods = {}
        if "time" in self["transient"]:
            package_times = self["transient"].coords["time"].values
            starts = np.searchsorted(globaltimes, package_times) + 1
            for i, s in enumerate(starts):
                periods[s] = self["transient"].isel(time=i).values[()]
        else:
            periods[1] = self["transient"].values[()]

        d["periods"] = periods

        return self._template.render(d)
