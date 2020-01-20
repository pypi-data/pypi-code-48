#! /usr/bin/env python3

import configparser
import datetime
import json
import logging
import os
import pprint
import requests
import urllib.parse

from pywand.wandreader import WandInputReader
from pywand.wandid import WandId

class HomeAssistantAutomation:

    def trigger(self, extra_data=None):

        if datetime.datetime.now() >= self.next_trigger_allowed:
            trigger_data = self.data
            if isinstance(extra_data, dict):
                trigger_data.update(extra_data)

            self.log.info("Triggering HomeAssistant Automation")
            self.log.debug("Request Data: {}".format(pprint.pformat(trigger_data)))
            r = requests.post(self.url, json=trigger_data, headers=self.headers)
            r.raise_for_status()
            self.next_trigger_allowed = datetime.datetime.now() + datetime.timedelta(seconds=self.debounce_time)


    def __init__(self, config, log):

        self.log = log

        self.url = urllib.parse.urljoin(
            config.get('HOMEASSISTANT', 'base_url'),
            'api/services/automation/trigger',
        )
        self.log.info("HomeAssistant URL: {}".format(self.url))

        self.debounce_time = config.getint('HOMEASSISTANT', 'debounce_time', fallback=1)
        self.log.info("HomeAssistant Debounce Time: {} seconds".format(self.debounce_time))

        self.next_trigger_allowed = datetime.datetime.now()

        self.headers = {}
        auth_token = config.get('HOMEASSISTANT', 'auth_token', fallback="")
        if auth_token:
            self.headers["Authorization"] = "Bearer {}".format(auth_token)

        self.data = {"entity_id": "automation.{}".format(
            config.get('HOMEASSISTANT', 'automation_name'),
        )}


class HomeAssistantWands:

    def run(self):

        for i in self.wandreader.get_codes():
            wand_name = self.wands.best_wand_match(i['wand'])
            if self.send_wand_name:
                self.ha.trigger(extra_data={'wand_name': wand_name})
            else:
                self.ha.trigger()

    def __init__(self, config_file_path=None, loglevel="INFO"):

        logging.basicConfig()
        self.log = logging.getLogger('ha_magiwand')
        self.log.setLevel(loglevel)

        if not config_file_path:
            config_file_path = "/etc/wand_config.ini"
        config_file_path = os.getenv("WAND_CONFIG_FILE", default=config_file_path)
        self.log.info("Using Log File {}".format(config_file_path))

        if not os.path.isfile(config_file_path):
            raise FileNotFoundError("A config file is REQUIRED for this service.")

        # init the pywand classes using the unified config file
        self.wandreader = WandInputReader(config_file_path=config_file_path)
        self.wands = WandId(config_file_path=config_file_path)

        config = configparser.ConfigParser()
        config.read(config_file_path)
        self.send_wand_name = config.getboolean('HOMEASSISTANT', 'send_wand_name', fallback=False)
        self.log.info("Sending Wand Names to HomeAssistant: {}".format(str(self.send_wand_name)))
        self.ha = HomeAssistantAutomation(config, self.log)
        del config



