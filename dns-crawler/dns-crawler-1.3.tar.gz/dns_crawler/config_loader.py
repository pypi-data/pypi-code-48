# Copyright © 2019 CZ.NIC, z. s. p. o.
#
# This file is part of dns-crawler.
#
# dns-crawler is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License. If not,
# see <http://www.gnu.org/licenses/>.

import sys
from os import getcwd, path

import yaml

from .timestamp import timestamp

defaults = {
    "geoip": {
        "country": "/usr/share/GeoIP/GeoLite2-Country.mmdb",
        "asn": "/usr/share/GeoIP/GeoLite2-ASN.mmdb"
    },
    "resolvers": [
        "193.17.47.1"
    ],
    "timeouts": {
        "job": 80,
        "dns": 2,
        "http": 2,
        "mail": 2
    },
    "web": {
        "save_content": False,
        "strip_html": True,
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "accept_language": "en-US;q=0.9,en;q=0.8"
    }
}


def merge_dicts(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_dicts(value, node)
        else:
            if isinstance(value, str):
                if value.isdigit():
                    destination[key] = int(value)
                elif value == "False":
                    destination[key] = False
                elif value == "True":
                    destination[key] = True
                else:
                    destination[key] = value
            else:
                destination[key] = value
    return destination


def load_config(filename):
    pwd = getcwd()
    try:
        with open(path.join(pwd, filename), "r") as conf_file:
            config_from_file = yaml.load(conf_file, Loader=yaml.BaseLoader)
            if "http_timeout" in config_from_file or \
               "dns_timeout" in config_from_file or \
               "save_web_content" in config_from_file:
                sys.stderr.write(f"{timestamp()} Incompatible config file loaded (the format" +
                                 "changed with v1.2, see README). Using defaults instead.\n")
                config = defaults
            else:
                config = merge_dicts(config_from_file, defaults)
    except FileNotFoundError:
        config = defaults
    return config
