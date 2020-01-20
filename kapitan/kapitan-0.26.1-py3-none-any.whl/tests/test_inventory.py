#!/usr/bin/env python3
#
# Copyright 2019 The Kapitan Authors
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

"inventory tests"

import unittest

from kapitan.resources import inventory


class InventoryTargetTest(unittest.TestCase):
    def test_inventory_target(self):
        inv = inventory(["examples/kubernetes"], "minikube-es")
        self.assertEqual(inv["parameters"]["cluster"]["name"], "minikube")

    def test_inventory_all_targets(self):
        inv = inventory(["examples/kubernetes"], None)
        self.assertNotEqual(inv.get("minikube-es"), None)
