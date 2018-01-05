# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check

import logging

log = logging.getLogger(__name__)


class Contexts(object):
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
        """List all contexts

        :return: contexts list
        """

        uri = self._console_url + '/api/cep/contexts'

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get context by id

        :param id: context id
        :return: context info dict
        """

        uri = self._console_url + '/api/cep/contexts/' + str(id)

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content

    def get_by_name(self, name):
        """Get context by name

        :param name: context name
        :return: context info dict
        """

        context_list = self.list()
        return [context for context in context_list if context['name'] == name][0]

    def create_by_data(self, data):
        uri = self._console_url + '/api/cep/contexts'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 201)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])
        # return response_content['data']['id']

    def create(self, data=None, **kwargs):
        pass

    def delete(self, id):
        """Delete context by id

        :param id: context id
        :return: None
        """

        uri = self._console_url + '/api/cep/contexts/' + str(id)
        response = self._session.delete(uri)
        status_code_check(response.status_code, 204)

    def delete_all(self):
        """Delete all contexts

        :return: None
        """

        context_list = self.list()
        for context in context_list:
            try:
                self.delete(context['id'])
            except Exception as ex:
                pass