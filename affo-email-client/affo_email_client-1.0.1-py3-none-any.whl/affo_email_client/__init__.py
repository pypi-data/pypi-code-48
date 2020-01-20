from simple_rest_client.api import API
from simple_rest_client.resource import Resource

__all__ = ["Client"]

VERSION = "1.0.1"


class MessageResource(Resource):
    actions = {"create": {"method": "POST", "url": "/message/"}}


class TemplateResource(Resource):
    actions = {"send": {"method": "POST", "url": "/template/{}/send/"}}


class UnsubscribeResource(Resource):
    actions = {"from_tag": {"method": "GET", "url": "/unsubscribe/{}/token/{}/"}}


class Client:
    def __init__(self, api_root_url, **kwargs):
        self.email_api = API(
            api_root_url=api_root_url, headers={"Content-Type": "application/json"}, json_encode_body=True, **kwargs
        )
        self.email_api.add_resource(resource_name="message", resource_class=MessageResource)
        self.email_api.add_resource(resource_name="template", resource_class=TemplateResource)
        self.email_api.add_resource(resource_name="unsubscribe", resource_class=UnsubscribeResource)

    def __getattr__(self, name):
        return getattr(self.email_api, name)
