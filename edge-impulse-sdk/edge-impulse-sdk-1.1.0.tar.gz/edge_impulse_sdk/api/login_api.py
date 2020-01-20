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


class LoginApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def login(self, get_jwt_token_request, **kwargs):  # noqa: E501
        """Get JWT token  # noqa: E501

        Get a JWT token to authenticate with the API.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.login(get_jwt_token_request, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param GetJWTTokenRequest get_jwt_token_request: (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: GetJWTTokenResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.login_with_http_info(get_jwt_token_request, **kwargs)  # noqa: E501

    def login_with_http_info(self, get_jwt_token_request, **kwargs):  # noqa: E501
        """Get JWT token  # noqa: E501

        Get a JWT token to authenticate with the API.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.login_with_http_info(get_jwt_token_request, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param GetJWTTokenRequest get_jwt_token_request: (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(GetJWTTokenResponse, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['get_jwt_token_request']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method login" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'get_jwt_token_request' is set
        if self.api_client.client_side_validation and ('get_jwt_token_request' not in local_var_params or  # noqa: E501
                                                        local_var_params['get_jwt_token_request'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `get_jwt_token_request` when calling `login`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'get_jwt_token_request' in local_var_params:
            body_params = local_var_params['get_jwt_token_request']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api-login', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='GetJWTTokenResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
