from .client import Ptax
from .resources import CloseResource


def close(date: str) -> object:
    """
    Retrieve closing Ptax rates on a certain date.

    Parameters
    ----------
    date : str
        The desired date in the format 'MM-DD-YYYY'

    Returns
    -------
    object
        A CloseReport object with datetime, bid and ask attributes

    Examples
    --------
    >>> close_report = close('01-20-2020')
    >>> close_report
    CloseReport(datetime=2020-01-20 13:09:02.871, bid=4.1823, ask=4.1829)
    >>> print(close_report)
    2020-01-20 13:09:02.871 - bid: 4.1823 - ask: 4.1829
    >>> close_report.bid
    4.1823
    >>> close_report.ask
    4.1829
    >>> close_report.as_dict
    {'datetime': '2020-01-20 13:09:02.871', 'bid': '4.1823', 'ask': '4.1829'}

    """
    resource = CloseResource(date)
    return Ptax(resource).response()
