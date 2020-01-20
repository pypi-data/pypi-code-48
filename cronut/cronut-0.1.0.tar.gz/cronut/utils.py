#!/usr/bin/env python

__author__ = "Patrick Godwin (patrick.godwin@ligo.org)"
__description__ = "a module to store commonly used utilities"

#-------------------------------------------------
### imports

from collections import namedtuple
import random
import string
import sys

if sys.version_info >= (3, ):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


#-------------------------------------------------
### kafka utilities

KafkaURI = namedtuple('KafkaURI', 'groupid broker topics')

def uriparse(uri):
    """Parses a Kafka URI of the form:

       kafka://[groupid@]broker[,broker2[,...]]/topicspec[,topicspec[,...]]

    and returns a namedtuple to access properties by name:

        uri.groupid
        uri.broker
        uri.topics

    """
    uri = urlparse(uri)
    assert uri.scheme == 'kafka'

    if uri.username:
        groupid, broker = uri.netloc.split('@')
    else:
        groupid, broker = None, uri.netloc

    topics = uri.path.lstrip('/')
    if topics:
        topics = topics.split(',')
    else:
        topics = []

    return KafkaURI(groupid, broker, topics)


def generate_groupid(app_name):
    """Generate a random Kafka group id

    """
    return '-'.join((app_name, random_alphanum(10)))


def random_alphanum(n):
    """Generate a random alpha-numeric sequence of N characters.

    """
    alphanum = string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(alphanum) for _ in range(n))
