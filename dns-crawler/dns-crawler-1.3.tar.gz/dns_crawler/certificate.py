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

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from .utils import drop_null_values


def cert_datetime_to_iso(cert_date):
    return cert_date.strftime("%Y-%m-%d %H:%M:%S")


def parse_cert_name(cert, field):
    try:
        name = getattr(cert, field)
        return {k: v for k, v in [s.rfc4514_string().split("=", 1) for s in name.rdns]}
    except ValueError as e:
        return {"error": str(e)}


def format_cert_serial_number(serial):
    return f"{serial:016x}"


def parse_cert(cert, domain):
    cert = x509.load_der_x509_certificate(cert, default_backend())
    result = {}
    result["not_before"] = cert_datetime_to_iso(cert.not_valid_before)
    result["not_after"] = cert_datetime_to_iso(cert.not_valid_after)
    result["subject"] = parse_cert_name(cert, "subject")
    result["issuer"] = parse_cert_name(cert, "issuer")
    result["version"] = int(str(cert.version)[-1])
    result["serial"] = format_cert_serial_number(cert.serial_number)
    result["algorithm"] = cert.signature_hash_algorithm.name
    try:
        result["alt_names"] = [str(name.value) for name in cert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value]
    except (x509.extensions.ExtensionNotFound, ValueError):
        pass
    return drop_null_values(result)
