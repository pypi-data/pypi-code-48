# coding: utf-8

"""
    Edge Impulse API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import openapi_client
from openapi_client.api.raw_data_api import RawDataApi  # noqa: E501
from openapi_client.rest import ApiException


class TestRawDataApi(unittest.TestCase):
    """RawDataApi unit test stubs"""

    def setUp(self):
        self.api = openapi_client.api.raw_data_api.RawDataApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_copy_sample(self):
        """Test case for copy_sample

        Copy sample  # noqa: E501
        """
        pass

    def test_delete_sample(self):
        """Test case for delete_sample

        Remove sample  # noqa: E501
        """
        pass

    def test_download_raw_data(self):
        """Test case for download_raw_data

        Download data (CSV)  # noqa: E501
        """
        pass

    def test_download_raw_data_parquet(self):
        """Test case for download_raw_data_parquet

        Download data (parquet)  # noqa: E501
        """
        pass

    def test_download_raw_labels(self):
        """Test case for download_raw_labels

        Download labels (CSV)  # noqa: E501
        """
        pass

    def test_edit_label(self):
        """Test case for edit_label

        Edit label  # noqa: E501
        """
        pass

    def test_get_sample(self):
        """Test case for get_sample

        Get sample  # noqa: E501
        """
        pass

    def test_get_sample_as_audio(self):
        """Test case for get_sample_as_audio

        Get WAV file  # noqa: E501
        """
        pass

    def test_get_sample_slice(self):
        """Test case for get_sample_slice

        Get sample  # noqa: E501
        """
        pass

    def test_list_samples(self):
        """Test case for list_samples

        List samples  # noqa: E501
        """
        pass

    def test_rename_sample(self):
        """Test case for rename_sample

        Rename sample  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
