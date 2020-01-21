#   Copyright 2019 AUI, Inc. Washington DC, USA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


def ms_to_zarr(infile, outfile=None, ddi=None, compressor=None, chunk_size_mb=512, chan_chunks=False):
    """
    Convert legacy format MS to xarray Visibility Dataset compatible zarr format

    This function requires CASA6 casatools module.

    Parameters
    ----------
    infile : str
        Input MS filename
    outfile : str
        Output zarr filename. If None, will use infile name with .vis.zarr extension
    ddi : int
        Specific ddi to convert. Leave as None to convert entire MS
    compressor : numcodecs.blosc.Blosc
        The blosc compressor to use when saving the converted data to disk using zarr.
        If None the zstd compression algorithm used with compression level 2.
    chunk_size_mb: float
        Zarr chunk size in megabytes. Default is 512 MB
    chan_chunks: bool
        Chunk along channel and then if necessary along time.  Default is False
    Returns
    -------
    """
    import os
    from casatools import table as tb
    from casatools import measures
    from numcodecs import Blosc
    import pandas as pd
    import xarray
    import numpy as np
    import time
    import datetime
    from itertools import cycle
    import warnings
    warnings.filterwarnings('ignore', category=FutureWarning)

    chunk_size_mb = int(chunk_size_mb)
    if compressor is None:
        compressor = Blosc(cname='zstd', clevel=2, shuffle=0)
    
    # parse filename to use
    infile = os.path.expanduser(infile)
    prefix = infile[:infile.rindex('.')]
    if outfile is None:
        outfile = prefix + '.vis.zarr'
    else:
        outfile = os.path.expanduser(outfile)
    
    # need to manually remove existing parquet file (if any)
    os.system("rm -fr " + outfile)
    os.system("mkdir " + outfile)
    start = time.time()
    
    MS = tb(infile)
    MS.open(infile, nomodify=True, lockoptions={'option': 'usernoread'})
    
    # let's assume that each DATA_DESC_ID is a fixed shape that may differ from others
    # process each DATA_DESC_ID and place it in its own partition
    ddis = MS.taql('select distinct DATA_DESC_ID from %s' % prefix + '.ms').getcol('DATA_DESC_ID')
    
    MS.close()
    
    if compressor is None:
        compressor = Blosc(cname='zstd', clevel=2, shuffle=0)
    
    # helper for normalizing variable column shapes
    def apad(arr, ts):
        return np.pad(arr, (0, ts[0] - arr.shape[0])) if arr.ndim == 1 else np.pad(arr,
                                                                                   ((0, ts[0] - arr.shape[0]), (0, ts[1] - arr.shape[1])))
    
    # helper for reading time columns to datetime format, there must be a better way to do this
    def convert_time(tdata):
        # me = measures()
        # ms_today = me.epoch('iat', 'today')['m0']['value'] * 24 * 60 * 60
        # real_today = datetime.datetime.now().timestamp()
        # correction = ms_today - real_today
        # return pd.to_datetime(np.array(tdata) - correction, unit='s').values
        return tdata
    
    ############################################
    # build combined metadata xarray dataset from each table in the ms directory (other than main)
    # - we want as much as possible to be stored as data_vars with appropriate coordinates
    # - whenever possible, meaningless id fields are replaced with string names as the coordinate index
    # - some things that are too variably structured will have to go in attributes
    # - this pretty much needs to be done individually for each table, some generalization is possible but it makes things too complex
    ############################################
    mvars, mcoords, mattrs = {}, {}, {}
    tables = ['DATA_DESCRIPTION', 'SPECTRAL_WINDOW', 'POLARIZATION', 'SORTED_TABLE']  # initialize to things we don't want to process now
    ms_meta = tb()
    
    ## ANTENNA table
    tables += ['ANTENNA']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        mcoords['antenna'] = list(range(ms_meta.nrows()))
        for col in ms_meta.colnames():
            data = ms_meta.getcol(col).transpose()
            if data.ndim == 1:
                mvars['ANT_' + col] = xarray.DataArray(data, dims=['antenna'])
            else:
                mvars['ANT_' + col] = xarray.DataArray(data, dims=['antenna', 'd' + str(data.shape[1])])
        ms_meta.close()
    
    ## FEED table
    tables += ['FEED']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() > 0:
            mcoords['spw'] = ms_meta.taql('select distinct SPECTRAL_WINDOW_ID from %s' % os.path.join(infile, tables[-1])).getcol(
                'SPECTRAL_WINDOW_ID')
            mcoords['feed'] = ms_meta.taql('select distinct FEED_ID from %s' % os.path.join(infile, tables[-1])).getcol('FEED_ID')
            mcoords['receptors'] = list(range(
                np.max(ms_meta.taql('select distinct NUM_RECEPTORS from %s' % os.path.join(infile, tables[-1])).getcol('NUM_RECEPTORS'))))
            antidx, spwidx, feedidx = ms_meta.getcol('ANTENNA_ID'), ms_meta.getcol('SPECTRAL_WINDOW_ID'), ms_meta.getcol('FEED_ID')
            if ms_meta.nrows() != (len(np.unique(antidx)) * len(np.unique(spwidx)) * len(np.unique(feedidx))): print(
                'WARNING: index mismatch in %s table' % tables[-1])
            for col in ms_meta.colnames():
                if col in ['SPECTRAL_WINDOW_ID', 'ANTENNA_ID', 'FEED_ID']: continue
                if ms_meta.isvarcol(col):
                    tshape, tdim = (len(mcoords['receptors']),), ('receptors',)
                    if col == 'BEAM_OFFSET':
                        tshape, tdim = (2, len(mcoords['receptors'])), ('d2', 'receptors')
                    elif col == 'POL_RESPONSE':
                        tshape, tdim = (len(mcoords['receptors']), len(mcoords['receptors'])), ('receptors', 'receptors')
                    data = ms_meta.getvarcol(col)
                    data = np.array([apad(data['r' + str(kk)][..., 0], tshape) for kk in np.arange(len(data)) + 1])
                    metadata = np.full((len(mcoords['spw']), len(mcoords['antenna']), len(mcoords['feed'])) + tshape, np.nan,
                                       dtype=data.dtype)
                    metadata[spwidx, antidx, feedidx] = data
                    mvars['FEED_' + col] = xarray.DataArray(metadata, dims=['spw', 'antenna', 'feed'] + list(tdim))
                else:
                    data = ms_meta.getcol(col).transpose()
                    if col == 'TIME': data = convert_time(data)
                    if data.ndim == 1:
                        metadata = np.full((len(mcoords['spw']), len(mcoords['antenna']), len(mcoords['feed'])), np.nan, dtype=data.dtype)
                        metadata[spwidx, antidx, feedidx] = data
                        mvars['FEED_' + col] = xarray.DataArray(metadata, dims=['spw', 'antenna', 'feed'])
                    else:  # only POSITION should trigger this
                        metadata = np.full((len(mcoords['spw']), len(mcoords['antenna']), len(mcoords['feed']), data.shape[1]), np.nan,
                                           dtype=data.dtype)
                        metadata[spwidx, antidx, feedidx] = data
                        mvars['FEED_' + col] = xarray.DataArray(metadata, dims=['spw', 'antenna', 'feed', 'd' + str(data.shape[1])])
        ms_meta.close()
    
    ## FIELD table
    tables += ['FIELD']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() > 0:
            funique, fidx, fcount = np.unique(ms_meta.getcol('NAME'), return_inverse=True, return_counts=True)
            mcoords['field'] = [funique[ii] if fcount[ii] == 1 else funique[ii] + ' (%s)' % str(nn) for nn, ii in enumerate(fidx)]
            max_poly = np.max(ms_meta.taql('select distinct NUM_POLY from %s' % os.path.join(infile, tables[-1])).getcol('NUM_POLY')) + 1
            tshape = (2, max_poly)
            if ms_meta.nrows() != len(mcoords['field']): print('WARNING: index mismatch in %s table' % tables[-1])
            for col in ms_meta.colnames():
                if col in ['NAME']: continue
                if ms_meta.isvarcol(col):
                    data = ms_meta.getvarcol(col)
                    data = np.array([apad(data['r' + str(kk)][..., 0], tshape) for kk in np.arange(len(data)) + 1])
                    mvars['FIELD_' + col] = xarray.DataArray(data, dims=['field', 'd2', 'd' + str(max_poly)])
                else:
                    data = ms_meta.getcol(col).transpose()
                    if col == 'TIME': data = convert_time(data)
                    mvars['FIELD_' + col] = xarray.DataArray(data, dims=['field'])
        ms_meta.close()
    
    ## OBSERVATION table
    tables += ['OBSERVATION']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() > 0:
            funique, fidx, fcount = np.unique(ms_meta.getcol('PROJECT'), return_inverse=True, return_counts=True)
            mcoords['observation'] = [funique[ii] if fcount[ii] == 1 else funique[ii] + ' (%s)' % str(nn) for nn, ii in enumerate(fidx)]
            for col in ms_meta.colnames():
                if col in ['PROJECT']: continue
                if not ms_meta.isvarcol(col):
                    data = ms_meta.getcol(col).transpose()
                    if col == 'TIME_RANGE':
                        data = np.hstack((convert_time(data[:, 0])[:, None], convert_time(data[:, 1])[:, None]))
                        mvars['OBS_' + col] = xarray.DataArray(data, dims=['observation', 'd2'])
                    else:
                        mvars['OBS_' + col] = xarray.DataArray(data, dims=['observation'])
        ms_meta.close()
    
    ## POINTING table
    tables += ['POINTING']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() > 0:
            mcoords['point_time'], timeidx = np.unique(convert_time(ms_meta.getcol('TIME')), return_inverse=True)
            max_poly = np.max(ms_meta.taql('select distinct NUM_POLY from %s' % os.path.join(infile, tables[-1])).getcol('NUM_POLY')) + 1
            antidx = ms_meta.getcol('ANTENNA_ID')
            tshape = (2, max_poly)
            if ms_meta.nrows() != (len(mcoords['point_time']) * len(mcoords['antenna'])): print(
                'WARNING: index mismatch in %s table' % tables[-1])
            for col in ms_meta.colnames():
                if col in ['TIME', 'ANTENNA_ID']: continue
                if ms_meta.isvarcol(col):
                    data = ms_meta.getvarcol(col)
                    data = np.array([apad(data['r' + str(kk)][..., 0], tshape) for kk in np.arange(len(data)) + 1])
                    metadata = np.full((len(mcoords['point_time']), len(mcoords['antenna'])) + tshape, np.nan, dtype=data.dtype)
                    metadata[timeidx, antidx] = data
                    mvars['POINT_' + col] = xarray.DataArray(metadata, dims=['point_time', 'antenna', 'd' + str(max_poly)])
                else:
                    data = ms_meta.getcol(col).transpose()
                    metadata = np.full((len(mcoords['point_time']), len(mcoords['antenna'])), np.nan, dtype=data.dtype)
                    metadata[timeidx, antidx] = data
                    mvars['POINT_' + col] = xarray.DataArray(metadata, dims=['point_time', 'antenna'])
        ms_meta.close()
    
    ## PROCESSOR table
    tables += ['PROCESSOR']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() > 0:
            funique, fidx, fcount = np.unique(ms_meta.getcol('TYPE'), return_inverse=True, return_counts=True)
            mcoords['processor'] = [funique[ii] if fcount[ii] == 1 else funique[ii] + ' (%s)' % str(nn) for nn, ii in enumerate(fidx)]
            for col in ms_meta.colnames():
                if col in ['TYPE']: continue
                if not ms_meta.isvarcol(col):
                    data = ms_meta.getcol(col).transpose()
                    mvars['PROC_' + col] = xarray.DataArray(data, dims=['processor'])
        ms_meta.close()
    
    ## SOURCE table
    tables += ['SOURCE']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() > 0:
            mcoords['source'] = np.unique(ms_meta.getcol('SOURCE_ID'))
            max_lines = np.max(ms_meta.taql('select distinct NUM_LINES from %s' % os.path.join(infile, tables[-1])).getcol('NUM_LINES'))
            srcidx, spwidx = ms_meta.getcol('SOURCE_ID'), ms_meta.getcol('SPECTRAL_WINDOW_ID')
            tshape = (2, max_lines)
            if ms_meta.nrows() != (len(mcoords['source']) * len(mcoords['spw'])): print('WARNING: index mismatch in %s table' % tables[-1])
            for col in ms_meta.colnames():
                if col in ['SOURCE_ID', 'SPECTRAL_WINDOW_ID']: continue
                if ms_meta.isvarcol(col) and (tshape[1] > 0) and (col not in ['POSITION', 'SOURCE_MODEL', 'PULSAR_ID']):
                    data = ms_meta.getvarcol(col)
                    data = np.array([apad(data['r' + str(kk)][..., 0], tshape) for kk in np.arange(len(data)) + 1])
                    metadata = np.full((len(mcoords['spw']), len(mcoords['source'])) + tshape, np.nan, dtype=data.dtype)
                    metadata[spwidx, srcidx] = data
                    mvars['SRC_' + col] = xarray.DataArray(metadata, dims=['spw', 'source', 'd' + str(max_lines)])
                elif ms_meta.iscelldefined(col, 0):
                    data = ms_meta.getcol(col).transpose()
                    if col == 'TIME': data = convert_time(data)
                    if data.ndim == 1:
                        metadata = np.full((len(mcoords['spw']), len(mcoords['source'])), np.nan, dtype=data.dtype)
                        metadata[spwidx, srcidx] = data
                        mvars['SRC_' + col] = xarray.DataArray(metadata, dims=['spw', 'source'])
                    else:
                        metadata = np.full((len(mcoords['spw']), len(mcoords['source']), data.shape[1]), np.nan, dtype=data.dtype)
                        metadata[spwidx, srcidx] = data
                        mvars['SRC_' + col] = xarray.DataArray(metadata, dims=['spw', 'source', 'd' + str(data.shape[1])])
        ms_meta.close()
    
    ## STATE table
    tables += ['STATE']
    if os.path.isdir(os.path.join(infile, tables[-1])):
        ms_meta.open(os.path.join(infile, tables[-1]), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() > 0:
            funique, fidx, fcount = np.unique(ms_meta.getcol('OBS_MODE'), return_inverse=True, return_counts=True)
            mcoords['state'] = [funique[ii] if fcount[ii] == 1 else funique[ii] + ' (%s)' % str(nn) for nn, ii in enumerate(fidx)]
            for col in ms_meta.colnames():
                if col in ['OBS_MODE']: continue
                if not ms_meta.isvarcol(col):
                    data = ms_meta.getcol(col).transpose()
                    mvars['STATE_' + col] = xarray.DataArray(data, dims=['state'])
        ms_meta.close()
    
    # remaining junk for the attributes section
    other_tables = [tt for tt in os.listdir(infile) if os.path.isdir(os.path.join(infile, tt)) and tt not in tables]
    other_tables = dict([(tt, tt[:4] + '_') for tt in other_tables])
    for ii, tt in enumerate(other_tables.keys()):
        print('processing support table %s of %s : %s' % (str(ii), str(len(other_tables.keys())), tt), end='\r')
        ms_meta.open(os.path.join(infile, tt), nomodify=True, lockoptions={'option': 'usernoread'})
        if ms_meta.nrows() == 0: continue
        for col in ms_meta.colnames():
            if ms_meta.isvarcol(col) and ms_meta.iscelldefined(col, 0):
                data = ms_meta.getvarcol(col)
                data = [data['r' + str(kk)].tolist() for kk in np.arange(len(data)) + 1]
                mattrs[other_tables[tt] + col] = data
            elif not ms_meta.isvarcol(col):
                data = ms_meta.getcol(col).transpose()
                mattrs[other_tables[tt] + col] = data.tolist()
        ms_meta.close()
    
    # write the global meta data to a separate global partition in the zarr output directory
    mxds = xarray.Dataset(mvars, coords=mcoords, attrs=mattrs)
    mxds.to_zarr(outfile + '/global', mode='w')
    
    print('meta data processing time ', time.time() - start)
    
    ####################################################################
    # process a DDI from the input MS, assume a fixed shape within the ddi (should always be true)
    # each DDI is written to its own subdirectory under the parent folder
    # consequently, different DDI's may be processed in parallel if the MS is opened with no locks
    def processDDI(ddi, infile, outfile, compressor, chunk_size_mb, chan_chunks):
        print('**********************************')
        print('Processing ddi', ddi)
        start_ddi = time.time()
        
        # Open measurement set (ms) select ddi and sort main table by TIME,ANTENNA1,ANTENNA2
        tb_tool = tb()
        tb_tool.open(infile, nomodify=True, lockoptions={'option': 'usernoread'})  # allow concurrent reads
        ms_ddi = tb_tool.taql('select * from %s where DATA_DESC_ID = %s ORDERBY TIME,ANTENNA1,ANTENNA2' % (infile, str(ddi)))
        print('Selecting and sorting time ', time.time() - start_ddi)
        start_ddi = time.time()
        
        tdata = ms_ddi.getcol('TIME')
        times = convert_time(tdata)
        unique_times, time_changes, time_idxs = np.unique(times, return_index=True, return_inverse=True)
        n_time = unique_times.shape[0]
        
        ant1_col = np.array(ms_ddi.getcol('ANTENNA1'))
        ant2_col = np.array(ms_ddi.getcol('ANTENNA2'))
        ant1_ant2 = np.hstack((ant1_col[:, np.newaxis], ant2_col[:, np.newaxis]))
        unique_baselines, baseline_idxs = np.unique(ant1_ant2, axis=0, return_inverse=True)
        n_baseline = unique_baselines.shape[0]
        
        # look up spw and pol ids as starting point
        tb_tool_meta = tb()
        tb_tool_meta.open(infile + "/DATA_DESCRIPTION", nomodify=True, lockoptions={'option': 'usernoread'})
        spw_id = tb_tool_meta.getcol("SPECTRAL_WINDOW_ID")[ddi]
        pol_id = tb_tool_meta.getcol("POLARIZATION_ID")[ddi]
        tb_tool_meta.close()
        
        ###################
        # build metadata structure from remaining spw-specific table fields
        aux_coords = {'time': unique_times, 'spw': np.array([spw_id]), 'antennas': (['baseline', 'pair'], unique_baselines)}
        meta_attrs = {'DDI': ddi, 'AUTO_CORRELATIONS': int(np.any(ant1_col == ant2_col))}
        for tt in ['POLARIZATION', 'SPECTRAL_WINDOW']:
            if os.path.isdir(os.path.join(infile, tt)):
                tb_tool_meta.open(os.path.join(infile, tt), nomodify=True, lockoptions={'option': 'usernoread'})
                if tt in ['FEED', 'FREQ_OFFSET', 'SOURCE', 'SYSCAL']:
                    tb_tool_meta = tb_tool_meta.taql(
                        'select * from %s where SPECTRAL_WINDOW_ID = %s' % (os.path.join(infile, tt), str(spw_id)))
                for col in tb_tool_meta.colnames():
                    if col in ['SPECTRAL_WINDOW_ID', 'FLAG_ROW', 'NUM_CORR']: continue  # don't need
                    if not tb_tool_meta.iscelldefined(col, 0): continue
                    if col in ['CHAN_FREQ', 'CHAN_WIDTH', 'EFFECTIVE_BW', 'RESOLUTION']:
                        aux_coords[col.lower()] = ('chan', tb_tool_meta.getcol(col, spw_id, 1)[:, 0])
                    elif col == 'CORR_TYPE':
                        aux_coords[col.lower()] = ('pol', tb_tool_meta.getcol(col, pol_id, 1)[:, 0])
                    elif col == 'CORR_PRODUCT':
                        aux_coords[col.lower()] = (['receptor', 'pol'], tb_tool_meta.getcol(col, pol_id, 1)[:, :, 0])
                    else:
                        meta_attrs[col] = tb_tool_meta.getcol(col).transpose()[0]
                tb_tool_meta.close()
        
        n_chan = len(aux_coords['chan_freq'][1])
        n_pol = len(aux_coords['corr_type'][1])
        
        if chan_chunks:
            chunk_size = np.int(np.ceil((chunk_size_mb * 10 ** 6) / (n_baseline * 1 * n_pol * 16)))
            chan_chunk_size = 1
            if chunk_size > n_time:
                chan_chunk_size = np.int(np.ceil((chunk_size_mb * 10 ** 6) / (n_baseline * n_time * n_pol * 16)))
                chunk_size = n_time
        else:
            chunk_size = min(np.int(np.ceil((chunk_size_mb * 10 ** 6) // (n_baseline * n_chan * n_pol * 16))), n_time)
            print('n_time:', n_time, '  n_baseline:', n_baseline,'  n_chan:', n_chan, '  n_pol:', n_pol, '  number of time steps in chunk:', chunk_size)

        coords = {'time': unique_times, 'baseline': np.arange(n_baseline), 'chan': aux_coords.pop('chan_freq')[1],
                  'pol': aux_coords.pop('corr_type')[1], 'uvw': np.array(['uu', 'vv', 'ww'])}
        
        ###################
        # main table loop over each column of each chunk
        for cc, start_row_indx in enumerate(range(0, n_time, chunk_size)):
            rtestimate = ', remaining time est %s s' % str(
                int(((time.time() - start_ddi) / cc) * (n_time / chunk_size - cc))) if cc > 0 else ''
            print('processing chunk %s of %s' % (str(cc), str(n_time // chunk_size)) + rtestimate, end='\r')
            chunk = np.arange(min(chunk_size, n_time - start_row_indx)) + start_row_indx
            chunk_time_changes = time_changes[chunk] - time_changes[chunk[0]]  # indices in this chunk of data where time value changes
            end_idx = time_changes[chunk[-1] + 1] if chunk[-1] + 1 < len(time_changes) else len(time_idxs)
            idx_range = np.arange(time_changes[chunk[0]], end_idx)  # indices (rows) in main table to be read
            coords.update({'time': unique_times[chunk]})
            
            chunkdata = {}
            for col in ms_ddi.colnames():
                if col in ['DATA_DESC_ID', 'TIME']: continue
                if not ms_ddi.iscelldefined(col, idx_range[0]): continue
                
                data = ms_ddi.getcol(col, idx_range[0], len(idx_range)).transpose()
                
                if col in 'UVW':  # n_row x 3 -> n_time x n_baseline x 3
                    fulldata = np.full((len(chunk), n_baseline, data.shape[1]), np.nan, dtype=data.dtype)
                    fulldata[time_idxs[idx_range] - chunk[0], baseline_idxs[idx_range], :] = data
                    chunkdata[col] = xarray.DataArray(fulldata, dims=['time', 'baseline', 'uvw'])
                
                elif data.ndim == 1:  # n_row -> n_time x n_baseline
                    if col == 'FIELD_ID' and 'field' in mxds.coords:
                        coords['field'] = ('time', mxds.coords['field'].values[data[chunk_time_changes]])
                    elif col == 'SCAN_NUMBER' and 'scan' in mxds.coords:
                        coords['scan'] = ('time', data[chunk_time_changes])
                    elif col == 'INTERVAL':
                        coords['interval'] = ('time', data[chunk_time_changes])
                    elif col == 'PROCESSOR_ID' and 'processor' in mxds.coords:
                        coords['processor'] = ('time', mxds.coords['processor'].values[data[chunk_time_changes]])
                    elif col == 'OBSERVATION_ID' and 'observation' in mxds.coords:
                        coords['observation'] = ('time', mxds.coords['observation'].values[data[chunk_time_changes]])
                    elif col == 'STATE_ID' and 'state' in mxds.coords:
                        coords['state'] = ('time', mxds.coords['state'].values[data[chunk_time_changes]])
                    else:
                        fulldata = np.full((len(chunk), n_baseline), np.nan, dtype=data.dtype)
                        if col == 'FLAG_ROW':
                            fulldata = np.ones((len(chunk), n_baseline), dtype=data.dtype)
                        fulldata[time_idxs[idx_range] - chunk[0], baseline_idxs[idx_range]] = data
                        chunkdata[col] = xarray.DataArray(fulldata, dims=['time', 'baseline'])
                
                elif (data.ndim == 2) and (data.shape[1] == n_pol):
                    fulldata = np.full((len(chunk), n_baseline, n_pol), np.nan, dtype=data.dtype)
                    fulldata[time_idxs[idx_range] - chunk[0], baseline_idxs[idx_range], :] = data
                    chunkdata[col] = xarray.DataArray(fulldata, dims=['time', 'baseline', 'pol'])
                
                elif (data.ndim == 2) and (data.shape[1] == n_chan):
                    fulldata = np.full((len(chunk), n_baseline, n_chan), np.nan, dtype=data.dtype)
                    fulldata[time_idxs[idx_range] - chunk[0], baseline_idxs[idx_range], :] = data
                    chunkdata[col] = xarray.DataArray(fulldata, dims=['time', 'baseline', 'chan'])
                
                elif data.ndim == 3:
                    assert (data.shape[1] == n_chan) & (data.shape[2] == n_pol), 'Column dimensions not correct'
                    if col == "FLAG":
                        fulldata = np.ones((len(chunk), n_baseline, n_chan, n_pol), dtype=data.dtype)
                    else:
                        fulldata = np.full((len(chunk), n_baseline, n_chan, n_pol), np.nan, dtype=data.dtype)
                    fulldata[time_idxs[idx_range] - chunk[0], baseline_idxs[idx_range], :, :] = data
                    chunkdata[col] = xarray.DataArray(fulldata, dims=['time', 'baseline', 'chan', 'pol'])
            
            if chan_chunks:
                x_dataset = xarray.Dataset(chunkdata, coords=coords).chunk({'time': chunk_size, 'baseline': None, 'chan': chan_chunk_size, 'pol': None, 'uvw': None})
            else:
                x_dataset = xarray.Dataset(chunkdata, coords=coords).chunk({'time': chunk_size, 'baseline': None, 'chan': None, 'pol': None, 'uvw': None})

            # if cc > 0:
            #    xds = xarray.open_zarr(outfile + '/' + str(ddi))
            #    x_dataset = xarray.concat([xds, x_dataset], coords='all', compat='broadcast_equals', dim='time')
            if cc == 0:
                encoding = dict(zip(list(x_dataset.data_vars), cycle([{'compressor': compressor}])))
                x_dataset.to_zarr(outfile + '/' + str(ddi), mode='w', encoding=encoding)
            else:
                x_dataset.to_zarr(outfile + '/' + str(ddi), mode='a', append_dim='time', compute=True)
        
        # Add non dimensional auxiliary coordinates and attributes
        aux_coords.update({'time': unique_times})
        x_dataset = xarray.Dataset(coords=aux_coords, attrs=meta_attrs)
        x_dataset.to_zarr(outfile + '/' + str(ddi), mode='a')
        
        ms_ddi.close()
        print('Completed ddi', ddi, ' process time ', time.time() - start_ddi)
        print('**********************************')
    
    #########################################
    
    # Parallelize with direct interface
    client = None  # GetFrameworkClient()
    if ddi is not None:
        processDDI(ddi, infile, outfile, compressor, chunk_size_mb, chan_chunks)
    elif client is None:
        for ddi in ddis:
            processDDI(ddi, infile, outfile, compressor, chunk_size_mb, chan_chunks)
    else:
        jobs = client.map(processDDI, ddis,
                          np.repeat(infile, len(ddis)),
                          np.repeat(outfile, len(ddis)),
                          np.repeat(compressor, len(ddis)),
                          np.repeat(chunk_size_mb, len(ddis)),
                          np.repeat(chan_chunks, len(ddis)))

        # block until complete
        for job in jobs: job.result()
        print('Complete.')
