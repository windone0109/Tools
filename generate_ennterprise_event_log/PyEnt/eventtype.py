# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check
from .eventattribute import EventAttribute


import logging
log = logging.getLogger(__name__)

class EventType(object):
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
        """Get all event type

        :return: event type list
        """

        uri = self._console_url + '/event/eventType/query'
        payload = {'paginate': False}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        type_list = [x for x in response_content['data']['list'] if not x['pid'] == '-1']
        # for x in type_list:
        #     x.pop('attributes')

        return type_list

    def list_sub_type(self):
        """Get all event sub type

        :return: event sub type list
        """
        uri = self._console_url + '/event/eventType/query'
        payload = {'paginate': False}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        type_list = [x for x in response_content['data']['list'] if (x['pid'] == '-1' and x['id'] != '-1')]
        # for x in type_list:
        #     x.pop('attributes')

        return type_list


    def get(self, id):
        """Get event type by id

        :param id: type id
        :return: event type
        """

        uri = self._console_url + '/event/eventType/' + id
        response = self.session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_by_name(self, name):
        """Get event type by name

        :param name: type name
        :return:  event type
        """

        event_type_list = self.list()
        event_type_list.extend(self.list_sub_type())
        return [event_type for event_type in event_type_list if event_type['typeName'] == name][0]

    def create_by_data(self, data):
        """Create event type

        :param data: create data
        :return: event type id
        """
        uri = self._console_url + '/event/eventType'
        response = self.session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['id']

    def create(self, name=None, desc=None, parent_name=None, key_fields=None, event_content='', data=None, **kwargs):
        """Create event type
        
        :param name: type name, required
        :param desc: description
        :param parent_name: parent type name, required
        :param key_fields: key fields
        :param event_content: event content
        :param data: create data
        :param kwargs: other option args
        :return: create id
        """
        if data:
            create_data = data
        else:
            assert name
            assert parent_name
            _event_attr = EventAttribute(self._console_url, self._session)
            parent_info = self.get_by_name(parent_name)
            parent_attrs = parent_info['attributes']
            parent_id = parent_info['id']
            parent_attrs.extend(_event_attr.get_attr_by_level(3))
            create_data = {
                'typeName': name,
                'attributes': parent_attrs,
                'pid': parent_id,
                'pName': parent_name,
                'description': desc,
                'eventContent': event_content,
                'keyFields': key_fields
            }
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update event type by id

        :param id: event type id
        :param data: update data
        :param kwargs: Optional arguments to update event type
        :return:
        """

        uri = self._console_url + '/event/eventType/' + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            desc = kwargs.pop('description', None)
            event_content = kwargs.pop('event_content', None)
            key_fields = kwargs.pop('key_fields', None)
            update_data = self.get(id)
            if name:
                update_data['typeName'] = name
            if desc:
                update_data['description'] = desc
            if event_content:
                update_data['eventContent'] = event_content
            if key_fields:
                update_data['keyFields'] = key_fields

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """ Delete event type by id

        :param id: event type id
        :return:
        """

        uri = self._console_url + '/event/eventType/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

