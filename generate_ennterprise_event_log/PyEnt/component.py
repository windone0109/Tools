# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time, EntityType, ShareType
from datetime import datetime, date, timedelta

import logging

log = logging.getLogger(__name__)


class ComponentGroup(object):
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
        """List all component groups

        :return: component group list
        """

        uri = self._console_url + '/system/componentGroup/query'

        response = self._session.post(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        type_list = [x for x in response_content['data']['list'] if ('isDelete' in x and x['isDelete'] != 1)]

        return type_list

    def get(self, id):
        """Get component group by id

        :param id: component group id
        :return: component group info dict
        """

        uri = self._console_url + '/system/componentGroup/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get component group by name

        :param name: component group name
        :return: component group info dict
        """

        group_list = self.list()
        return [group for group in group_list if group['name'] == name][0]

    def create_by_data(self, data):
        """Create component group

        :param data: component group data
        :return: None
        """

        uri = self._console_url + '/system/componentGroup'
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        # return response_content['data']['id']

    def create(self, name=None, parent_name=None, data=None, **kwargs):
        """Create component group

        :param name: component group name, required
        :param parent_name: component group parent name, required
        :param data: component group data
        :param kwargs: other optional data
        :return: None
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
                'parentName': parent_name
            }
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update component group

        :param id: component group id
        :param data: component group data
        :param kwargs: optional arguments to update component group
        :return: None
        """

        uri = self._console_url + '/system/componentGroup/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            if name:
                update_data['name'] = name
                # other kwargs handler

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete component group by id

        :param id: component group id
        :return: None
        """

        uri = self._console_url + '/system/componentGroup/' + id
        response = self._session.delete(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])


class Component(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self._entity_type = EntityType['component']

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def list(self):
        """List all components

        :return: components list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + '/components/query'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get component by id

        :param id: component id
        :return: component info dict
        """

        uri = self._console_url + '/component/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get component by name

        :param name: component name
        :return: component info dict
        """

        component_list = self.list()
        return [component for component in component_list if component['name'] == name][0]

    def create_by_data(self, data):
        """Create component

        :param data: component data
        :return: component id
        """

        uri = self._console_url + '/components'
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create_by_file(self, local_file, name=None):
        """Create component by file data
        
        :param local_file: file data contains component info
        :param name: component name
        :return: component id
        """
        with open(local_file) as pf:
            create_data = json.loads(pf.read())
        if name:
            create_data['name'] = name
        return self.create_by_data(create_data)

    def preview(self, id, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """preview component
        
        :param id: component id
        :param start_time: preview start time
        :param end_time: preview end time
        :return: preview data
        """
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')

        payload = {
            'id': id,
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        uri = self._console_url + '/component/data'
        response = self._session.post(uri, json=payload)

        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def update(self, id, data=None, **kwargs):
        """Update component

        :param id: component id
        :param data: component data
        :param kwargs: optional arguments to update component
        :return: None
        """

        uri = self._console_url + '/component/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            if name:
                update_data['name'] = name
                # other kwargs handler

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete component by id

        :param id: component id
        :return: None
        """

        uri = self._console_url + '/component/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def get_share_type(self, id):
        """Get share type for component

        :param id: component id
        :return: shareType
        """
        payload = {'entityType': self._entity_type}
        uri = self._console_url + '/system/share/' + id

        response = self._session.get(uri, params=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['shareType']

    def set_share_type(self, id, share_type, users=[]):
        """Set share type for component

        :param id: component id
        :param share_type: share type
        :param users: users if set shareType=2
        :return: None
        """
        uri = self._console_url + '/system/share/' + id
        _share_type = ShareType.get(share_type, 1)
        payload = {
            'entityType': self._entity_type,
            'shareType': _share_type
        }
        if share_type == 'specific':
            assert users
            payload['users'] = users

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

