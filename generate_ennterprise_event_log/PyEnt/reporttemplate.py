# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, EntityType, ShareType
from .assettype import AssetType

import logging

log = logging.getLogger(__name__)


class ReportTemplate(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self._entity_type = EntityType['report_template']

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def get_user_info(self):
        uri = self._console_url + '/system/auth/userInfo'
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def list(self):
        """List all templates

        :return: template list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + '/api/node/report/templates'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get template by id

        :param id: template id
        :return: template info dict
        """

        uri = self._console_url + '/api/node/report/template/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get template by name

        :param name: template name
        :return: template info dict
        """

        template_list = self.list()
        return [template for template in template_list if template['name'] == name][0]

    def create_by_data(self, data):
        """Create template

        :param data: template data
        :return: template id
        """

        uri = self._console_url + '/api/node/report/template'
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create_by_file(self, local_file, title=None):
        """Create template by file
        
        :param local_file: template file
        :param title: template name
        :return: template id
        """
        with open(local_file) as pf:
            create_data = json.loads(pf.read())
        if title:
            create_data['title'] = title
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update template

        :param id: template id
        :param data: template data
        :param kwargs: optional arguments to update template
        :return: None
        """

        uri = self._console_url + '/api/node/report/template/' + id
        if data:
            update_data = data
        else:
            ori_data = self.get(id)
            update_data = {}

            title = kwargs.pop('title', None)
            html = kwargs.pop('html', None)
            if title:
                update_data['title'] = title
            if html:
                update_data['html'] = html
                update_data['parsedHtml'] = html
            else:
                if 'html' in ori_data:
                    update_data['html'] = ori_data['html']
                    update_data['parsedHtml'] = ori_data['html']
                # other kwargs handler

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete template by id

        :param id: template id
        :return: None
        """

        uri = self._console_url + '/api/node/report/template/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def get_share_type(self, id):
        """Get share type for report template

        :param id: template id
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
        """Set share type for report template

        :param id: template id
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

