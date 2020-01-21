from abc import ABC
from typing import List


class Token(ABC):
    pass


class StrToken(Token):
    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.value == self.value

    def __repr__(self):
        return f"{self.__class__.__name__}(value='{self.value}')"


class AnyToken(Token):
    SIGN = "*"

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


def tokenize(template: str) -> List[Token]:
    if template == AnyToken.SIGN:
        return [AnyToken()]
    return [StrToken(value=template)]
