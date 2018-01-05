# -*- coding: utf-8 -*-

import os
import json
from ._internal_utils import status_code_check, response_status_check

import logging
log = logging.getLogger(__name__)


class License(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def import_in(self, localfile):
        uri = self._console_url + "/license/import"
        file_name = os.path.basename(localfile)
        files = {'tempFile': (file_name, open(localfile, 'rb'), 'application/octet-stream')}
        response = self._session.post(uri, files=files)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)

        if response_content:
            response_status_check(response_content['statusCode'], 0, response_content['messages'])

