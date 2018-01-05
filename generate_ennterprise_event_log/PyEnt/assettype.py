# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check


import logging
log = logging.getLogger(__name__)


class AssetType(object):
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
        """Get all asset types

        :return: asset type list
        """

        payload = {'paginate': False}
        uri = self._console_url + "/asset/type/query"

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        type_list = [x for x in response_content['data']['list'] if (x['parentId'].strip() and x['parentId'].strip() != '1')]

        for x in type_list:
            x.pop('parent')

        return type_list

    def get(self, id):
        """Get asset type by id

        :param id: asset type id
        :return: asset type info dict
        """

        uri = self._console_url + "/asset/type/" + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get asset type by name

        :param name:asset type name
        :return:asset type info dict
        """

        asset_type_list = self.list()
        return [asset_type for asset_type in asset_type_list if asset_type['name'] == name][0]

    def create_by_data(self, data):
        """Create asset type by name
        
        :param data: asset data
        :return: asset type id
        """

        uri = self._console_url + '/asset/type'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name=None, desc=None, parent_name=None, data=None, **kwargs):
        """Create asset type
        
        :param name: refer to name, required
        :param desc: refer to description, optional
        :param parent_name: parent asset name, parentId needed, required.
        :param data: asset data
        :param kwargs: other attrs
        :return: asset type id
        """

        if data:
            create_data = data
        else:
            assert name
            assert parent_name
            parent_id = self.get_by_name(parent_name)['id']
            create_data = {
                'name': name,
                'parentId': parent_id
            }
            if desc:
                create_data['description'] = desc

        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update asset type by id
        
        :param id: asset type id
        :param data: update data
        :param kwargs: optional arguments to update asset type
        :return: None
        """

        uri = self._console_url + '/asset/type/' + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            desc = kwargs.pop('description', None)
            update_data = self.get(id)
            if name:
                update_data['name'] = name
            if desc:
                update_data['description'] = desc

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete asset type by id
        
        :param id: assert type id
        :return: None
        """

        uri = self._console_url + '/asset/type/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all asset types
        
        :return: None
        """

        asset_type_list = self.list()
        for asset_type in asset_type_list:
            try:
                self.delete(asset_type['id'])
            except Exception as ex:
                pass
