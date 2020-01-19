# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http:// and https:// URLs"""

import time
import mimetypes
from requests.exceptions import RequestException, ConnectionError, Timeout
from .common import DownloaderBase
from .. import text, util

from ssl import SSLError
try:
    from OpenSSL.SSL import Error as OpenSSLError
except ImportError:
    OpenSSLError = SSLError


class HttpDownloader(DownloaderBase):
    scheme = "http"

    def __init__(self, extractor, output):
        DownloaderBase.__init__(self, extractor, output)
        self.adjust_extension = self.config("adjust-extensions", True)
        self.retries = self.config("retries", extractor._retries)
        self.timeout = self.config("timeout", extractor._timeout)
        self.verify = self.config("verify", extractor._verify)
        self.mtime = self.config("mtime", True)
        self.rate = self.config("rate")
        self.downloading = False
        self.chunk_size = 16384

        if self.retries < 0:
            self.retries = float("inf")
        if self.rate:
            rate = text.parse_bytes(self.rate)
            if rate:
                if rate < self.chunk_size:
                    self.chunk_size = rate
                self.rate = rate
                self.receive = self._receive_rate
            else:
                self.log.warning("Invalid rate limit (%r)", self.rate)

    def download(self, url, pathfmt):
        try:
            return self._download_impl(url, pathfmt)
        except Exception:
            print()
            raise
        finally:
            # remove file from incomplete downloads
            if self.downloading and not self.part:
                util.remove_file(pathfmt.temppath)

    def _download_impl(self, url, pathfmt):
        response = None
        tries = 0
        msg = ""

        if self.part:
            pathfmt.part_enable(self.partdir)

        while True:
            if tries:
                if response:
                    response.close()
                self.log.warning("%s (%s/%s)", msg, tries, self.retries+1)
                if tries > self.retries:
                    return False
                time.sleep(min(2 ** (tries-1), 1800))
            tries += 1

            headers = {}
            # check for .part file
            filesize = pathfmt.part_size()
            if filesize:
                headers["Range"] = "bytes={}-".format(filesize)
            # file-specific headers
            extra = pathfmt.kwdict.get("_http_headers")
            if extra:
                headers.update(extra)

            # connect to (remote) source
            try:
                response = self.session.request(
                    "GET", url, stream=True, headers=headers,
                    timeout=self.timeout, verify=self.verify)
            except (ConnectionError, Timeout) as exc:
                msg = str(exc)
                continue
            except Exception as exc:
                self.log.warning(exc)
                return False

            # check response
            code = response.status_code
            if code == 200:  # OK
                offset = 0
                size = response.headers.get("Content-Length")
            elif code == 206:  # Partial Content
                offset = filesize
                size = response.headers["Content-Range"].rpartition("/")[2]
            elif code == 416 and filesize:  # Requested Range Not Satisfiable
                break
            else:
                msg = "'{} {}' for '{}'".format(code, response.reason, url)
                if code == 429 or 500 <= code < 600:  # Server Error
                    continue
                self.log.warning(msg)
                return False
            size = text.parse_int(size)

            # set missing filename extension
            if not pathfmt.extension:
                pathfmt.set_extension(self.get_extension(response))
                if pathfmt.exists():
                    pathfmt.temppath = ""
                    return True

            # set open mode
            if not offset:
                mode = "w+b"
                if filesize:
                    self.log.debug("Unable to resume partial download")
            else:
                mode = "r+b"
                self.log.debug("Resuming download at byte %d", offset)

            # start downloading
            self.out.start(pathfmt.path)
            self.downloading = True
            with pathfmt.open(mode) as file:
                if offset:
                    file.seek(offset)

                # download content
                try:
                    self.receive(response, file)
                except (RequestException, SSLError, OpenSSLError) as exc:
                    msg = str(exc)
                    print()
                    continue

                # check filesize
                if size and file.tell() < size:
                    msg = "filesize mismatch ({} < {})".format(
                        file.tell(), size)
                    print()
                    continue

                # check filename extension
                if self.adjust_extension:
                    adj_ext = self.check_extension(file, pathfmt.extension)
                    if adj_ext:
                        pathfmt.set_extension(adj_ext)

            break

        self.downloading = False
        if self.mtime:
            pathfmt.kwdict["_mtime"] = response.headers.get("Last-Modified")
        return True

    def receive(self, response, file):
        for data in response.iter_content(self.chunk_size):
            file.write(data)

    def _receive_rate(self, response, file):
        t1 = time.time()
        rt = self.rate

        for data in response.iter_content(self.chunk_size):
            file.write(data)

            t2 = time.time()           # current time
            actual = t2 - t1           # actual elapsed time
            expected = len(data) / rt  # expected elapsed time

            if actual < expected:
                # sleep if less time elapsed than expected
                time.sleep(expected - actual)
                t1 = time.time()
            else:
                t1 = t2

    def get_extension(self, response):
        mtype = response.headers.get("Content-Type", "image/jpeg")
        mtype = mtype.partition(";")[0]

        if mtype in MIMETYPE_MAP:
            return MIMETYPE_MAP[mtype]

        exts = mimetypes.guess_all_extensions(mtype, strict=False)
        if exts:
            exts.sort()
            return exts[-1][1:]

        self.log.warning(
            "No filename extension found for MIME type '%s'", mtype)
        return "txt"

    @staticmethod
    def check_extension(file, extension):
        """Check filename extension against fileheader"""
        if extension in FILETYPE_CHECK:
            file.seek(0)
            header = file.read(8)
            if len(header) >= 8 and not FILETYPE_CHECK[extension](header):
                for ext, check in FILETYPE_CHECK.items():
                    if ext != extension and check(header):
                        return ext
        return None


FILETYPE_CHECK = {
    "jpg": lambda h: h[0:2] == b"\xff\xd8",
    "png": lambda h: h[0:8] == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a",
    "gif": lambda h: h[0:4] == b"GIF8" and h[5] == 97,
}


MIMETYPE_MAP = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/webp": "webp",
    "image/svg+xml": "svg",

    "video/webm": "webm",
    "video/ogg": "ogg",
    "video/mp4": "mp4",

    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",

    "application/zip": "zip",
    "application/x-zip": "zip",
    "application/x-zip-compressed": "zip",
    "application/x-rar": "rar",
    "application/x-rar-compressed": "rar",
    "application/x-7z-compressed": "7z",

    "application/ogg": "ogg",
    "application/octet-stream": "bin",
}


__downloader__ = HttpDownloader
