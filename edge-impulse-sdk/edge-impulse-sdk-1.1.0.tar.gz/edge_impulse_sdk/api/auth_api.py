# coding: utf-8

"""
    Edge Impulse API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from edge_impulse_sdk.api_client import ApiClient
from edge_impulse_sdk.exceptions import (
    ApiTypeError,
    ApiValueError
)


class AuthApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def discourse(self, sso, sig, **kwargs):  # noqa: E501
        """Discourse  # noqa: E501

        Log in a user to the forum. This function is only available through a JWT token.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.discourse(sso, sig, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str sso: Single sign-on token (required)
        :param str sig: Verification signature (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.discourse_with_http_info(sso, sig, **kwargs)  # noqa: E501

    def discourse_with_http_info(self, sso, sig, **kwargs):  # noqa: E501
        """Discourse  # noqa: E501

        Log in a user to the forum. This function is only available through a JWT token.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.discourse_with_http_info(sso, sig, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str sso: Single sign-on token (required)
        :param str sig: Verification signature (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['sso', 'sig']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method discourse" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'sso' is set
        if self.api_client.client_side_validation and ('sso' not in local_var_params or  # noqa: E501
                                                        local_var_params['sso'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `sso` when calling `discourse`")  # noqa: E501
        # verify the required parameter 'sig' is set
        if self.api_client.client_side_validation and ('sig' not in local_var_params or  # noqa: E501
                                                        local_var_params['sig'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `sig` when calling `discourse`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'sso' in local_var_params and local_var_params['sso'] is not None:  # noqa: E501
            query_params.append(('sso', local_var_params['sso']))  # noqa: E501
        if 'sig' in local_var_params and local_var_params['sig'] is not None:  # noqa: E501
            query_params.append(('sig', local_var_params['sig']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['ApiKeyAuthentication', 'JWTAuthentication']  # noqa: E501

        return self.api_client.call_api(
            '/api/auth/discourse', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def readme(self, **kwargs):  # noqa: E501
        """Readme.io  # noqa: E501

        Log in a user to the docs. This function is only available through a JWT token.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.readme(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.readme_with_http_info(**kwargs)  # noqa: E501

    def readme_with_http_info(self, **kwargs):  # noqa: E501
        """Readme.io  # noqa: E501

        Log in a user to the docs. This function is only available through a JWT token.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.readme_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = []  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method readme" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['ApiKeyAuthentication', 'JWTAuthentication']  # noqa: E501

        return self.api_client.call_api(
            '/api/auth/readme', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
