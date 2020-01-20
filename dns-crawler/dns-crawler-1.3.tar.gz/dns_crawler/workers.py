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

import subprocess
import sys
from multiprocessing import cpu_count
from os.path import basename
from socket import gethostname
from time import sleep

from redis import Redis

from .redis_utils import get_redis_host
from .timestamp import timestamp


def print_help():
    exe = basename(sys.argv[0])
    sys.stderr.write(f"{exe} - a process that spawns crawler workers.\n\n")
    sys.stderr.write(f"Usage: {exe} [count] [redis]\n")
    sys.stderr.write(f"       count - worker count, 8 workers per CPU core by default\n")
    sys.stderr.write(f"       redis - redis host:port:db, localhost:6379:0 by default\n\n")
    sys.stderr.write(f"Examples: {exe} 8\n")
    sys.stderr.write(f"          {exe} 24 192.168.0.22:4444:0\n")
    sys.stderr.write(f"          {exe} 16 redis.foo.bar:7777:2\n")
    sys.stderr.write(f"          {exe} 16 redis.foo.bar # port 6379 and DB 0 will be used if not specified\n")
    sys.exit(1)


def main():
    cpus = cpu_count()
    worker_count = cpus * 8
    hostname = gethostname()
    if "-h" in sys.argv or "--help" in sys.argv:
        print_help()

    try:
        worker_count = int(sys.argv[1])
    except ValueError:
        sys.stderr.write(f"Worker count ('{sys.argv[1]}') is not an integer.\n\n")
        print_help()
    except IndexError:
        pass
    if worker_count <= 0:
        sys.stderr.write(f"At least one worker is needed.\n\n")
        print_help()
    if worker_count > 24 * cpus:
        sys.stderr.write((
            f"Whoa. You are trying to run {worker_count} workers on {cpus} CPU "
            f"core{('s' if cpus > 1 else '')}. It's easy to scale \n"
            f"across multiple machines, if you need to. See README.md for details.\n\n"
            f"Cancel now (Ctrl-C) or have a fire extinguisher ready.\n"
        ))
        try:
            for s in reversed(range(0, 5)):
                sleep(1)
                sys.stdout.write(f"{str(s+1)} - ")
                sys.stdout.flush()
                if s == 0:
                    sleep(1)
                    sys.stdout.write("ignition\n\n")
        except KeyboardInterrupt:
            sys.exit(1)

    try:
        redis_host = get_redis_host(sys.argv, 2)
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)
    redis = Redis(host=redis_host[0], port=redis_host[1], db=redis_host[2])

    commands = []

    for n in range(worker_count):
        commands.append(["dns-crawler-worker",
                         redis_host[0],
                         str(redis_host[1]),
                         str(redis_host[2]),
                         f"{hostname}-{n+1}"
                         ])

    while redis.get("locked") == b"1":
        try:
            sys.stderr.write(f"{timestamp()} Waiting for the main process to unlock the queue.\n")
            sleep(5)
        except KeyboardInterrupt:
            exit(0)

    procs = [subprocess.Popen(i) for i in commands]

    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        pass
