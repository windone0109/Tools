# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check

import logging
log = logging.getLogger(__name__)

class IntelligenceGroup(object):
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
        """Get all intelligence type

        :return: intelligence list
        """

        uri = self._console_url + '/security/intelligenceGroup'
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        type_list = [x for x in response_content['data']['list'] if x['idPath'].count(r'/') != 0]

        return type_list

    def list_sub_type(self):
        """Get all intelligence sub type

        :return: intelligence sub type list
        """
        uri = self._console_url + '/security/intelligenceGroup'

        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        type_list = [x for x in response_content['data']['list'] if (x['idPath'].count(u'／') == 2 and x['idPath'].count(r'/') == 0)]

        return type_list


    def get(self, id):
        """Get intelligence type by id

        :param id: intelligence id
        :return: intelligence type
        """

        uri = self._console_url + '/security/intelligenceGroup/' + id
        response = self.session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['intelligenceGroup']

    def get_by_name(self, name):
        """Get event type by name

        :param name: type name
        :return:  event type
        """

        intelligence_type_list = self.list()
        intelligence_type_list.extend(self.list_sub_type())
        return [intelligence_type for intelligence_type in intelligence_type_list if intelligence_type['name'] == name][0]
