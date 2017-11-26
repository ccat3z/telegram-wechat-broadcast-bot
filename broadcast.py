import copy

from urllib.request import Request, urlopen
from urllib.parse import urlencode

class Broadcast(object):
    require_key = []

    def __init__(self):
        self._require_key = copy.deepcopy(self.require_key)
        self.key = {}

    def need(self):
        if self._require_key:
            key = self._require_key[0]
            return (key,
                    lambda x: self._set(key, x))
        else:
            return ()

    def _set(self, key, value):
        self.key[key] = value
        self._require_key.remove(key)

    def send_img(self, uid, url):
        return False

class ServerChan(Broadcast):
    require_key = ["sckey"]

    def send_img(self, uid, url):
        data = urlencode({
            'text': "WeChat Broadcast from Telegram",
            'desp': str(uid) + '\n' + '![](' + url + ')'
        }).encode()
        urlopen(
            Request("https://sc.ftqq.com/" + self.key["sckey"] + ".send", data)
        )
        return True
