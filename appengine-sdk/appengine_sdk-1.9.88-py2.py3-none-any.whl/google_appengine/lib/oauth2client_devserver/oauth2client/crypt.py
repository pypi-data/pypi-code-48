# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Crypto-related routines for oauth2client."""

import base64
import json
import logging
import time


CLOCK_SKEW_SECS = 300  # 5 minutes in seconds
AUTH_TOKEN_LIFETIME_SECS = 300  # 5 minutes in seconds
MAX_TOKEN_LIFETIME_SECS = 86400  # 1 day in seconds


logger = logging.getLogger(__name__)


class AppIdentityError(Exception):
  pass


try:
  from OpenSSL import crypto

  class OpenSSLVerifier(object):
    """Verifies the signature on a message."""

    def __init__(self, pubkey):
      """Constructor.

      Args:
        pubkey, OpenSSL.crypto.PKey, The public key to verify with.
      """
      self._pubkey = pubkey

    def verify(self, message, signature):
      """Verifies a message against a signature.

      Args:
        message: string, The message to verify.
        signature: string, The signature on the message.

      Returns:
        True if message was signed by the private key associated with the public
        key that this object was constructed with.
      """
      try:
        crypto.verify(self._pubkey, signature, message, 'sha256')
        return True
      except:
        return False

    @staticmethod
    def from_string(key_pem, is_x509_cert):
      """Construct a Verified instance from a string.

      Args:
        key_pem: string, public key in PEM format.
        is_x509_cert: bool, True if key_pem is an X509 cert, otherwise it is
          expected to be an RSA key in PEM format.

      Returns:
        Verifier instance.

      Raises:
        OpenSSL.crypto.Error if the key_pem can't be parsed.
      """
      if is_x509_cert:
        pubkey = crypto.load_certificate(crypto.FILETYPE_PEM, key_pem)
      else:
        pubkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key_pem)
      return OpenSSLVerifier(pubkey)


  class OpenSSLSigner(object):
    """Signs messages with a private key."""

    def __init__(self, pkey):
      """Constructor.

      Args:
        pkey, OpenSSL.crypto.PKey (or equiv), The private key to sign with.
      """
      self._key = pkey

    def sign(self, message):
      """Signs a message.

      Args:
        message: string, Message to be signed.

      Returns:
        string, The signature of the message for the given key.
      """
      return crypto.sign(self._key, message, 'sha256')

    @staticmethod
    def from_string(key, password='notasecret'):
      """Construct a Signer instance from a string.

      Args:
        key: string, private key in PKCS12 or PEM format.
        password: string, password for the private key file.

      Returns:
        Signer instance.

      Raises:
        OpenSSL.crypto.Error if the key can't be parsed.
      """
      parsed_pem_key = _parse_pem_key(key)
      if parsed_pem_key:
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, parsed_pem_key)
      else:
        pkey = crypto.load_pkcs12(key, password.encode('utf8')).get_privatekey()
      return OpenSSLSigner(pkey)

except ImportError:
  OpenSSLVerifier = None
  OpenSSLSigner = None


try:
  from Crypto.PublicKey import RSA
  from Crypto.Hash import SHA256
  from Crypto.Signature import PKCS1_v1_5
  from Crypto.Util.asn1 import DerSequence


  class PyCryptoVerifier(object):
    """Verifies the signature on a message."""

    def __init__(self, pubkey):
      """Constructor.

      Args:
        pubkey, OpenSSL.crypto.PKey (or equiv), The public key to verify with.
      """
      self._pubkey = pubkey

    def verify(self, message, signature):
      """Verifies a message against a signature.

      Args:
        message: string, The message to verify.
        signature: string, The signature on the message.

      Returns:
        True if message was signed by the private key associated with the public
        key that this object was constructed with.
      """
      try:
        return PKCS1_v1_5.new(self._pubkey).verify(
            SHA256.new(message), signature)
      except:
        return False

    @staticmethod
    def from_string(key_pem, is_x509_cert):
      """Construct a Verified instance from a string.

      Args:
        key_pem: string, public key in PEM format.
        is_x509_cert: bool, True if key_pem is an X509 cert, otherwise it is
          expected to be an RSA key in PEM format.

      Returns:
        Verifier instance.
      """
      if is_x509_cert:
        pemLines = key_pem.replace(' ', '').split()
        certDer = _urlsafe_b64decode(''.join(pemLines[1:-1]))
        certSeq = DerSequence()
        certSeq.decode(certDer)
        tbsSeq = DerSequence()
        tbsSeq.decode(certSeq[0])
        pubkey = RSA.importKey(tbsSeq[6])
      else:
        pubkey = RSA.importKey(key_pem)
      return PyCryptoVerifier(pubkey)


  class PyCryptoSigner(object):
    """Signs messages with a private key."""

    def __init__(self, pkey):
      """Constructor.

      Args:
        pkey, OpenSSL.crypto.PKey (or equiv), The private key to sign with.
      """
      self._key = pkey

    def sign(self, message):
      """Signs a message.

      Args:
        message: string, Message to be signed.

      Returns:
        string, The signature of the message for the given key.
      """
      return PKCS1_v1_5.new(self._key).sign(SHA256.new(message))

    @staticmethod
    def from_string(key, password='notasecret'):
      """Construct a Signer instance from a string.

      Args:
        key: string, private key in PEM format.
        password: string, password for private key file. Unused for PEM files.

      Returns:
        Signer instance.

      Raises:
        NotImplementedError if they key isn't in PEM format.
      """
      parsed_pem_key = _parse_pem_key(key)
      if parsed_pem_key:
        pkey = RSA.importKey(parsed_pem_key)
      else:
        raise NotImplementedError(
            'PKCS12 format is not supported by the PyCrypto library. '
            'Try converting to a "PEM" '
            '(openssl pkcs12 -in xxxxx.p12 -nodes -nocerts > privatekey.pem) '
            'or using PyOpenSSL if native code is an option.')
      return PyCryptoSigner(pkey)

except ImportError:
  PyCryptoVerifier = None
  PyCryptoSigner = None


if OpenSSLSigner:
  Signer = OpenSSLSigner
  Verifier = OpenSSLVerifier
elif PyCryptoSigner:
  Signer = PyCryptoSigner
  Verifier = PyCryptoVerifier
else:
  raise ImportError('No encryption library found. Please install either '
                    'PyOpenSSL, or PyCrypto 2.6 or later')


def _parse_pem_key(raw_key_input):
  """Identify and extract PEM keys.

  Determines whether the given key is in the format of PEM key, and extracts
  the relevant part of the key if it is.

  Args:
    raw_key_input: The contents of a private key file (either PEM or PKCS12).

  Returns:
    string, The actual key if the contents are from a PEM file, or else None.
  """
  offset = raw_key_input.find('-----BEGIN ')
  if offset != -1:
    return raw_key_input[offset:]


def _urlsafe_b64encode(raw_bytes):
  return base64.urlsafe_b64encode(raw_bytes).rstrip('=')


def _urlsafe_b64decode(b64string):
  # Guard against unicode strings, which base64 can't handle.
  b64string = b64string.encode('ascii')
  padded = b64string + '=' * (4 - len(b64string) % 4)
  return base64.urlsafe_b64decode(padded)


def _json_encode(data):
  return json.dumps(data, separators=(',', ':'))


def make_signed_jwt(signer, payload):
  """Make a signed JWT.

  See http://self-issued.info/docs/draft-jones-json-web-token.html.

  Args:
    signer: crypt.Signer, Cryptographic signer.
    payload: dict, Dictionary of data to convert to JSON and then sign.

  Returns:
    string, The JWT for the payload.
  """
  header = {'typ': 'JWT', 'alg': 'RS256'}

  segments = [
      _urlsafe_b64encode(_json_encode(header)),
      _urlsafe_b64encode(_json_encode(payload)),
  ]
  signing_input = '.'.join(segments)

  signature = signer.sign(signing_input)
  segments.append(_urlsafe_b64encode(signature))

  logger.debug(str(segments))

  return '.'.join(segments)


def verify_signed_jwt_with_certs(jwt, certs, audience):
  """Verify a JWT against public certs.

  See http://self-issued.info/docs/draft-jones-json-web-token.html.

  Args:
    jwt: string, A JWT.
    certs: dict, Dictionary where values of public keys in PEM format.
    audience: string, The audience, 'aud', that this JWT should contain. If
      None then the JWT's 'aud' parameter is not verified.

  Returns:
    dict, The deserialized JSON payload in the JWT.

  Raises:
    AppIdentityError if any checks are failed.
  """
  segments = jwt.split('.')

  if len(segments) != 3:
    raise AppIdentityError('Wrong number of segments in token: %s' % jwt)
  signed = '%s.%s' % (segments[0], segments[1])

  signature = _urlsafe_b64decode(segments[2])

  # Parse token.
  json_body = _urlsafe_b64decode(segments[1])
  try:
    parsed = json.loads(json_body)
  except:
    raise AppIdentityError('Can\'t parse token: %s' % json_body)

  # Check signature.
  verified = False
  for _, pem in certs.items():
    verifier = Verifier.from_string(pem, True)
    if verifier.verify(signed, signature):
      verified = True
      break
  if not verified:
    raise AppIdentityError('Invalid token signature: %s' % jwt)

  # Check creation timestamp.
  iat = parsed.get('iat')
  if iat is None:
    raise AppIdentityError('No iat field in token: %s' % json_body)
  earliest = iat - CLOCK_SKEW_SECS

  # Check expiration timestamp.
  now = long(time.time())
  exp = parsed.get('exp')
  if exp is None:
    raise AppIdentityError('No exp field in token: %s' % json_body)
  if exp >= now + MAX_TOKEN_LIFETIME_SECS:
    raise AppIdentityError('exp field too far in future: %s' % json_body)
  latest = exp + CLOCK_SKEW_SECS

  if now < earliest:
    raise AppIdentityError('Token used too early, %d < %d: %s' %
                           (now, earliest, json_body))
  if now > latest:
    raise AppIdentityError('Token used too late, %d > %d: %s' %
                           (now, latest, json_body))

  # Check audience.
  if audience is not None:
    aud = parsed.get('aud')
    if aud is None:
      raise AppIdentityError('No aud field in token: %s' % json_body)
    if aud != audience:
      raise AppIdentityError('Wrong recipient, %s != %s: %s' %
                             (aud, audience, json_body))

  return parsed
