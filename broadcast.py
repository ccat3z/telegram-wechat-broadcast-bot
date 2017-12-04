import copy
import os
import base64
import tempfile
import subprocess

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

    def _set(self, key, value, update = None):
        self.key[key] = value
        self._require_key.remove(key)

    def send_img(self, uid, url):
        return False

class ServerChan(Broadcast):
    name = "Server酱"
    require_key = ["sckey"]

    def send_img(self, uid, url, update = None):
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

    def send_img(self, uid, url, update = None):
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

class ReplyFile(Broadcast):
    name = "Reply file"
    convert_cmd = ("convert {} -background '#FFFFFF' -flatten -trim "
                   "-resize 512x512 "
                   "{}")

    def send_img(self, uid, url, update):

        # fetch file
        update.message.reply_text("Fetching image...")
        r = urlopen(url)
        cache = tempfile.NamedTemporaryFile()
        cache.file.write(r.read())

        # process uid
        uid = base64.b64encode(str(uid).encode()).decode()

        # process image
        converted_file_path = '/tmp/' + uid + '.png'
        update.message.reply_text("Processing image...")
        p = subprocess.Popen(
                self.convert_cmd.format(cache.name, converted_file_path),
                shell = True, stderr = subprocess.PIPE
            )
        err_msg = p.stderr.read().decode("UTF-8")

        # reply image
        try:
            with open(converted_file_path, 'rb') as f:
                update.message.reply_text("Sending...")
                update.message.reply_photo(f)
                os.remove(converted_file_path)
        except FileNotFoundError:
            update.message.reply_text("Convert error.")
            update.message.reply_text(err_msg)

        # clear cache
        cache.close()
