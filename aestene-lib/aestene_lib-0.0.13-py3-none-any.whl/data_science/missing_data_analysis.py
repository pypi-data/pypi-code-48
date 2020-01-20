from typing import List

import missingno as msno
import pandas as pd


from aeslib.data_science import interval_analysis as ia

def plot_correlation_between_missing_data(df: pd.DataFrame):
    """Get a Seaborn heatmap of column correlations.
    
    Arguments:
        df {pd.DataFrame} -- Pandas dataframe.
    """
    msno.heatmap(df)
    
def find_missing_intervals_for_dataframe(df: pd.DataFrame, cols: List = None) -> pd.DataFrame:
    """Returns a dataframe with all intervals where one or more columns contain a NaN value.
    The dataframe holds the start and end of the interval and it's duration. To examine a
    selection of columns pass in a list of columns in cols.
    
    Arguments:
        df {pd.DataFrame} -- A pandas dataframe with a single-level datetime
        index. Keep in mind that pd.to_datetime() must be formatted correctly.
        cols {List} -- A list of columns to examine. Default is None meaning all
        columns will be evaluated.
    
    Returns:
        pd.DataFrame -- Dataframe with intervals.
    """
    return ia.IntervalAnalysis.get_empty_intervals(df=df, cols=cols)

def plot_missing_intervals(df: pd.DataFrame, group_by=None):
    if group_by is not None:
        grouped = df.groupby(group_by)
        for _, group in grouped:
            msno.matrix(group)
    else:
        msno.matrix(df)
        
def plot_missing_value_column_correlation(df: pd.DataFrame):
    msno.heatmap(df)
