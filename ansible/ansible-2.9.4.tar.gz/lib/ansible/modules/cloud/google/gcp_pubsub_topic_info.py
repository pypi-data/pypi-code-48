#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Google
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# ----------------------------------------------------------------------------
#
#     ***     AUTO GENERATED CODE    ***    AUTO GENERATED CODE     ***
#
# ----------------------------------------------------------------------------
#
#     This file is automatically generated by Magic Modules and manual
#     changes will be clobbered when the file is regenerated.
#
#     Please read more about how to change this file at
#     https://www.github.com/GoogleCloudPlatform/magic-modules
#
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

__metaclass__ = type

################################################################################
# Documentation
################################################################################

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ["preview"], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gcp_pubsub_topic_info
description:
- Gather info for GCP Topic
- This module was called C(gcp_pubsub_topic_facts) before Ansible 2.9. The usage has
  not changed.
short_description: Gather info for GCP Topic
version_added: 2.8
author: Google Inc. (@googlecloudplatform)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options: {}
extends_documentation_fragment: gcp
'''

EXAMPLES = '''
- name: get info on a topic
  gcp_pubsub_topic_info:
    project: test_project
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
resources:
  description: List of resources
  returned: always
  type: complex
  contains:
    name:
      description:
      - Name of the topic.
      returned: success
      type: str
    kmsKeyName:
      description:
      - The resource name of the Cloud KMS CryptoKey to be used to protect access
        to messages published on this topic. Your project's PubSub service account
        (`service-{{PROJECT_NUMBER}}@gcp-sa-pubsub.iam.gserviceaccount.com`) must
        have `roles/cloudkms.cryptoKeyEncrypterDecrypter` to use this feature.
      - The expected format is `projects/*/locations/*/keyRings/*/cryptoKeys/*` .
      returned: success
      type: str
    labels:
      description:
      - A set of key/value label pairs to assign to this Topic.
      returned: success
      type: dict
    messageStoragePolicy:
      description:
      - Policy constraining the set of Google Cloud Platform regions where messages
        published to the topic may be stored. If not present, then no constraints
        are in effect.
      returned: success
      type: complex
      contains:
        allowedPersistenceRegions:
          description:
          - A list of IDs of GCP regions where messages that are published to the
            topic may be persisted in storage. Messages published by publishers running
            in non-allowed GCP regions (or running outside of GCP altogether) will
            be routed for storage in one of the allowed regions. An empty list means
            that no regions are allowed, and is not a valid configuration.
          returned: success
          type: list
'''

################################################################################
# Imports
################################################################################
from ansible.module_utils.gcp_utils import navigate_hash, GcpSession, GcpModule, GcpRequest
import json

################################################################################
# Main
################################################################################


def main():
    module = GcpModule(argument_spec=dict())

    if module._name == 'gcp_pubsub_topic_facts':
        module.deprecate("The 'gcp_pubsub_topic_facts' module has been renamed to 'gcp_pubsub_topic_info'", version='2.13')

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/pubsub']

    return_value = {'resources': fetch_list(module, collection(module))}
    module.exit_json(**return_value)


def collection(module):
    return "https://pubsub.googleapis.com/v1/projects/{project}/topics".format(**module.params)


def fetch_list(module, link):
    auth = GcpSession(module, 'pubsub')
    return auth.list(link, return_if_object, array_name='topics')


def return_if_object(module, response):
    # If not found, return nothing.
    if response.status_code == 404:
        return None

    # If no content, return nothing.
    if response.status_code == 204:
        return None

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg="Invalid JSON response with error: %s" % inst)

    if navigate_hash(result, ['error', 'errors']):
        module.fail_json(msg=navigate_hash(result, ['error', 'errors']))

    return result


if __name__ == "__main__":
    main()
