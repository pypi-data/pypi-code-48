import koconf.common as common
import pytest

from datetime import datetime, timedelta
from koconf.db import DataBaseManager
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def days_from_now(days):
    return (datetime.now() + timedelta(days=days)).strftime(common.date_format)


@pytest.fixture(autouse=True)
def mock_init(mocker):
    def init(self):
        self._DataBaseManager__db = TinyDB(storage=MemoryStorage)
        self._DataBaseManager__query = Query()
        data = [
            {
                "id": "BAPPLY",
                "title": "BAPPLY, 서울",
                "city": "서울",
                "address": "강남구",
                "homepage": "https://test.data.complete",
                "tag": "BAPPLY, APPLY, SEOUL",
                "apply_start": days_from_now(1),
                "apply_end": days_from_now(2),
                "event_start": days_from_now(3),
                "event_end": days_from_now(4),
                "is_remind": True,
            },
            {
                "id": "OAPPLY",
                "title": "OAPPLY, 대전",
                "city": "대전",
                "address": "중구",
                "homepage": "https://test.data.complete",
                "tag": "OAPPLY, APPLY, DAEJEON",
                "apply_start": days_from_now(-1),
                "apply_end": days_from_now(2),
                "event_start": days_from_now(3),
                "event_end": days_from_now(4),
                "is_remind": False,
            },
            {
                "id": "BEVENT",
                "title": "BEVENT, 서울",
                "city": "서울",
                "address": "강남구",
                "homepage": "https://test.data.complete",
                "tag": "BEVENT, EVENT, SEOUL",
                "apply_start": days_from_now(-2),
                "apply_end": days_from_now(-1),
                "event_start": days_from_now(3),
                "event_end": days_from_now(4),
                "is_remind": False,
            },
            {
                "id": "OEVENT",
                "title": "BEVENT, 부산",
                "city": "부산",
                "address": "해운대구",
                "homepage": "https://test.data.complete",
                "tag": "OEVENT, EVENT, BUSAN",
                "apply_start": days_from_now(-4),
                "apply_end": days_from_now(-3),
                "event_start": days_from_now(-1),
                "event_end": days_from_now(4),
                "is_remind": False,
            },
            {
                "id": "EXPIRE",
                "title": "EXPIRE, 대전",
                "city": "대전",
                "address": "중구",
                "homepage": "https://test.data.complete",
                "tag": "EXPIRE, DAEJEON",
                "apply_start": days_from_now(-5),
                "apply_end": days_from_now(-4),
                "event_start": days_from_now(-3),
                "event_end": days_from_now(-2),
                "is_remind": True,
            },
        ]
        self._DataBaseManager__db.insert_multiple(data)

    mocker.patch.object(DataBaseManager, '__init__', init)


@pytest.fixture()
def db():
    with DataBaseManager() as db:
        yield db


@pytest.mark.parametrize(
    'method, expects',
    [
        (
            'show',
            ['BAPPLY', 'OAPPLY', 'BEVENT', 'OEVENT', 'EXPIRE'],
        ),
        (
            'show_by_applicable',
            ['BAPPLY', 'OAPPLY'],
        ),
    ],
)
def test_show_with_no_param(db, method, expects):
    result = getattr(db, method)().get_string()

    for expect in expects:
        assert expect in result


@pytest.mark.parametrize(
    'method, param, expects',
    [
        (
            'show_by_id',
            'BAPPLY',
            ['BAPPLY'],
        ),
        (
            'show_by_id',
            'OAPPLY',
            ['OAPPLY'],
        ),
        (
            'show_by_title',
            'BEVENT',
            ['BEVENT'],
        ),
        (
            'show_by_title',
            '서울',
            ['BAPPLY', 'BEVENT'],
        ),
        (
            'show_by_city',
            '대전',
            ['OAPPLY'],
        ),
        (
            'show_by_city',
            '서울',
            ['BAPPLY', 'BEVENT'],
        ),
        (
            'show_by_tag',
            'EVENT',
            ['BEVENT', 'OEVENT'],
        ),
        (
            'show_by_tag',
            'SEOUL',
            ['BAPPLY', 'BEVENT'],
        ),
    ],
)
def test_show_with_single_param(db, method, param, expects):
    result = getattr(db, method)(param).get_string()

    for expect in expects:
        assert expect in result
