# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check


import logging
log = logging.getLogger(__name__)


class SystemUnit(object):
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
        """List system unit
        
        :return: system unit list
        """

        payload = {'paginate': False}
        uri = self._console_url + "/system/unit/query"

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get system unit by id
        
        :param id: system unit id
        :return: system unit info dict
        """

        uri = self._console_url + "/system/unit/" + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get system unit by name
        
        :param name: system unit name
        :return: system unit info dict
        """

        unit_list = self.list()
        return [unit for unit in unit_list if unit['name'] == name][0]

    def create_by_data(self, data):
        """Create system unit by data
        
        :param data: system unit data
        :return: system unit id
        """

        uri = self._console_url + "/system/unit"
        response = self._session.put(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name=None, description=None, parent_name=None, data=None, **kwargs):
        """Create system unit
        
        :param name: refer to name. required
        :param description: refer to description, optional
        :param parent_name: parentId related, required
        :param data: stereotypes of the parameters, do not need to construct.
        :param kwargs: other attrs
        :return: system unit id
        """

        if data:
            create_data = data
        else:
            assert name
            assert parent_name
            parent_id = self.get_by_name(parent_name)['id']
            create_data = {
                'name': name,
                'parentId': parent_id,
            }
            if description:
                create_data['description'] = description
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update system unit
        
        :param id: system unit id
        :param data: update data
        :param kwargs: optional arguments to update system unit
        :return: None
        """

        uri = self._console_url + "/system/unit/" + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            description = kwargs.pop('description', None)
            update_data = self.get(id)
            if name:
                update_data['name'] = name
            if description:
                update_data['description'] = description
        response = self._session.post(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete system unit
        
        :param id: system unit id
        :return: None
        """

        uri = self._console_url + '/system/unit/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

