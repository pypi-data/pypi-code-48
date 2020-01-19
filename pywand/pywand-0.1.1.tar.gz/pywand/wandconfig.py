#! /usr/bin/env python3

import configparser
import os
import shutil

class WandConfig:

    def __init__(self, config_file_path=None):

        # check for class init path location
        if not config_file_path:
            config_file_path = "/etc/wand_config.ini"

        # check for env var overriding path
        config_file_path = os.getenv("WAND_CONFIG_FILE", default=config_file_path)

        # init config, read blank if file is missing.
        config = configparser.ConfigParser()
        if os.path.isfile(config_file_path):
            config.read(config_file_path)
        else:
            config.read_string("")

        # IR Section
        self.pulse_time_thresh = config.getint('IR', 'pulse_time_thresh', fallback=410)
        self.ir_device = config.get('IR', 'ir_device', fallback="/dev/lirc0")
        self.ir_timeout = config.getint('IR', 'ir_timeout', fallback=2000)
        self.irctl_path = config.get('IR', 'irctl_path', fallback=shutil.which('ir-ctl'))

        # TUNING Section
        self.wand_bit_tolerance = config.getint('TUNING', 'wand_bit_tolerance', fallback=1)

        # WANDS
        # reverse wands so they key is the code and value is the name
        if config.has_section('WANDS'):
            self.wands = {wcode:wname for wname, wcode in config['WANDS'].items()}
        else:
            self.wands = {}
