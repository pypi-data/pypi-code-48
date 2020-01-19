import pathlib
import subprocess

import affine
import dask
import numba
import numpy as np
import pandas as pd
import scipy.ndimage
import xarray as xr

# since rasterio is a big dependency that is sometimes hard to install
# and not always required, we made this an optional dependency
try:
    import rasterio
    import rasterio.features
    import rasterio.warp
except ImportError:
    pass

import imod
from imod.prepare import pcg


def round_extent(extent, cellsize):
    """Increases the extent until all sides lie on a coordinate
    divisible by cellsize."""
    xmin, ymin, xmax, ymax = extent
    xmin = np.floor(xmin / cellsize) * cellsize
    ymin = np.floor(ymin / cellsize) * cellsize
    xmax = np.ceil(xmax / cellsize) * cellsize
    ymax = np.ceil(ymax / cellsize) * cellsize
    return xmin, ymin, xmax, ymax


def round_z(z_extent, dz):
    """Increases the extent until all sides lie on a coordinate
    divisible by dz."""
    zmin, zmax = z_extent
    zmin = np.floor(zmin / dz) * dz
    zmax = np.ceil(zmax / dz) * dz
    return zmin, zmax


def _fill_np(data, invalid):
    """Basic nearest neighbour interpolation"""
    # see: https://stackoverflow.com/questions/5551286/filling-gaps-in-a-numpy-array
    ind = scipy.ndimage.distance_transform_edt(
        invalid, return_distances=False, return_indices=True
    )
    return data[tuple(ind)]


def fill(da, invalid=None, by=None):
    """
    Replace the value of invalid ``da`` cells (indicated by ``invalid``)
    using basic nearest neighbour interpolation.

    Parameters
    ----------
    da: xr.DataArray with gaps
        array containing missing value
        if one of the dimensions is layer, it will interpolate one layer at a
        a time (2D interpolation over x and y in case of dims == (by, "y", "x")).

    invalid: xr.DataArray
        a binary array of same shape as ``da``.
        data value are replaced where invalid is True
        If None (default), uses: `invalid = np.isnan(data)`

    Returns
    -------
    xarray.DataArray
        with the same coordinates as the input.
    """

    out = xr.full_like(da, np.nan)
    if invalid is None:
        invalid = np.isnan(da)
    if by:
        for coordvalue in da[by]:
            d = {by: coordvalue}
            out.sel(d)[...] = _fill_np(da.sel(d).values, invalid.sel(d).values)
    else:
        out.values = _fill_np(da.values, invalid.values)

    return out


def laplace_interpolate(
    source, ibound=None, close=0.01, mxiter=5, iter1=50, relax=0.98
):
    """
    Fills gaps in `source` by interpolating from existing values using Laplace
    interpolation.

    Parameters
    ----------
    source : xr.DataArray with dims (y, x)
        Data values to interpolate.
    ibound : xr.DataArray with dims (y, x)
        Precomputed array which marks where to interpolate
    close : float
        Closure criteration of iterative solver. Should be one to two orders
        of magnitude smaller than desired accuracy.
    mxiter : int
        Outer iterations of iterative solver.
    iter1 : int
        Inner iterations of iterative solver. Should not exceed 50.
    relax : float
        Iterative solver relaxation parameter. Should be between 0 and 1.

    Returns
    -------
    interpolated : xr.DataArray with dims (y, x)
        source, with interpolated values where ibound equals 1
    """
    solver = pcg.PreconditionedConjugateGradientSolver(
        close, close * 1.0e6, mxiter, iter1, relax
    )

    if not source.dims == ("y", "x"):
        raise ValueError('source dims must be ("y", "x")')

    if ibound is not None:
        if not ibound.dims == ("y", "x"):
            raise ValueError('ibound dims must be ("y", "x")')
        if not ibound.shape == source.shape:
            raise ValueError("ibound and source must have the same shape")

        # expand dims to make 3d
        source3d = source.expand_dims("layer")
        hnew = source3d.values
        iboundv = ibound.expand_dims("layer").astype(np.int).values
    else:
        # expand dims to make 3d
        source3d = source.expand_dims("layer")
        hnew = source3d.fillna(0.0).values  # Set start interpolated estimate to 0.0
        ibound = np.isnan(source3d)  # Mark nodata values as 1
        # Mark data values as -1, convert to int np.array
        iboundv = ibound.where(ibound).fillna(-1.0).astype(np.int).values

    shape = iboundv.shape
    nlay, nrow, ncol = shape
    nodes = nlay * nrow * ncol
    # Allocate work arrays
    # Not really used now, but might come in handy to implements weights
    cc = cr = cv = np.ones(shape)
    rhs = np.zeros(shape)
    hcof = np.zeros(shape)
    # Solver work arrays
    res = np.zeros(nodes)
    cd = np.zeros(nodes)
    v = np.zeros(nodes)
    ss = np.zeros(nodes)
    p = np.zeros(nodes)

    # Picard iteration
    converged = False
    outer_iteration = 0
    while not converged and outer_iteration < mxiter:
        # Mutates hnew
        converged = solver.solve(
            hnew=hnew,
            cc=cc,
            cr=cr,
            cv=cv,
            ibound=iboundv,
            rhs=rhs,
            hcof=hcof,
            res=res,
            cd=cd,
            v=v,
            ss=ss,
            p=p,
        )
        outer_iteration += 1
    else:
        if not converged:
            raise RuntimeError("Failed to converge")

    return xr.full_like(source, hnew[0])


def rasterize(geodataframe, like, column=None, fill=np.nan, **kwargs):
    """
    Rasterize a geopandas GeoDataFrame onto the given
    xarray coordinates.

    Parameters
    ----------
    geodataframe : geopandas.GeoDataFrame
    column : str, int, float
        column name of geodataframe to burn into raster
    like : xarray.DataArray
        Example DataArray. The rasterized result will match the shape and
        coordinates of this DataArray.
    fill : float, int
        Fill value for nodata areas. Optional, default value is np.nan.
    kwargs : additional keyword arguments for rasterio.features.rasterize.
        See: https://rasterio.readthedocs.io/en/stable/api/rasterio.features.html#rasterio.features.rasterize

    Returns
    -------
    rasterized : xarray.DataArray
        Vector data rasterized. Matches shape and coordinates of ``like``.
    """

    if column is not None:
        shapes = [
            (geom, value)
            for geom, value in zip(geodataframe.geometry, geodataframe[column])
        ]
    else:
        shapes = [geom for geom in geodataframe.geometry]

    # shapes must be an iterable
    try:
        iter(shapes)
    except TypeError:
        shapes = (shapes,)

    raster = rasterio.features.rasterize(
        shapes,
        out_shape=like.shape,
        fill=fill,
        transform=imod.util.transform(like),
        **kwargs,
    )

    return xr.DataArray(raster, like.coords, like.dims)


def _handle_dtype(dtype, nodata):
    # Largely taken from rasterio.dtypes
    # https://github.com/mapbox/rasterio/blob/master/rasterio/dtypes.py
    # TODO: look at licensing of Mapbox license:
    # https://github.com/mapbox/rasterio/blob/master/LICENSE.txt
    # Not supported:
    # GDT_CInt16 = 8, GDT_CInt32 = 9, GDT_CFloat32 = 10, GDT_CFloat64 = 11
    dtype_mapping = {
        "uint8": 1,  # GDT_Byte
        "uint16": 2,  # GDT_Uint16
        "int16": 3,  # GDT_Int16
        "uint32": 4,  # GDT_Uint32
        "int32": 5,  # GDT_Int32
        "float32": 6,  # GDT_Float32
        "float64": 7,  # GDT_Float64
    }
    dtype_ranges = {
        "uint8": (0, 255),
        "uint16": (0, 65535),
        "int16": (-32768, 32767),
        "uint32": (0, 4294967295),
        "int32": (-2147483648, 2147483647),
        "float32": (-3.4028235e38, 3.4028235e38),
        "float64": (-1.7976931348623157e308, 1.7976931348623157e308),
    }

    def format_invalid(str_dtype):
        str_dtypes = dtype_mapping.keys()
        return "Invalid dtype: {0}, must be one of: {1}".format(
            str_dtype, ", ".join(str_dtypes)
        )

    if dtype is np.dtype(np.int64):
        dtype = np.int32

    str_dtype = str(np.dtype(dtype))
    if str_dtype not in dtype_mapping.keys():
        raise ValueError(format_invalid(str_dtype))
    gdal_dtype = dtype_mapping[str_dtype]

    if nodata is None:
        if np.issubdtype(dtype, np.integer):
            # Default to lowest value in case of integers
            nodata = dtype_ranges[str_dtype][0]
        elif np.issubdtype(dtype, np.floating):
            # Default to NaN in case of floats
            nodata = np.nan
    else:
        lower, upper = dtype_ranges[str_dtype]
        if nodata < lower or nodata > upper:
            raise ValueError(f"Nodata value {nodata} is out of bounds for {str_dtype}")

    return gdal_dtype, nodata


def gdal_rasterize(
    path, column, like=None, nodata=None, dtype=None, spatial_reference=None
):
    """
    Use GDAL to rasterize a vector file into an xarray.DataArray.

    Can be significantly more efficient than rasterize. This doesn't load the
    vector data into a GeoDataFrame and loops over the individual shapely
    geometries like rasterio.rasterize does, but loops over the features within
    GDAL instead.

    Parameters
    ----------
    path : str or pathlib.Path
        path to OGR supported vector file (e.g. a shapefile)
    column : str
        column name of column to burn into raster
    like : xr.DataArray, optional
        example of raster
    nodata : int, float; optional
    dtype : numpy.dtype, optional
    spatial_reference : dict, optional
        Optional dict to avoid allocating the like DataArray. Used if template
        is None. Dict has keys "bounds" and "cellsizes", with:

        * bounds = (xmin, xmax, ymin, ymax)
        * cellsizes = (dx, dy)

    Returns
    -------
    rasterized : np.array
    """
    from osgeo import gdal
    from osgeo import ogr

    if isinstance(path, pathlib.Path):
        p = path
        path = str(p)
    else:
        p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No such file: {path}")

    if dtype is None:
        if like is None:
            raise ValueError("If ``like`` is not provided, ``dtype`` has to be given")
        else:
            dtype = like.dtype
    gdal_dtype, nodata = _handle_dtype(dtype, nodata)

    # Exceptions will get raised on anything >= gdal.CE_Failure
    gdal.UseExceptions()

    # An attempt at decent errors
    class GdalErrorHandler:
        def __init__(self):
            self.err_level = gdal.CE_None
            self.err_no = 0
            self.err_msg = ""

        def handler(self, err_level, err_no, err_msg):
            self.err_level = err_level
            self.err_no = err_no
            self.err_msg = err_msg

    error = GdalErrorHandler()
    handler = error.handler
    gdal.PushErrorHandler(handler)

    # Get spatial data from template
    if like is not None:
        dx, xmin, _, dy, _, ymax = imod.util.spatial_reference(like)
        nrow, ncol = like.shape
    else:
        cellsizes = spatial_reference["cellsizes"]
        bounds = spatial_reference["bounds"]
        dx, dy = cellsizes
        if not isinstance(dx, (int, float)) or not isinstance(dy, (int, float)):
            raise ValueError("Cannot rasterize to a non-equidistant grid")
        coords = imod.util._xycoords(bounds, cellsizes)
        xmin, _, _, ymax = bounds
        nrow = coords["y"].size
        ncol = coords["x"].size
        dims = ("y", "x")

    # File will be closed when vector is dereferenced, after return
    vector = ogr.Open(path)
    vector_layer = vector.GetLayer()

    memory_driver = gdal.GetDriverByName("MEM")
    memory_raster = memory_driver.Create("", ncol, nrow, 1, gdal_dtype)
    memory_raster.SetGeoTransform([xmin, dx, 0, ymax, 0, dy])
    memory_band = memory_raster.GetRasterBand(1)
    memory_band.SetNoDataValue(nodata)
    memory_band.Fill(nodata)

    options = [f"ATTRIBUTE={column}"]
    gdal.RasterizeLayer(memory_raster, [1], vector_layer, None, None, [1], options)
    if error.err_level >= gdal.CE_Warning:
        reference_err_msg = (
            "Failed to fetch spatial reference on layer shape to build"
            " transformer, assuming matching coordinate systems."
        )
        if error.err_msg == reference_err_msg:
            pass
        else:
            raise RuntimeError("GDAL error: " + error.err_msg)

    if like is not None:
        rasterized = xr.full_like(like, memory_raster.ReadAsArray(), dtype=dtype)
    else:
        rasterized = xr.DataArray(memory_raster.ReadAsArray(), coords, dims)

    return rasterized


@numba.njit(cache=True)
def _cell_count(src, values, frequencies, nodata, *inds_weights):
    """
    numba compiled function to count the number of src cells occuring in the dst
    cells.

    Parameters
    ----------
    src : np.array
    values : np.array
        work array to store the unique values
    frequencies : np.array
        work array to store the tallied counts
    nodata : int, float
    inds_weights : tuple of np.arrays
        Contains indices of dst, indices of src, and weights.

    Returns
    -------
    tuple of np.arrays

       * row_indices
       * col_indices
       * values
       * frequencies
    """
    jj, blocks_iy, blocks_weights_y, kk, blocks_ix, blocks_weights_x = inds_weights

    # Use list for dynamic allocation, since we don't know number of rows in
    # advance.
    row_indices = []
    col_indices = []
    value_list = []
    count_list = []

    # j, k are indices of dst array
    # block_i contains indices of src array
    # block_w contains weights of src array
    for countj, j in enumerate(jj):
        block_iy = blocks_iy[countj]
        block_wy = blocks_weights_y[countj]
        for countk, k in enumerate(kk):
            block_ix = blocks_ix[countk]
            block_wx = blocks_weights_x[countk]

            # TODO: use weights in frequency count, and area sum?
            # Since src is equidistant, normed weights are easy to calculate.

            # Add the values and weights per cell in multi-dim block
            value_count = 0
            for iy, wy in zip(block_iy, block_wy):
                if iy < 0:
                    break
                for ix, wx in zip(block_ix, block_wx):
                    if ix < 0:
                        break

                    v = src[iy, ix]
                    if v == nodata:  # Skip nodata cells
                        continue
                    # Work on a single destination cell
                    # Count the number of polygon id's occuring in the cell
                    # a new row per id
                    found = False
                    for i in range(value_count):
                        if v == values[i]:
                            frequencies[i] += 1
                            found = True
                            break
                    if not found:
                        values[value_count] = v
                        frequencies[value_count] = 1
                        value_count += 1
                        # Add a new entry
                        row_indices.append(j)
                        col_indices.append(k)

            # Store for output
            value_list.extend(values[:value_count])
            count_list.extend(frequencies[:value_count])

            # reset storage
            values[:value_count] = 0
            frequencies[:value_count] = 0

    # Cast to numpy arrays
    row_i_arr = np.array(row_indices)
    col_i_arr = np.array(col_indices)
    value_arr = np.array(value_list)
    count_arr = np.array(count_list)

    return row_i_arr, col_i_arr, value_arr, count_arr


def _celltable(path, column, resolution, like, rowstart=0, colstart=0):
    """
    Returns a table of cell indices (row, column) with feature ID, and feature
    area within cell. Essentially returns a COO sparse matrix, but with
    duplicate values per cell, since more than one geometry may be present.

    The feature area within the cell is approximated by first rasterizing the
    feature, and then counting the number of occuring cells. This means the
    accuracy of the area depends on the cellsize of the rasterization step.

    Parameters
    ----------
    path : str or pathlib.Path
        path to OGR supported vector file (e.g. a shapefile)
    column : str
        column name of column to burn into raster
    resolution : float
        cellsize at which the rasterization, and determination of area within
        cellsize occurs. Very small values are recommended (e.g. <= 0.5 m).
    like : xarray.DataArray
        Example DataArray of where the cells will be located. Used only for the
        coordinates.

    Returns
    -------
    cell_table : pandas.DataFrame
    """
    _, xmin, xmax, _, ymin, ymax = imod.util.spatial_reference(like)
    dx = resolution
    dy = -dx
    nodata = -1
    spatial_reference = {"bounds": (xmin, xmax, ymin, ymax), "cellsizes": (dx, dy)}

    rasterized = gdal_rasterize(
        path, column, nodata=nodata, dtype=np.int32, spatial_reference=spatial_reference
    )

    dst_coords = [imod.prepare.common._coord(like, dim) for dim in ("y", "x")]
    src_coords = [imod.prepare.common._coord(rasterized, dim) for dim in ("y", "x")]
    # Determine weights for every regrid dimension, and alloc_len,
    # the maximum number of src cells that may end up in a single dst cell
    inds_weights = []
    alloc_len = 1
    for src_x, dst_x in zip(src_coords, dst_coords):
        is_increasing = imod.prepare.common._is_increasing(src_x, dst_x)
        size, i_w = imod.prepare.common._weights_1d(src_x, dst_x, is_increasing)
        for elem in i_w:
            inds_weights.append(elem)
        alloc_len *= size

    # Pre-allocate work arrays
    values = np.full(alloc_len, 0)
    frequencies = np.full(alloc_len, 0)
    rows, cols, values, counts = _cell_count(
        rasterized.values, values, frequencies, nodata, *inds_weights
    )

    df = pd.DataFrame()
    df["row_index"] = rows + rowstart
    df["col_index"] = cols + colstart
    df[column] = values
    df["area"] = counts * (dx * dx)

    return df


def _create_chunks(like, resolution, chunksize):
    """
    Cuts data into chunksize by chunksize.

    Parameters
    ----------
    like : xarray.DataArray
    resolution : float
    chunksize : int

    Returns
    -------
    chunks : list of xr.DataArray
    """

    _, xmin, xmax, _, ymin, ymax = imod.util.spatial_reference(like)
    # Compute how many rows and columns are necessary for fine resolution
    nrow = int((ymax - ymin) / resolution)
    ncol = int((xmax - xmin) / resolution)
    # Find out where to cut
    x_starts = np.arange(0, ncol, chunksize) * resolution + xmin
    y_starts = np.arange(0, nrow, chunksize) * resolution + ymin
    # Searchsorted assumes the arrays are pre-sorted.
    x = np.sort(like.coords["x"].values)
    y = np.sort(like.coords["y"].values)
    # Get the matching indices of like.
    ix_starts = list(np.searchsorted(x, x_starts))
    iy_starts = list(np.searchsorted(y, y_starts))
    # Append None. In python's slice object, None denotes "slice including
    # first/last element"
    ix_ends = ix_starts[1:] + [None]
    iy_ends = iy_starts[1:] + [None]
    # Use xarray to grab the chunks. The chunks have x and y coordinates.
    # These will inform GDAL on which part to rasterize.
    # GDAL will only rasterize within the boundaries of the chunks, so there's
    # no need to clip the shapefile beforehand.
    chunks = []
    rowstarts = []
    colstarts = []
    for j0, j1 in zip(iy_starts, iy_ends):
        for i0, i1 in zip(ix_starts, ix_ends):
            chunks.append(like.isel(y=slice(j0, j1), x=slice(i0, i1)))
            rowstarts.append(j0)
            colstarts.append(i0)
    return chunks, rowstarts, colstarts


def celltable(path, column, resolution, like, chunksize=1e4):
    r"""
    Process area of features by rasterizing in a chunkwise to limit memory
    usage.

    Returns a table of cell indices (row, column) with for example feature ID,
    and feature area within cell. Essentially returns a COO sparse matrix, but
    with duplicate values per cell, since more than one geometry may be present.

    The feature area within the cell is approximated by first rasterizing the
    feature, and then counting the number of occuring cells. This means the
    accuracy of the area depends on the cellsize of the rasterization step.

    A celltable is returned, as a ``pandas.DataFrame``. It has the following
    columns:

    1. ``"row_index"``
    2. ``"col_index"``
    3. the value of the ``column`` argument
    4. ``"area"``

    ``"row_index"`` and ``"col_index"`` are the indices of the like array in
    which the polygon is located. The ``column`` value holds the rasterized
    value of the specified column. ``"area"`` contains the area of the 
    polygon within the cell.

    The most convenient way of using this celltable is by specifying a feature
    ID as ``column``. After creating a celltable, ``pandas.DataFrame.merge()``
    can be used to join additional data on this ID. Refer to the examples.

    Parameters
    ----------
    path : str or pathlib.Path
        path to OGR supported vector file (e.g. a shapefile)
    column : str
        column name of column to burn into raster
    resolution : float
        cellsize at which the rasterization, and determination of area within
        cellsize occurs. Very small values are recommended (e.g. <= 0.5 m).
    like : xarray.DataArray
        Example DataArray of where the cells will be located. Used only for the
        coordinates.
    chunksize : int, optional
        The size of the chunksize. Used for both x and y dimension.

    Returns
    -------
    celltable : pandas.DataFrame

    Examples
    --------
    Assume we have a shapefile called ``waterways.shp`` and information on the
    model discretization is described by a ``like`` DataArray. The feature ID is
    provided by a column in the shapefile called "ID-code". Additionally, this
    shapefile also specifies bed hydraulic resistance (c0). For this specific
    discretization, we wish to calculate a conductance (area divided by
    hydraulic resistance). To do so, we:

    1. create a ``celltable``
    2. join the additional attributes (such as c0)
    3. compute the conductance per feature
    4. sum conductances per cell

    Import the required packages.

    >>> import imod
    >>> import geopandas as gpd

    Generate the celltable.

    >>> celltable = imod.prepare.celltable(
            path="waterways.shp",
            column="ID-code",
            resolution=0.5,
            like=like,
        )

    Load the shapefile with geopandas into a ``GeoDataFrame``.

    >>> gdf = gpd.read_file("waterways.shp)

    Select the relevant columns into a ``pandas.DataFrame`` and merge with the
    celltable.

    >>> df = gdf[["ID-code", "c0"]]
    >>> joined = celltable.merge(gdf, on="ID-code")

    We compute the conductance, and sum it per cell using ``pandas`` methods:

    >>> joined["conductance"] = joined["area"] / joined["c0"]
    >>> summed_conductance = joined.groupby(["row_index", "col_index"], as_index=False)[
            "conductance"
        ].sum()

    Finally, turn the result into a DataArray so it can be used as model input:

    >>> conductance = imod.prepare.rasterize_celltable(
            table=summed_conductance,
            column="conductance",
            like=like,
        )

    """
    dx, _, _, dy, _, _ = imod.util.spatial_reference(like)
    if not (np.atleast_1d(dx) % resolution == 0.0).all():
        raise ValueError("resolution is not an (integer) divisor of dx")
    if not (np.atleast_1d(dy) % resolution == 0.0).all():
        raise ValueError("resolution is not an (integer) divisor of dy")

    like_chunks, rowstarts, colstarts = _create_chunks(like, resolution, chunksize)
    collection = [
        dask.delayed(_celltable)(path, column, resolution, chunk, rowstart, colstart)
        for chunk, rowstart, colstart in zip(like_chunks, rowstarts, colstarts)
    ]
    result = dask.compute(collection)[0]
    return pd.concat(result)


@numba.njit
def _burn_cells(raster, rows, cols, values):
    """
    Burn values of sparse COO-matrix into raster.
    rows, cols, and values form a sparse matrix in coordinate format (COO)
    (also known as "ijv" or "triplet" format).

    Parameters
    ----------
    raster : np.array
        raster to burn values into.
    rows : np.array of integers 
        row indices (i)
    cols : np.array of integers
        column indices (j)
    values : np.array of floats
        values to burn (v)
    """
    for i, j, v in zip(rows, cols, values):
        raster[i, j] = v
    return raster


def rasterize_celltable(table, column, like):
    """
    Rasterizes a table, such as produced by ``imod.prepare.spatial.celltable``.
    Before rasterization, multiple values should be grouped and aggregated per
    cell. Values will be overwritten otherwise.

    Parameters
    ----------
    like : xr.DataArray
    table : pandas.DataFrame
        with columns: "row_index", "col_index"
    column : str, int, float
        column name of values to rasterize

    Returns
    -------
    rasterized : xr.DataArray
    """
    rows = table["row_index"].values
    cols = table["col_index"].values
    area = table[column].values
    dst = like.copy()
    dst.values = _burn_cells(dst.values, rows, cols, area)
    return dst
