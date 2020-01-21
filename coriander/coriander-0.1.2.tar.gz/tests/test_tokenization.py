from coriander import StrToken, AnyToken, tokenize


def test_eq_str_tokens():
    token1 = StrToken(value="asd")
    token2 = StrToken(value="asd")

    assert token1 == token2


def test_eq_any_tokens():
    token1 = AnyToken()
    token2 = AnyToken()

    assert token1 == token2


def test_repr_str_token():
    token = StrToken(value="asd")

    assert repr(token) == "StrToken(value='asd')"


def test_repr_any_token():
    token = AnyToken()

    assert repr(token) == "AnyToken()"


def test_str__token_tokenize():
    template = "asd"
    tokens = tokenize(template)

    assert tokens == [StrToken(value="asd")]


def test_any__token_tokenize():
    template = "*"
    tokens = tokenize(template)

    assert tokens == [AnyToken()]
