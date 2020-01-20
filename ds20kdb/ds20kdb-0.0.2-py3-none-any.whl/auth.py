"""
Module to handle authentication credentials.
"""


from stat import S_IRGRP as READ_GRP, S_IROTH as READ_OTH
from os import stat, getenv, umask
from sys import stderr
from getpass import getpass
from requests import get as http_get
from requests.auth import HTTPBasicAuth as HBA
from ds20kdb.default import *


__all__ = ('authenticate', 'auth_store', 'get_auth', 'NetrcParseError', 'AuthError')


AUTH = None


class AuthError(Exception):
    """Exception class for authenticate error."""

    def __init__(self, endpoint):
        super(AuthError).__init__(f"Unable to authenticate at {endpoint}")


def authenticate(endpoint=DEFAULT_DB_ENDPOINT):
    global AUTH
    print("Authenticate yourself with your DB credentials")
    try:
        user = getpass(prompt='Username: ')
        password = getpass(prompt='Password: ')

        AUTH = HBA(user, password)

        if http_get(f"{endpoint}/api", auth=AUTH).status_code == 401:
            raise AuthError(endpoint)
    except AuthError as exception:
        print(exception, file=stderr)
        AUTH = None
    finally:
        try:
            del password, user
        except:
            pass


def auth_store(endpoint=DEFAULT_DB_ENDPOINT):
    global AUTH

    if not AUTH:
        authenticate()

    if not AUTH:
        return

    try:
        oldmask = umask(0o77)
        with open(getenv("HOME") + "/.netrc", "a") as netrc:
            print(f"machine {endpoint} login {AUTH.username} password {AUTH.password}", file=netrc)
    finally:
        umask(oldmask)


def get_auth():
    global AUTH
    return AUTH
