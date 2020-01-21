# -*- coding: utf-8 -*-
try:
    from DocumentTemplate import DT_Var
except ImportError:
    DT_Var = None
try:
    # PythonScripts does "from DocumentTemplate.DT_Var import sql_quote"
    # so we should patch this too.
    from Products.PythonScripts import standard
except ImportError:
    standard = None
try:
    from Shared.DC.ZRDB.Connection import Connection
except ImportError:
    Connection = None


# Note: DT_Var has this function signature:
# def sql_quote(v, name='(Unknown name)', md={}):
# and the Connection class has this method signature:
# def sql_quote__(self, v):
# So they are slightly different, but in both cases only 'v' is actually used.

# Searching and replacing a byte in text, or text in bytes,
# may give various errors on Python 2 or 3.  So we make separate functions
UNTRUSTED_BYTES = (b"'", b'"', b"\\")
UNTRUSTED_TEXT = (u"'", u'"', u"\\")
BAD_BYTES = (b"\x00",)
BAD_TEXT = (u"\x00",)


def bytes_sql_quote(v):
    # Remove bad characters.
    for char in BAD_BYTES:
        if char in v:
            v = v.replace(char, b"")
    # Double untrusted characters to make them harmless.
    for char in UNTRUSTED_BYTES:
        if char in v:
            v = v.replace(char, char * 2)
    return v


def text_sql_quote(v):
    # Remove bad characters.
    for char in BAD_TEXT:
        if char in v:
            v = v.replace(char, u"")
    # Double untrusted characters to make them harmless.
    for char in UNTRUSTED_TEXT:
        if char in v:
            v = v.replace(char, char * 2)
    return v


def dtml_sql_quote(v, *args, **kwargs):
    """Quote single quotes in a string by doubling them.

    Do the same for double quotes and and backslashes.
    Remove nul-strings.

    This is needed to securely insert values into sql
    string literals in templates that generate sql.
    """
    if isinstance(v, bytes):
        return bytes_sql_quote(v)
    return text_sql_quote(v)


def connection_sql_quote(self, v):
    # As extra, the Connection puts single quotes around the entire value.
    if isinstance(v, bytes):
        return b"'%s'" % bytes_sql_quote(v)
    return u"'%s'" % text_sql_quote(v)


if DT_Var is not None:
    DT_Var.sql_quote = dtml_sql_quote
    # sql-quote is a deprecated alias for sql_quote
    if "sql-quote" in DT_Var.special_formats:
        DT_Var.special_formats["sql-quote"] = dtml_sql_quote
    for index, (name, function) in enumerate(DT_Var.modifiers):
        if name == "sql_quote":
            DT_Var.modifiers[index] = (name, dtml_sql_quote)
            break

if standard is not None:
    standard.sql_quote = dtml_sql_quote
if Connection is not None:
    Connection.sql_quote__ = connection_sql_quote
