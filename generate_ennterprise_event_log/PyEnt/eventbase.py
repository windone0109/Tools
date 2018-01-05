# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check
from .eventtype import EventType

import logging
log = logging.getLogger(__name__)


class EventBase(object):
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
        """Get all event

        :return: event list
        """

        uri = self._console_url + '/security/eventBase/query'
        payload = {'paginate': False, "sorts": []}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get event by id

        :param id: event id
        :return: event dict
        """

        uri = self._console_url + '/security/eventBase/' + id
        response = self.session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_by_name(self, name):
        """Get event by name

        :param name: event name
        :return:  event dict
        """

        event_list = self.list()
        return [event for event in event_list if event['name'] == name][0]

    def create_by_data(self, data):
        """Create event

        :param data: create data
        :return:
        """
        print data
        uri = self._console_url + '/security/eventBase'
        response = self.session.post(uri, json=data)
        response_content = json.loads(response.content)
        print response.content

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['id']

    def create(self, name=None, keyword=None, type_name=None, level=None, data=None, **kwargs):
        """Create event
        
        :param name: event name, required
        :param keyword: event keyword, optional
        :param type_name: event type name, required
        :param level: event level, required
        :param data: create data
        :param kwargs: other args
        :return: create id
        """
        if data:
            create_data = data
        else:
            assert name
            assert type_name
            assert (level is not None)
            _event_type = EventType(self._console_url, self._session)
            print _event_type.get_by_name(type_name)
            type_id = _event_type.get_by_name(type_name)['id']
            create_data = {
                'name': name,
                'keyword': keyword,
                'eventTypeName': type_name,
                'typeId': type_id,
                'level': level

            }
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update event by id
        
        :param id: event id
        :param data: update data
        :param kwargs: optional args need to update
        :return: None
        """
        uri = self._console_url + '/security/eventBase/' + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            keyword = kwargs.pop('keyword', None)
            update_data = self.get(id)
            if name:
                update_data['name'] = name
            if keyword:
                update_data['keyword'] = keyword

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete event
        
        :param id: event id
        :return: None
        """
        uri = self._console_url + '/security/eventBase/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)
