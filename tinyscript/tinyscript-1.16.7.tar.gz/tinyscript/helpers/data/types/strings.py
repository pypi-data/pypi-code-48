# -*- coding: UTF-8 -*-
"""String-related checking functions and argument types.

"""
import ast
import re
from six import string_types
from string import ascii_lowercase as LC, ascii_uppercase as UC, \
                   ascii_letters as letters, digits, printable, punctuation


__all__ = __features__ = []


def _str2list(s):
    """ Convert string to list if input is effectively a string. """
    # if already a list, simply return it, otherwise ensure input is a string
    if isinstance(s, list):
        return s
    else:
        s = str(s)
    # remove heading and trailing brackets
    if s[0] == '[' and s[-1] == ']' or s[0] == '(' and s[-1] == ')':
        s = s[1:-1]
    # then parse list elements from the string
    l = []
    for i in s.split(","):
        i = i.strip()
        try:
            l.append(ast.literal_eval(i))
        except Exception:
            l.append(i)
    return l


def _is_from_alph(s, a, t):
    if is_str(s):
        val = str_contains(a, t)
        try:
            val(s)
            return True
        except ValueError:
            pass
    return False


# various string-related check functions
__all__ += ["is_str", "is_digits", "is_letters", "is_lowercase", "is_printable",
            "is_punctuation", "is_uppercase"]
is_str         = lambda s: isinstance(s, string_types)
is_digits      = lambda s, t=1.0: _is_from_alph(s, digits, t)
is_letters     = lambda s, t=1.0: _is_from_alph(s, letters, t)
is_lowercase   = lambda s, t=1.0: _is_from_alph(s, LC, t)
is_printable   = lambda s, t=1.0: _is_from_alph(s, printable, t)
is_punctuation = lambda s, t=1.0: _is_from_alph(s, punctuation, t)
is_uppercase   = lambda s, t=1.0: _is_from_alph(s, UC, t)

# various data format check functions
__all__ += ["is_bin", "is_hex"]
is_bin = lambda b: is_str(b) and all(set(_).difference(set("01")) == set() \
                                     for _ in re.split(r"\W+", b))
is_hex = lambda h: is_str(h) and len(h) % 2 == 0 and \
                   set(h.lower()).difference(set("0123456789abcdef")) == set()

# some other common check functions
__all__ += ["is_long_opt", "is_short_opt"]
is_long_opt  = lambda o: is_str(o) and \
                         re.match(r"^--[a-z]+(-[a-z]+)*$", o, re.I)
is_short_opt = lambda o: is_str(o) and re.match(r"^-[a-z]$", o, re.I)


# -------------------- STRING FORMAT ARGUMENT TYPES --------------------
__all__ += ["str_contains", "str_matches"]


def str_contains(alphabet, threshold=1.0):
    """ Counts the characters of a string and determines, given an alphabet, if
         the string has enough valid characters. """
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("Bad threshold (should be between 0 and 1)")
    def _validation(s):
        p = sum(int(c in alphabet) for c in s) / float(len(s))
        if p < threshold:
            raise ValueError("Input string does not contain enough items from "
                             "the given alphabet ({:.2f}%)".format(p * 100))
        return s
    return _validation


def str_matches(pattern, flags=0):
    """ Applies the given regular expression to a string argument. """
    def _validation(s):
        if re.match(pattern, s, flags) is None:
            raise ValueError("Input string does not match the given regex")
        return s
    return _validation
