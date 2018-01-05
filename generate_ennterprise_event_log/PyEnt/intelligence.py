# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check

import logging

log = logging.getLogger(__name__)


class Intelligence(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def list(self):
        """List all intelligences

        :return: intelligence list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + '/security/intelligence/query'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get intelligence by id

        :param id: intelligence id
        :return: intelligence info dict
        """

        uri = self._console_url + '/security/intelligence/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get intelligence by name

        :param name: intelligence name
        :return: intelligence info dict
        """

        intelligence_list = self.list()
        return [intelligence for intelligence in intelligence_list if intelligence['content'] == name][0]