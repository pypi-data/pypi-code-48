'''
This file is a part of Test Mile Arjuna
Copyright 2018 Test Mile Software Testing Pvt Ltd

Website: www.TestMile.com
Email: support [at] testmile.com
Creator: Rahul Verma

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from .common.rule import *
from .common.utils import *

class EvarsDefinedRule(DictKeyPresenceRule):

    def _get_container(self, test_object):
        return test_object.tvars.evars


class EvarValueRule(DictKeyValueRule):

    def __init__(self, totype, is_inclusion_rule, robject, condition, expression):
        super().__init__(totype, is_inclusion_rule, robject, condition, expression)

    def _get_container(self, test_object):
        return test_object.tvars.evars

    def _convert_provided_value(self, provided_value, name=None, target_object_value=None):
        target_type = type(target_object_value)
        if target_type == bool:
            target_type = custom_bool
        return target_type(provided_value)