#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-14 12:09
# Author  : MrFiona
# File    : cache_mechanism.py
# Software: PyCharm Community Edition

from __future__ import absolute_import

import os
import re
import pickle
import urlparse
from datetime import datetime, timedelta
from setting_global_variable import SRC_CACHE_DIR

class DiskCache(object):
    def __init__(self, purl_bak_string, cache_dir=SRC_CACHE_DIR, expires=timedelta(days=30)):
        self.cache_dir = cache_dir + os.sep + purl_bak_string
        self.expires = expires

    # def has_expired(self, timestamp):
    #     return datetime.utcnow() > timestamp + self.expires

    def url_to_path(self, url):
        components = urlparse.urlsplit(url)
        path = components.path
        filename = components.netloc + path + components.query
        filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]', '_', filename)
        filename = '/'.join(segment[:255] for segment in filename.split('/'))
        return_path = os.path.join(self.cache_dir, filename)
        return return_path

    def __getitem__(self, url):
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                return pickle.load(fp)
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(path, 'wb') as fp:
            fp.write(pickle.dumps(result))

if __name__ == '__main__':
    cache = DiskCache(purl_bak_string='Purley-FPGA')
    rr = cache['https://dcg-oss.intel.com/ossreport/auto/Purley-FPGA/BKC/2017%20WW13/5774_BKC.html']