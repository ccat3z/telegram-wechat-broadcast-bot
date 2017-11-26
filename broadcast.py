import copy
import os
import base64
import tempfile

from urllib.request import Request, urlopen
from urllib.parse import urlencode

class Broadcast(object):
    name = "Broadcast"
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
    name = "Server酱"
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

class Local(Broadcast):
    name = "Local"
    require_key = ["output dir", "broadcast fifo"]

    def send_img(self, uid, url):
        r = urlopen(url)

        out_dir = self.key["output dir"].replace("ROOT", "/")
        fifo = self.key["broadcast fifo"]
        uid = base64.b64encode(str(uid).encode()).decode()

        cache = tempfile.NamedTemporaryFile()
        cache.file.write(r.read())

        os.system(("convert {} -background '#FFFFFF' -flatten -trim "
                  "{}.png").format(cache.name, out_dir + '/' + uid))
        os.system("echo {} > {}/{}".format(uid, out_dir, fifo))
        cache.close()
