import re
import sys
from io import BytesIO
from binascii import unhexlify
from collections import OrderedDict
from datetime import datetime, timedelta, date
from decimal import Decimal
from email.mime.text import MIMEText
from fractions import Fraction
from uuid import UUID
try:
    from ipaddress import ip_address, ip_network
except ImportError:
    def ip_address(x): pass
    def ip_network(x, strict): pass

import pytest

from cbor2 import shareable_encoder
from cbor2.compat import timezone, pack_float16
from cbor2.types import FrozenDict


def test_fp_attr(impl):
    with pytest.raises(ValueError):
        impl.CBOREncoder(None)
    with pytest.raises(ValueError):
        class A(object):
            pass
        foo = A()
        foo.write = None
        impl.CBOREncoder(foo)
    with BytesIO() as stream:
        encoder = impl.CBOREncoder(stream)
        assert encoder.fp is stream
        with pytest.raises(AttributeError):
            del encoder.fp


def test_default_attr(impl):
    with BytesIO() as stream:
        encoder = impl.CBOREncoder(stream)
        assert encoder.default is None
        with pytest.raises(ValueError):
            encoder.default = 1
        with pytest.raises(AttributeError):
            del encoder.default


def test_timezone_attr(impl):
    with BytesIO() as stream:
        encoder = impl.CBOREncoder(stream)
        assert encoder.timezone is None
        with pytest.raises(ValueError):
            encoder.timezone = 1
        with pytest.raises(AttributeError):
            del encoder.timezone


def test_write(impl):
    with BytesIO() as stream:
        encoder = impl.CBOREncoder(stream)
        encoder.write(b'foo')
        assert stream.getvalue() == b'foo'
        with pytest.raises(TypeError):
            encoder.write(1)


def test_encoders_load_type(impl):
    with BytesIO() as stream:
        encoder = impl.CBOREncoder(stream)
        encoder._encoders[(1, 2, 3)] = lambda self, value: None
        with pytest.raises(ValueError) as exc:
            encoder.encode(object())
            assert str(exc.value).endswith(
                'invalid deferred encoder type (1, 2, 3) (must be a 2-tuple '
                "of module name and type name, e.g. ('collections', "
                "'defaultdict'))")


def test_encode_length(impl):
    # This test is purely for coverage in the C variant
    with BytesIO() as stream:
        encoder = impl.CBOREncoder(stream)
        encoder.encode_length(0, 1)
        assert stream.getvalue() == b'\x01'


def test_canonical_attr(impl):
    # Another test purely for coverage in the C variant
    with BytesIO() as stream:
        enc = impl.CBOREncoder(stream)
        assert not enc.canonical
        enc = impl.CBOREncoder(stream, canonical=True)
        assert enc.canonical


def test_dump(impl):
    with pytest.raises(TypeError):
        impl.dump()
    with pytest.raises(TypeError):
        impl.dumps()
    assert impl.dumps(obj=1) == b'\x01'
    with BytesIO() as stream:
        impl.dump(fp=stream, obj=1)
        assert stream.getvalue() == b'\x01'


@pytest.mark.parametrize('value, expected', [
    (0, '00'),
    (1, '01'),
    (10, '0a'),
    (23, '17'),
    (24, '1818'),
    (100, '1864'),
    (1000, '1903e8'),
    (1000000, '1a000f4240'),
    (1000000000000, '1b000000e8d4a51000'),
    (18446744073709551615, '1bffffffffffffffff'),
    (18446744073709551616, 'c249010000000000000000'),
    (-18446744073709551616, '3bffffffffffffffff'),
    (-18446744073709551617, 'c349010000000000000000'),
    (-1, '20'),
    (-10, '29'),
    (-100, '3863'),
    (-1000, '3903e7')
])
def test_integer(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


@pytest.mark.parametrize('value, expected', [
    (1.1, 'fb3ff199999999999a'),
    (1.0e+300, 'fb7e37e43c8800759c'),
    (-4.1, 'fbc010666666666666'),
    (float('inf'), 'f97c00'),
    (float('nan'), 'f97e00'),
    (float('-inf'), 'f9fc00')
])
def test_float(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


@pytest.mark.parametrize('value, expected', [
    (b'', '40'),
    (b'\x01\x02\x03\x04', '4401020304'),
])
def test_bytestring(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


def test_bytearray(impl):
    expected = unhexlify('4401020304')
    assert impl.dumps(bytearray(b'\x01\x02\x03\x04')) == expected


@pytest.mark.parametrize('value, expected', [
    (u'', '60'),
    (u'a', '6161'),
    (u'IETF', '6449455446'),
    (u'"\\', '62225c'),
    (u'\u00fc', '62c3bc'),
    (u'\u6c34', '63e6b0b4')
])
def test_string(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


@pytest.fixture(params=[
    (False, 'f4'),
    (True, 'f5'),
    (None, 'f6'),
    ('undefined', 'f7')
], ids=['false', 'true', 'null', 'undefined'])
def special_values(request, impl):
    value, expected = request.param
    if value == 'undefined':
        value = impl.undefined
    return value, expected


def test_special(impl, special_values):
    value, expected = special_values
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


@pytest.fixture(params=[
    (0, 'e0'),
    (2, 'e2'),
    (19, 'f3'),
    (32, 'f820')
])
def simple_values(request, impl):
    value, expected = request.param
    return impl.CBORSimpleValue(value), expected


def test_simple_value(impl, simple_values):
    value, expected = simple_values
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


#
# Tests for extension tags
#

@pytest.mark.parametrize('value, as_timestamp, expected', [
    (datetime(2013, 3, 21, 20, 4, 0, tzinfo=timezone.utc), False,
     'c074323031332d30332d32315432303a30343a30305a'),
    (datetime(2013, 3, 21, 20, 4, 0, 380841, tzinfo=timezone.utc), False,
     'c0781b323031332d30332d32315432303a30343a30302e3338303834315a'),
    (datetime(2013, 3, 21, 22, 4, 0, tzinfo=timezone(timedelta(hours=2))), False,
     'c07819323031332d30332d32315432323a30343a30302b30323a3030'),
    (datetime(2013, 3, 21, 20, 4, 0), False, 'c074323031332d30332d32315432303a30343a30305a'),
    (datetime(2013, 3, 21, 20, 4, 0, tzinfo=timezone.utc), True, 'c11a514b67b0'),
    (datetime(2013, 3, 21, 20, 4, 0, 123456, tzinfo=timezone.utc), True, 'c1fb41d452d9ec07e6b4'),
    (datetime(2013, 3, 21, 22, 4, 0, tzinfo=timezone(timedelta(hours=2))), True, 'c11a514b67b0')
], ids=[
    'datetime/utc',
    'datetime+micro/utc',
    'datetime/eet',
    'naive',
    'timestamp/utc',
    'timestamp+micro/utc',
    'timestamp/eet'
])
def test_datetime(impl, value, as_timestamp, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value, datetime_as_timestamp=as_timestamp, timezone=timezone.utc) == expected


@pytest.mark.parametrize('tz', [None, timezone.utc], ids=['no timezone', 'utc'])
def test_date_fails(impl, tz):
    encoder = impl.CBOREncoder(BytesIO(b''), timezone=tz, date_as_datetime=False)
    assert date not in encoder._encoders
    with pytest.raises(impl.CBOREncodeError) as exc:
        encoder.encode(date(2013, 3, 21))
        assert isinstance(exc, ValueError)


def test_date_as_datetime(impl):
    expected = unhexlify('c074323031332d30332d32315430303a30303a30305a')
    assert impl.dumps(date(2013, 3, 21), timezone=timezone.utc, date_as_datetime=True) == expected


def test_naive_datetime(impl):
    """Test that naive datetimes are gracefully rejected when no timezone has been set."""
    with pytest.raises(impl.CBOREncodeError) as exc:
        impl.dumps(datetime(2013, 3, 21))
        exc.match('naive datetime datetime.datetime(2013, 3, 21) encountered '
                  'and no default timezone has been set')
        assert isinstance(exc, ValueError)


@pytest.mark.parametrize('value, expected', [
    (Decimal('14.123'), 'c4822219372b'),
    (Decimal('-14.123'), 'C4822239372A'),
    (Decimal('NaN'), 'f97e00'),
    (Decimal('Infinity'), 'f97c00'),
    (Decimal('-Infinity'), 'f9fc00')
], ids=['normal', 'negative', 'nan', 'inf', 'neginf'])
def test_decimal(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


def test_rational(impl):
    expected = unhexlify('d81e820205')
    assert impl.dumps(Fraction(2, 5)) == expected


def test_regex(impl):
    expected = unhexlify('d8236d68656c6c6f2028776f726c6429')
    assert impl.dumps(re.compile(u'hello (world)')) == expected


def test_mime(impl):
    expected = unhexlify(
        'd824787b436f6e74656e742d547970653a20746578742f706c61696e3b20636861727365743d2269736f2d38'
        '3835392d3135220a4d494d452d56657273696f6e3a20312e300a436f6e74656e742d5472616e736665722d456'
        'e636f64696e673a2071756f7465642d7072696e7461626c650a0a48656c6c6f203d413475726f')
    message = MIMEText(u'Hello \u20acuro', 'plain', 'iso-8859-15')
    assert impl.dumps(message) == expected


def test_uuid(impl):
    expected = unhexlify('d825505eaffac8b51e480581277fdcc7842faf')
    assert impl.dumps(UUID(hex='5eaffac8b51e480581277fdcc7842faf')) == expected


@pytest.mark.skipif(sys.version_info < (3, 3), reason="Address encoding requires Py3.3+")
@pytest.mark.parametrize('value, expected', [
    (ip_address('192.10.10.1'), 'd9010444c00a0a01'),
    (ip_address('2001:db8:85a3::8a2e:370:7334'), 'd901045020010db885a3000000008a2e03707334'),
], ids=[
    'ipv4',
    'ipv6',
])
def test_ipaddress(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


@pytest.mark.skipif(sys.version_info < (3, 3), reason="Network encoding requires Py3.3+")
@pytest.mark.parametrize('value, expected', [
    (ip_network('192.168.0.100/24', False), 'd90105a144c0a800001818'),
    (ip_network('2001:db8:85a3:0:0:8a2e::/96', False),
     'd90105a15020010db885a3000000008a2e000000001860'),
], ids=[
    'ipv4',
    'ipv6',
])
def test_ipnetwork(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value) == expected


def test_custom_tag(impl):
    expected = unhexlify('d917706548656c6c6f')
    assert impl.dumps(impl.CBORTag(6000, u'Hello')) == expected


def test_cyclic_array(impl):
    """Test that an array that contains itself can be serialized with value sharing enabled."""
    expected = unhexlify('d81c81d81c81d81d00')
    a = [[]]
    a[0].append(a)
    assert impl.dumps(a, value_sharing=True) == expected


def test_cyclic_array_nosharing(impl):
    """Test that serializing a cyclic structure w/o value sharing will blow up gracefully."""
    a = []
    a.append(a)
    with pytest.raises(impl.CBOREncodeError) as exc:
        impl.dumps(a)
        exc.match('cyclic data structure detected but value sharing is disabled')
        assert isinstance(exc, ValueError)


def test_cyclic_map(impl):
    """Test that a dict that contains itself can be serialized with value sharing enabled."""
    expected = unhexlify('d81ca100d81d00')
    a = {}
    a[0] = a
    assert impl.dumps(a, value_sharing=True) == expected


def test_cyclic_map_nosharing(impl):
    """Test that serializing a cyclic structure w/o value sharing will fail gracefully."""
    a = {}
    a[0] = a
    with pytest.raises(impl.CBOREncodeError) as exc:
        impl.dumps(a)
        exc.match('cyclic data structure detected but value sharing is disabled')
        assert isinstance(exc, ValueError)


@pytest.mark.parametrize('value_sharing, expected', [
    (False, '828080'),
    (True, 'd81c82d81c80d81d01')
], ids=['nosharing', 'sharing'])
def test_not_cyclic_same_object(impl, value_sharing, expected):
    """Test that the same shareable object can be included twice if not in a cyclic structure."""
    expected = unhexlify(expected)
    a = []
    b = [a, a]
    assert impl.dumps(b, value_sharing=value_sharing) == expected


def test_unsupported_type(impl):
    with pytest.raises(impl.CBOREncodeError) as exc:
        impl.dumps(lambda: None)
        exc.match('cannot serialize type function')
        assert isinstance(exc, TypeError)


def test_default(impl):
    class DummyType(object):
        def __init__(self, state):
            self.state = state

    def default_encoder(encoder, value):
        encoder.encode(value.state)

    expected = unhexlify('820305')
    obj = DummyType([3, 5])
    serialized = impl.dumps(obj, default=default_encoder)
    assert serialized == expected


def test_default_cyclic(impl):
    class DummyType(object):
        def __init__(self, value=None):
            self.value = value

    @shareable_encoder
    def default_encoder(encoder, value):
        state = encoder.encode_to_bytes(value.value)
        encoder.encode(impl.CBORTag(3000, state))

    expected = unhexlify('D81CD90BB849D81CD90BB843D81D00')
    obj = DummyType()
    obj2 = DummyType(obj)
    obj.value = obj2
    serialized = impl.dumps(obj, value_sharing=True, default=default_encoder)
    assert serialized == expected


def test_dump_to_file(impl, tmpdir):
    path = tmpdir.join('testdata.cbor')
    with path.open('wb') as fp:
        impl.dump([1, 10], fp)

    assert path.read_binary() == b'\x82\x01\x0a'


@pytest.mark.parametrize('value, expected', [
    ({}, 'a0'),
    (OrderedDict([(b'a', b''), (b'b', b'')]), 'A2416140416240'),
    (OrderedDict([(b'b', b''), (b'a', b'')]), 'A2416140416240'),
    (OrderedDict([(u'a', u''), (u'b', u'')]), 'a2616160616260'),
    (OrderedDict([(u'b', u''), (u'a', u'')]), 'a2616160616260'),
    (OrderedDict([(b'00001', u''), (b'002', u'')]), 'A2433030326045303030303160'),
    (OrderedDict([(255, 0), (2, 0)]), 'a2020018ff00'),
    (FrozenDict([(b'a', b''), (b'b', b'')]), 'A2416140416240')
], ids=['empty', 'bytes in order', 'bytes out of order', 'text in order',
        'text out of order', 'byte length', 'integer keys', 'frozendict'])
def test_ordered_map(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value, canonical=True) == expected


@pytest.mark.parametrize('value, expected', [
    (3.5, 'F94300'),
    (100000.0, 'FA47C35000'),
    (3.8, 'FB400E666666666666'),
    (float('inf'), 'f97c00'),
    (float('nan'), 'f97e00'),
    (float('-inf'), 'f9fc00'),
    (float.fromhex('0x1.0p-24'), 'f90001'),
    (float.fromhex('0x1.4p-24'), 'fa33a00000'),
    (float.fromhex('0x1.ff8p-63'), 'fa207fc000'),
    (1e300, 'fb7e37e43c8800759c')
], ids=['float 16', 'float 32', 'float 64', 'inf', 'nan', '-inf',
        'float 16 minimum positive subnormal', 'mantissa o/f to 32',
        'exponent o/f to 32', 'oversize float'])
def test_minimal_floats(impl, value, expected):
    expected = unhexlify(expected)
    assert impl.dumps(value, canonical=True) == expected


def test_tuple_key(impl):
    assert impl.dumps({(2, 1): u''}) == unhexlify('a182020160')


def test_dict_key(impl):
    assert impl.dumps({FrozenDict({2: 1}): u''}) == unhexlify('a1a1020160')


@pytest.mark.parametrize('frozen', [False, True], ids=['set', 'frozenset'])
def test_set(impl, frozen):
    value = {u'a', u'b', u'c'}
    if frozen:
        value = frozenset(value)

    serialized = impl.dumps(value)
    assert len(serialized) == 10
    assert serialized.startswith(unhexlify('d9010283'))


@pytest.mark.parametrize('frozen', [False, True], ids=['set', 'frozenset'])
def test_canonical_set(impl, frozen):
    value = {u'y', u'x', u'aa', u'a'}
    if frozen:
        value = frozenset(value)

    serialized = impl.dumps(value, canonical=True)
    assert serialized == unhexlify('d9010284616161786179626161')


@pytest.mark.skipif(sys.version_info >= (3, 6), reason="Using native struct.pack")
@pytest.mark.parametrize('value, expected', [
    (3.5, 'F94300'),
    (100000.0,  False),
    (3.8, False),
    (float.fromhex('0x1.0p-24'), 'f90001'),
    (float.fromhex('0x1.4p-24'), False),
    (float.fromhex('0x1.ff8p-63'), False),
    (1e300, False)
], ids=['float 16', 'float 32', 'float 64',
        'float 16 minimum positive subnormal', 'mantissa o/f to 32',
        'exponent o/f to 32', 'oversize float'])
def test_float16_encoder(value, expected):
    if expected:
        expected = unhexlify(expected)
        assert pack_float16(value) == expected
    else:
        assert not pack_float16(value)
