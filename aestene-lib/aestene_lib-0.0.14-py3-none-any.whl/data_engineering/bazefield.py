import datetime as dt
import json
import re
import requests
import pandas as pd
import numpy as np
import urllib3

from requests.auth import HTTPBasicAuth

from aeslib.data_engineering import azure_tools as at

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_datetime_as_string(timestamp: dt.datetime.timestamp,
                           string_format="%Y_%m_%d_%H_%M_%S") -> str:
    time_stamp_as_datetime = dt.datetime.fromtimestamp(timestamp / 1000)
    return time_stamp_as_datetime.strftime(string_format)

def reduce_dataframe_size(df) -> pd.DataFrame:
    df.loc[:, df.select_dtypes(include=np.float64).columns] \
        = df.select_dtypes(include=np.float64).astype(np.float32)
    return df

def get_bazefield_authentication_from_key_vault(key_vault_name: str) -> HTTPBasicAuth:
    api_key = at.get_secret_from_key_vault(key_vault_name, secret_name='bazefield-api-key')
    return HTTPBasicAuth(api_key, '')

def get_bazefield_headers() -> dict:
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*'}
    return headers

def get_full_tag_list_from_bazefield(key_vault_name: str):
    auth = get_bazefield_authentication_from_key_vault(key_vault_name)
    tag_list_url = at.get_secret_from_key_vault(key_vault_name, secret_name='bazefield-tagid-url')
    tag_list = requests.get(url=tag_list_url, verify=False, auth=auth)
    return json.loads(tag_list.text)

def match_taglist_to_regular_expression(tag_list: list, regular_expression: str) -> list:
    tag_ids = [t["tagId"] for t in tag_list
               if re.match(regular_expression, t["tagName"])]
    return tag_ids

def get_transformed_tag_list_from_bazefield(reg_ex_strings: list, key_vault_name: str):
    tag_list = get_full_tag_list_from_bazefield(key_vault_name)

    tag_ids = []

    for reg_ex in reg_ex_strings:
        tag_ids = tag_ids + match_taglist_to_regular_expression(tag_list=tag_list,
                                                                regular_expression=reg_ex)

    tag_list_to_download = {"tagIds": str(tag_ids)[1:-1].replace(" ", "")}

    tag_list_to_download["dateTimeFormat"] = "dd-MM-yyyy HH:mm:ss.fff"
    tag_list_to_download["calenderUnit"] = "Minute"
    tag_list_to_download["useAssetTitle"] = False
    tag_list_to_download["useInterval"] = True
    tag_list_to_download["exportInUtc"] = True
    return json.dumps(tag_list_to_download)

def prepare_download(from_timestamp: int,
                     key_vault_name: str,
                     aggregates: str,
                     interval: str,
                     reg_ex_strings: list,
                     download_file_resolution=1000*3600*24):

    from_timestamp_as_string = get_datetime_as_string(from_timestamp)
    end_timestamp = from_timestamp + download_file_resolution

    print("Downloading " + from_timestamp_as_string)

    url = at.get_secret_from_key_vault(key_vault_name, secret_name='bazefield-data-export-url')
    auth = get_bazefield_authentication_from_key_vault(key_vault_name)
    headers = get_bazefield_headers()
    proxy = {'https': at.get_secret_from_key_vault(key_vault_name, secret_name='equinor-proxy')}
    data = get_transformed_tag_list_from_bazefield(reg_ex_strings, key_vault_name)

    res = requests.post(url=url.format(from_timestamp, end_timestamp, interval, aggregates),
                        auth=auth,
                        headers=headers,
                        verify=False,
                        proxies=proxy,
                        data=data)

    filename = res.text
    next_timestamp = end_timestamp

    return filename, next_timestamp, from_timestamp_as_string

def download_file(filename: str, from_timestamp_as_string: str, key_vault_name: str):
    csv_name = from_timestamp_as_string + '.csv'
    filename = filename.replace(".txt", "")

    url = at.get_secret_from_key_vault(key_vault_name, secret_name='bazefield-get-file-url')
    auth = get_bazefield_authentication_from_key_vault(key_vault_name)
    proxy = {'https': at.get_secret_from_key_vault(key_vault_name, secret_name='equinor-proxy')}

    res = requests.get(url=url.format(filename),
                       auth=auth,
                       verify=False,
                       proxies=proxy)

    file = res.content.decode()

    destination = '../Data/UTC/'
    file_path = destination + csv_name

    with open(file_path, 'w') as f:
        f.write(file)
        print("Finished.")
        print("Downloaded to "+ str(file_path))

    df = pd.read_csv(file_path, sep=';')
    df = reduce_dataframe_size(df)

    df.to_csv(file_path, sep=';')

    return True


def download_data_from_bazefield_as_csv(from_timestamp: dt.datetime,
                                        to_timestamp: dt.datetime,
                                        aggregates: str,
                                        interval: str,
                                        reg_ex_strings: list,
                                        key_vault_name: str):
    from_timestamp_int = int(from_timestamp.timestamp()) * 1000
    to_timestamp_int = int(to_timestamp.timestamp())

    while True:
        try:
            filename, next_timestamp, from_timestamp_as_string = \
                prepare_download(from_timestamp=from_timestamp_int,
                                 key_vault_name=key_vault_name,
                                 aggregates=aggregates,
                                 interval=interval,
                                 reg_ex_strings=reg_ex_strings)
            print('Downloading ' + from_timestamp_as_string)
            print(filename)
            _ = download_file(filename, from_timestamp_as_string, key_vault_name)
        except Exception as e:
            print(e)
            from_timestamp_int = next_timestamp
            continue
        
        if dt.datetime.fromtimestamp(next_timestamp / 1000) \
           > dt.datetime.fromtimestamp(to_timestamp_int):
            return
        else:
            from_timestamp_int = next_timestamp
