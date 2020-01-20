import requests

SERVICE_URL = "https://olinda.bcb.gov.br/olinda/service/PTAX/version/v1/odata/"
RESOURCE = "DollarRateDate(dataCotacao=@dataCotacao)"


def close(date: str) -> dict:
    """
    Retrieve closing Ptax rates on a certain date.

    Parameters
    ----------
    date : str
        The desired date in the format 'MM-DD-YYYY'

    Returns
    -------
    dict
        The closing rates data

    Examples
    --------
    >>> close('01-16-2020')
    {'datetime': '2020-01-17 13:09:30.096', 'bid': '4.1831', 'ask': '4.1837'}

    """
    params = f"@dataCotacao={date!r}&$format=json"
    response = requests.get(f"{SERVICE_URL}{RESOURCE}", params=params)
    raw_data = response.json()["value"][0]
    return {
        "datetime": raw_data["dataHoraCotacao"],
        "bid": f'{raw_data["cotacaoCompra"]:.4f}',
        "ask": f'{raw_data["cotacaoVenda"]:.4f}',
    }
