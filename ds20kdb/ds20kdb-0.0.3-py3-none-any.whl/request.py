"""
Helper library for accessing data from the DarkSide 20K Construction
DataBase.
"""


from io import StringIO
import requests
requests.packages.urllib3.disable_warnings()
import pandas
from ds20kdb import auth
from ds20kdb.default import *


__all__ = ['asc', 'desc', 'Request', 'query', 'RequestError']


class RequestError(Exception):
    """Exception class for request errors."""

    def __init__(self, url, status_code, html_message):
        msg = requests.status_codes._codes[status_code]
        super(RequestError, self).__init__(f"""
Error trying to access URL:
{url}
Error code: {status_code} ({msg})
Server responded:
{html_message}

Are you correctly authenticated/authorized?
""")


def to_pandas(function):
    """
    Decorator for automatically export text to pandas dataframe.
    """

    def decorator(self, tablename, **kwargs):
        """
        Return a pandas.DataFrame from text file.
        """

        text = function(self, tablename, **kwargs)
        with StringIO(text) as sio:
            return pandas.read_csv(sio)

    decorator.__name__ = function.__name__

    return decorator


def desc(column):
    """
    Request to order the results by column, in descending order.
    """

    return column+"=d"


def asc(column):
    """
    Request to order the results by column, in ascending order (default).

    This function is kind of uneffective and shall be used only for code
    readability.
    """

    return column


class Request:
    """
    The class to perform data requests to the DB.
    """

    def __init__(self, **kwargs):
        """
        Named arguments:
        - db: use alternative DB instance (optional).
        """

        self.endpoint = kwargs["db"] if "db" in kwargs else DEFAULT_DB_ENDPOINT
        self.request_url = None


    def url(self, tablename, **kwargs):
        """
        Computes the request URL.

        Arguments:
        - tablename: string, the name of the table to request data from.

        Named arguments:
        - columns:     string or list of strings, limits the results to
                       the specified column(s) (default: all columns).
        - wheres:      string or list of strings, applies conditions to
                       the results. Mathematical formulas are accepted,
                       e.g.:

                       wheres=["sipm_pid > 4567", "wafer_id < 20"]

        - inner_join:  dictionary or array of dictionaries, performs one
                       or multiple inner joins operations against other
                       tables. Each dictionary must contain a "table" and
                       a "on" members, e.g.:

                       inner_join={"table": 'wafer', "on": "wafer_id =
                       wafer_pid"}

        - order_by:    string or list of strings, sort the results by the
                       specified column(s). The order of appereance in the
                       list matters. To invert the ordering, use the
                       desc() function, e.g.:

                       order_by=desc("production_date")

        Return:
        A string representing the request URL.
        """

        default_options = { "columns": [], "wheres": [], "inner_join": [],
                "order_by": []}

        default_options.update(kwargs)

        p_columns = default_options["columns"]
        if isinstance(p_columns, str):
            columns = f"c={p_columns}&"
        else:
            columns = "".join([f"c={c}&" for c in p_columns])

        p_wheres = default_options["wheres"]
        if isinstance(p_wheres, str):
            wheres = f"w={p_wheres.replace(' ', '')}&"
        else:
            wheres = "".join([f"w={w.replace(' ', '')}&" for w in p_wheres])

        p_inner_join = default_options["inner_join"]
        if isinstance(p_inner_join, dict):
            inner_join = f"ij={p_inner_join['table']}&on={p_inner_join['on'].replace(' ', '')}&"
        else:
            n = len(p_inner_join)
            inner_join = ""
            for i in range(n):
                ij = f"ij[{i}]={p_inner_join[i]['table']}&"
                on = f"on[{i}]={p_inner_join[i]['on'].replace(' ', '')}&"
                inner_join += ij + on

        p_order_by = default_options["order_by"]
        if isinstance(p_order_by, str):
            order_by = f"ob={p_order_by}&"

        else:
            order_by = "".join([f"ob={o}&" for o in p_order_by])

        return f"{self.endpoint}/api/item/{tablename}?f=csv&{columns}{wheres}{inner_join}{order_by}"

    @to_pandas
    def query(self, tablename, **kwargs):
        """
        Function to retrieve data from the DB.

        See help(Request.url) for the documentation of the parameters.

        Return:
        A pandas.DataFrame object containing the query results.
        """

        self.request_url = self.url(tablename, **kwargs)

        if auth.get_auth():
            req = requests.get(self.request_url, auth=auth.get_auth())
            if req.status_code != 200:
                raise RequestError(self.request_url, req.status_code, req.text)
            return req.text
        else:
            # try with netrc
            req = requests.get(self.request_url)
            if req.status_code != 200:
                raise RequestError(self.request_url, req.status_code, req.text)
            return req.text


def query(tablename, **kwargs):
    """
    Short for Request(kwargs).query(tablename, kwargs).

    See help(Request.query) for documentation.
    """

    return Request(**kwargs).query(tablename, **kwargs)

