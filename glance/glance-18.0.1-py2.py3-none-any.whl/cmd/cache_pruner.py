# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Glance Image Cache Pruner

This is meant to be run as a periodic task, perhaps every half-hour.
"""

import os
import sys

from oslo_log import log as logging

# If ../glance/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(possible_topdir, 'glance', '__init__.py')):
    sys.path.insert(0, possible_topdir)

from glance.common import config
from glance.image_cache import pruner

CONF = config.CONF
logging.register_options(CONF)
CONF.set_default(name='use_stderr', default=True)


def main():
    try:
        config.parse_cache_args()
        logging.setup(CONF, 'glance')

        app = pruner.Pruner()
        app.run()
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)
