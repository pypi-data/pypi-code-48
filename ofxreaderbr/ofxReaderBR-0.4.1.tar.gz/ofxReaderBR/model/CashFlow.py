from datetime import datetime
from enum import Enum

from .Origin import Origin


class CashFlowType(Enum):
    DEBIT = 1
    CREDIT = 2


class CashFlow(object):

    def __init__(self,
                 name: str = 'N/A',
                 flow_type: CashFlowType = CashFlowType.DEBIT,
                 value: float = 0.0,
                 date: datetime = None,
                 cash_date: datetime = None,
                 origin: Origin = None):
        self.name = name
        self.flowType = flow_type
        self.value = value
        self.date = date
        self.cash_date = cash_date
        self.origin = origin

    @property
    def cash_date(self):
        return self.__cash_date

    @cash_date.setter
    def cash_date(self, value):
        if isinstance(value, datetime):
            self.__cash_date = value
        elif isinstance(value, str):
            self.__cash_date = None if value == 'N/A' else datetime.fromisoformat(
                value)
        else:
            self.__cash_date = None

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime):
            self.__date = value
        elif isinstance(value, str):
            self.__date = None if value == 'N/A' else datetime.fromisoformat(
                value)
        else:
            self.__date = None

    @staticmethod
    def __is_valid_value(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def __valid_dates(self):
        return self.cash_date and self.date and self.cash_date >= self.date

    def is_valid(self):
        return (self.__is_valid_value(self.value) and self.__valid_dates() and
                isinstance(self.flowType, CashFlowType) and
                (isinstance(self.origin, Origin) or self.origin is None) and
                type(self.name) == str)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name.strip() == other.name.strip() and
                self.value == other.value and self.date == other.date and
                self.cash_date == other.cash_date and
                self.origin == other.origin)

    def __repr__(self):
        return 'CashFlow: \
                \n\tName: {} \
                \n\tType: {} \
                \n\tValue: {} \
                \n\tDate: {} \
                \n\tCash date: {} \
                \n\tOrigin: {}'.format(self.name, self.flowType.name,
                                       self.value, self.date, self.cash_date,
                                       self.origin)
