import datetime

from .core import UnitedStates
from ..core import MON
from ..core import Holiday
from ..registry import iso_register


@iso_register('US-AK')
class Alaska(UnitedStates):
    """Alaska"""
    FIXED_HOLIDAYS = UnitedStates.FIXED_HOLIDAYS + (
        Holiday(
            datetime.date(2000, 10, 18),
            'Alaska Day',
        ),
    )
    include_columbus_day = False

    def get_variable_days(self, year):
        days = super().get_variable_days(year)
        days.append(
            (Alaska.get_last_weekday_in_month(year, 3, MON), "Seward's Day")
        )
        return days
