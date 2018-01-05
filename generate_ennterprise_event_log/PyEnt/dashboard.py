# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time, EntityType, ShareType
from datetime import datetime, date, timedelta
import logging

log = logging.getLogger(__name__)


class Dashboard(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self._entity_type = EntityType['dashboard']

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def list(self):
        """Get dashboard list

        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :return: data
        """
        payload = dict(type='workspace')
        uri = self._console_url + '/dashboards'

        response = self._session.get(uri, params=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get(self, id):
        """Get dashboard by id

        :param id: dashboard id
        :return: dashboard info dict
        """

        uri = self._console_url + '/dashboard/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get dashboard by name

        :param name: dashboard name
        :return: dashboard info dict
        """

        dashboard_list = self.list()
        return [dashboard for dashboard in dashboard_list if dashboard['name'] == name][0]

    def create_by_data(self, data):
        """Create dashboard

        :param data: dashboard data
        :return: dashboard id
        """

        uri = self._console_url + '/dashboards'
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name=None, editable=True, layout_mode='gridster', layout_params=dict(columns=24), data=None, **kwargs):
        """Create dashboard
        
        :param name: dashboard name, required
        :param editable: dashboard editable or not, default is true
        :param layout_mode: dashboard layout mode, default is gridster
        :param layout_params: dashboard layout params
        :param data: dashboard data
        :param kwargs: other optional args
        :return: dashboard id
        """
        if data:
            create_data = data
        else:
            assert name
            create_data = {
                'name': name,
                'editable': editable,
                'type': 'workspace',
                'layoutMode': layout_mode,
                'layoutParams': layout_params,
            }
        return self.create_by_data(create_data)

    def get_components(self, id):
        """Get component list on this dashboard
        
        :param id: dashboard id
        :return: component list
        """
        uri = self._console_url + '/dashboard/' + id + '/components'
        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def add_component(self, id, component_id, height='G:6', width='G:6'):
        """Add component to this dashboard, only add on component once, if want to add n-times, call n-times
        
        :param id: dashboard id
        :param component_id: component id, string format
        :param height: component height
        :param width: component width
        :return: None
        """
        uri = self._console_url + '/dashboard/' + id + '/components'
        payload = {
            'componentId': component_id,
            'height': height,
            'width': width
        }
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def update_component(self, id, component_id, data=None, **kwargs):
        """Update component on this dashboard
        
        :param id: dashboard id
        :param component_id: component id
        :param data: update args
        :param kwargs: other optional keywords
        :return: None
        """
        uri = self._console_url + '/dashboard/' + id + '/component/' + component_id
        if data:
            update_data = data
        else:
            update_data = {}
            width = kwargs.pop('width', None)
            height = kwargs.pop('height', None)
            bottom = kwargs.pop('bottom', None)
            top = kwargs.pop('top', None)
            left = kwargs.pop('left', None)
            right = kwargs.pop('right', None)
            if width:
                update_data['width'] = width
            if height:
                update_data['height'] = height
            if bottom:
                update_data['bottom'] = bottom
            if top:
                update_data['top'] = top
            if left:
                update_data['left'] = left
            if right:
                update_data['right'] = right
                # other kwargs handler

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete_component(self, id, component_id):
        """Delete component on this dashboard

        :param id: dashboard id
        :param component_id: component id, string format
        :param height: component height
        :param width: component width
        :return: None
        """
        uri = self._console_url + '/dashboard/' + id + '/component/' + component_id

        response = self._session.delete(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def get_component_data(self, component_id, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """Get component data on this dashboard
        
        :param component_id: component id
        :param start_time: start time
        :param end_time: end time
        :return: component data
        """
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')

        payload = {
            'id': component_id,
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
        """Update dashboard

        :param id: dashboard id
        :param data: dashboard data
        :param kwargs: optional arguments to update dashboard
        :return: None
        """

        uri = self._console_url + '/dashboard/' + id
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
        """Delete dashboard by id, dashboard cannot be deleted if it has component

        :param id: dashboard id
        :return: None
        """

        uri = self._console_url + '/dashboard/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all assets

        :return: None
        """

        dashboard_list = self.list()
        for dashboard in dashboard_list:
            try:
                self.delete(dashboard['id'])
            except Exception as ex:
                print ex

    def get_share_type(self, id):
        """Get share type for dashboard

        :param id: dashboard id
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
        """Set share type for dashboard

        :param id: dashboard id
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