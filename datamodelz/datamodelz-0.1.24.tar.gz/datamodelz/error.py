from datetime import datetime


class Error:
    def __init__(self,
                 timeseries_code: str = "",
                 company: str = "",
                 check_name: str = "",
                 date: datetime = datetime.now(),
                 value=None,
                 business_rule=None,
                 reference: str = "",
                 api_call: str = ""):
        self.timeseries_code = timeseries_code
        self.company = company
        self.check_name = check_name
        self.date = date
        self.value = value
        self.business_rule = business_rule
        self.reference = reference
        self.api_call = api_call

    def __repr__(self):
        return self.excel_format()

    def excel_format(self):
        lst = [self.timeseries_code, self.company, self.check_name, self.date, self.value, str(self.business_rule),
               self.reference, self.api_call]
        return ",".join(lst)
