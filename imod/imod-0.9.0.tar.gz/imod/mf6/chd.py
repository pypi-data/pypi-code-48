from imod.mf6.pkgbase import BoundaryCondition


class ConstantHead(BoundaryCondition):
    """
    Constant-Head package. Any number of CHD Packages can be specified for a
    single groundwater flow model; however, an error will occur if a CHD Package
    attempts to make a GWF cell a constant-head cell when that cell has already
    been designated as a constant-head cell either within the present CHD
    Package or within another CHD Package. In previous MODFLOW versions, it was
    not possible to convert a constant-head cell to an active cell. Once a cell
    was designated as a constant-head cell, it remained a constant-head cell
    until the end of the end of the simulation. In MODFLOW 6 a constant-head
    cell will become active again if it is not included as a constant-head cell
    in subsequent stress periods. Previous MODFLOW versions allowed
    specification of SHEAD and EHEAD, which were the starting and ending
    prescribed heads for a stress period. Linear interpolation was used to
    calculate a value for each time step. In MODFLOW 6 only a single head value
    can be specified for any constant-head cell in any stress period. The
    time-series functionality must be used in order to interpolate values to
    individual time steps.

    Parameters
    ----------
    head: array of floats (xr.DataArray)
        Is the head at the boundary.
    print_input: ({True, False}, optional)
        keyword to indicate that the list of constant head information will
        be written to the listing file immediately after it is read. Default is
        False.
    print_flows: ({True, False}, optional)
        Indicates that the list of constant head flow rates will be printed to
        the listing file for every stress period time step in which “BUDGET
        PRINT”is specified in Output Control. If there is no Output Control
        option and PRINT FLOWS is specified, then flow rates are printed for the
        last time step of each stress period.
        Default is False.
    save_flows: ({True, False}, optional)
        Indicates that constant head flow terms will be written to the file
        specified with “BUDGET FILEOUT” in Output Control. Default is False.
    observations: [Not yet supported.]
        Default is None.
    """

    __slots__ = ("head", "print_input", "print_flows", "save_flows", "observations")
    _pkg_id = "chd"
    _binary_data = ("head",)
    _template = BoundaryCondition._initialize_template(_pkg_id)

    def __init__(
        self,
        head,
        print_input=False,
        print_flows=False,
        save_flows=False,
        observations=None,
    ):
        super(__class__, self).__init__()
        self["head"] = head
        self["print_input"] = print_input
        self["print_flows"] = print_flows
        self["save_flows"] = save_flows
        self["observations"] = observations
