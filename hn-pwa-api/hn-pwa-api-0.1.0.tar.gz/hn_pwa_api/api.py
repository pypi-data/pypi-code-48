import requests

from .entry import Entry
from .post import Post


class HNApi(object):
    def __init__(self, *args, **kwargs):
        self.s = requests.Session()
        self.feed_limits = {
            "news": 10,
            "newest": 12,
            "ask": 2,
            "show": 2,
            "jobs": 1
        }

    def feed(self, feed_type, pagination=1):
        if pagination < self.feed_limits[feed_type]:
            feed_entries = self.s.get(f'https://api.hnpwa.com/v0/{feed_type}/{pagination}.json').json()
        else:
            feed_entries = self.s.get(f'https://api.hnpwa.com/v0/{feed_type}/{self.feed_limits[feed_type]}.json').json()
        return [Entry(**feed_entry) for feed_entry in feed_entries]

    def post_item(self, post_id):
        post = self.s.get(f'https://api.hnpwa.com/v0/item/{post_id}.json').json()
        return Post(**post)
