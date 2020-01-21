class DataCorrectorBase(ABC):

    @abstractmethod
    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        pass

    def get_freq(self, df: pd.DataFrame)->dt.timedelta:
        return Utility.get_freq(df)


class StateRunDataCorrector(DataCorrectorBase):
    def __init__(self, bazefield_client: BazefieldClient, keyvault: AzureKeyvaultHelper, df_tags: pd.DataFrame, statecol_pattern: str = 'StateRun', interpolate:bool = True):
        self.bazefield_client = bazefield_client
        self.keyvault = keyvault
        self.df_tags = df_tags
        self.statecol_pattern = statecol_pattern
        self.interpolate = interpolate

    # Assuming Time indexed dataframe
    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        assert not (df is None)
        assert len(df)>2

        #identify frequency
        interval_seconds = self.get_freq(df).seconds
        
        #identify from-to
        from_time = df.index.min()
        to_time = df.index.max() + dt.timedelta(seconds=interval_seconds)
        
        #identify tagIds
        df_state_cols = df.columns[df.columns.str.contains(self.statecol_pattern)]
        tag_ids = self.df_tags.loc[[x.replace(' (Average)', '') for x in df_state_cols.to_list()],'tagId'].to_list()
        
        # Fetch API key
        bazefield_key = self.keyvault.get_secret(BAZEFIELD_KEY_ID)

        # Send request and fetch data frame from Bazefield
        df_states = self.bazefield_client._read_TimeSeriesAgg(tag_ids,str(from_time), str(to_time), bazefield_key, 'END',interval_seconds)
        assert len(df_states) == len(df), f"Inconsistent results from Bazefield: expected {len(df)} data points, got {len(df_states)}"
        
        df_states.columns = df_state_cols
        
        # Interpolate - fill forward
        if self.interpolate:
            df_states.fillna(method='pad', inplace=True)

        # Need to reset index since df is indexed by UK time, df_states is indexed by UTC
        df.reset_index(inplace=True)
        df_states.reset_index(inplace=True)
        df_states.drop(columns=['TimeStamp'], inplace=True)

        df[df_state_cols] = df_states
        df.set_index(['TimeStamp'], inplace=True)

        return df

class MultiIndexDataCorrector(DataCorrectorBase):
    def __init__(self, level0 = 'string_ind',  level1='TimeStamp'):
        self.level0 = level0
        self.level1 = level1

    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        res = df.drop(columns=['Unnamed: 0'])    
        res.reset_index(inplace=True)    
        res.set_index([self.level0, self.level1], inplace=True)         
        return res


class TimeZoneDataCorrector(DataCorrectorBase):
    def __init__(self, tz_source = 'Europe/London', tz_dest = 'UTC', ambiguous ='infer', neutralize_tz : bool = True, level_name='TimeStamp'):
        self.tz_source = tz_source
        self.ambiguous = ambiguous
        self.tz_dest = tz_dest
        self.neutralize_tz = neutralize_tz
        self.level_name = level_name

    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        level = self.level_name if type(df.index) is pd.MultiIndex else None
        res = df.tz_localize(self.tz_source, ambiguous=self.ambiguous, copy=False, level=level).tz_convert(self.tz_dest, level=level)
        if self.neutralize_tz: res = res.tz_convert(None, level=level)
        res.sort_index(inplace=True)
        return res
    
# Assumption:
#  data Index - DateTime, timezone neutral, contains UTC timestamps (no duplicates)
#  cols_to_interpolate does not include "step columns"
class InterpolateDropDataCorrector(DataCorrectorBase):
    def __init__(self, drop_threshold: dt.timedelta, cols_to_interpolate = None, method='linear'):
        self.drop_threshold = drop_threshold
        self.cols_to_interpolate = cols_to_interpolate
        self.method = method
        self.all_intervals = None
        self.dropped_intervals = None


    def get_empty_intervals(self,df: pd.DataFrame)-> pd.DataFrame:
        cols = df.columns if self.cols_to_interpolate is None else self.cols_to_interpolate
        return IntervalAnalysis.get_empty_intervals(df, cols)


    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        cols_to_interpolate = df.columns if self.cols_to_interpolate is None else self.cols_to_interpolate

        # Prepare list of intervals
        df_interval = self.get_empty_intervals(df)

        # Drop big intervals
        df_drops = df_interval[df_interval.duration>self.drop_threshold]
        dfres = df

        for drop in df_drops.itertuples():
            dfres = dfres.drop(axis=0, index = dfres.loc[(dfres.index > drop.interval.left) & (dfres.index < drop.interval.right)].index)

        # Interpolate
        dfres[cols_to_interpolate] = dfres[cols_to_interpolate].interpolate(method=self.method, axis=0)

        self.all_intervals = df_interval
        self.dropped_intervals = df_drops
        return dfres

# Assumption:
#  data Index - DateTime, timezone neutral, contains UTC timestamps (no duplicates)
#  cols_to_interpolate does not include "step columns"
class InterpolateDropMultiDataCorrector(InterpolateDropDataCorrector):
    # def __init__(self, drop_threshold: dt.timedelta, cols_to_interpolate = None, method='linear'):
    #     self.drop_threshold = drop_threshold
    #     self.cols_to_interpolate = cols_to_interpolate
    #     self.method = method
    #     self.all_intervals = None
    #     self.dropped_intervals = None


    def get_empty_intervals_(self,df: pd.DataFrame)-> pd.DataFrame:
        cols = df.columns if self.cols_to_interpolate is None else self.cols_to_interpolate
        return IntervalAnalysisMulti.get_empty_intervals(df, cols)


    def correct_dataframe(self, df: pd.DataFrame)->pd.DataFrame:
        slice_levels = IntervalAnalysisMulti._get_slice_levels(df)
        timeindex_name = IntervalAnalysisMulti._get_timeindex_name(df)
        dfres = None
        for slicer, df_slice in IntervalAnalysisMulti.iterate_time_levels(df):
            df_corrected = super().correct_dataframe(df_slice)
            df_corrected.reset_index(inplace=True)

            if len(slice_levels )==1: slicer = [slicer]
        
            for idx, level in enumerate(slice_levels):
                df_corrected[level] = slicer[idx]

            dfres = df_corrected if dfres is None else pd.concat([dfres, df_corrected], axis=0)


        dfres.set_index(slice_levels + [timeindex_name], inplace=True)
        dfres.sort_index(level=dfres.index.names, inplace=True)
        return dfres


class DataCorrector:
    @staticmethod
    def Execute(df: pd.DataFrame, df_tagids: pd.DataFrame, interpolate:bool = True) ->pd.DataFrame:
        akv = AzureKeyvaultHelper(env.VAULT_URL)
        bf_client = BazefieldClient(env.BAZEFIELD_URL)
        sr_corrector = StateRunDataCorrector(bf_client, akv, df_tagids, interpolate=interpolate)
        # Add more correctors and execute these in a sequence, if needed
        return sr_corrector.correct_dataframe(df)