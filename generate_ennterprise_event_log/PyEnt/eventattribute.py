# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check
from .filter import EntObject, filter


class EventAttribute(object):
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
        """Get all event attributes

        :return: event attribute list
        """

        uri = self._console_url + '/event/attribute/query'
        data = {'paginate': False}
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get_attr_by_level(self, level):
        """Get attr list matched level
        
        :param level: level need to match
        :return: attr list
        """
        attribute_list = self.list()
        return [attribute for attribute in attribute_list if attribute['sysAttr'] == level]

    def get(self, id):
        """Get event attribute by id

        :param id: attribute id
        :return: event attribute
        """

        uri = self._console_url + '/event/attribute/' + id
        response = self.session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_by_name(self, name):
        """Get event attribute by name
        
        :param name: attribute name
        :return: event attribute
        """
        attribute_list = self.list()
        return [attribute for attribute in attribute_list if attribute['attrName'] == name][0]

    def update(self, id, data=None, **kwargs):
        """Update event attribute by id

        :param id: event attribute id
        :param data: update data
        :param kwargs: Optional arguments to update event attribute
        :return:
        """

        uri = self._console_url + '/event/attribute/' + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            desc = kwargs.pop('desc', None)
            update_data = self.get(id)
            if name:
                update_data['attrName'] = name
            if desc:
                update_data['attrDesc'] = desc

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def filter(self, **kwargs):
        object_list = [EntObject(**x) for x in self.list()]
        return filter(object_list, **kwargs)

