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

from os import path, getcwd

import geoip2.database

from .ip_utils import is_valid_ip_address


def init_geoip(config):
    pwd = getcwd()
    geoip_country = None
    geoip_isp = None
    geoip_asn = None

    if "country" in config["geoip"]:
        geoip_country = geoip2.database.Reader(path.join(pwd, config["geoip"]["country"]))

    if "isp" in config["geoip"]:
        geoip_isp = geoip2.database.Reader(path.join(pwd, config["geoip"]["isp"]))

    if "asn" in config["geoip"] and not ("isp" in config["geoip"]):
        geoip_asn = geoip2.database.Reader(path.join(pwd, config["geoip"]["asn"]))

    return (geoip_country, geoip_isp, geoip_asn)


def annotate_geoip(items, key, dbs):
    geoip_country, geoip_isp, geoip_asn = dbs
    if items:
        for item in items:
            ip = item[key]
            if not is_valid_ip_address(ip):
                continue
            try:
                result = {}
                if geoip_country:
                    country = geoip_country.country(ip).country
                    result["country"] = country.iso_code
                if geoip_isp:
                    isp = geoip_isp.isp(ip)
                if geoip_asn and not geoip_isp:
                    isp = geoip_asn.asn(ip)
                if geoip_asn or geoip_isp:
                    result["org"] = isp.autonomous_system_organization
                    result["asn"] = isp.autonomous_system_number
            except Exception as e:
                result["error"] = str(e)
            item["geoip"] = result
    return items
