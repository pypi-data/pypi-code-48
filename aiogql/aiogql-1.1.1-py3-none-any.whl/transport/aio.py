import asyncio
import aiohttp
from graphql.execution import ExecutionResult
from graphql.language.printer import print_ast

from .http import HTTPTransport


class AIOHTTPTransport(HTTPTransport):
    def __init__(self, url: str, auth=None, use_json=True, timeout=None, **kwargs):
        """
        :param url: The GraphQL URL
        :param auth: Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth
        :param use_json: Send request body as JSON instead of form-urlencoded
        :param timeout: Specifies a default timeout for requests (Default: None)
        """
        super().__init__(url, **kwargs)
        self.auth = auth
        self.default_timeout = timeout
        self.use_json = use_json

    async def execute(self, document, variable_values=None, timeout=None):
        query_str = print_ast(document)
        payload = {
            'query': query_str,
            'variables': variable_values or {}
        }

        if self.use_json:
            body = {'json': payload}
        else:
            body = {'data': payload}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url,
                                 auth=self.auth,
                                 headers=self.headers,
                                 timeout=timeout or self.default_timeout,
                                 **body) as response:
                assert response.status == 200, '{} {} - {}'.format(
                    response.status,
                    response.reason,
                    await response.text())
                result = await response.json() if self.use_json else await response.text()

        assert 'errors' in result or 'data' in result, 'Received non-compatible response "{}"'.format(result)
        return ExecutionResult(
            errors=result.get('errors'),
            data=result.get('data')
        )

