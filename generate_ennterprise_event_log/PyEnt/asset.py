# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check
from .assettype import AssetType

import logging
log = logging.getLogger(__name__)


class Asset(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def init_param(self):
        uri = self._console_url + '/asset/getInitParams'

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['assetAttrsMap']

    def list(self):
        """List all assets
        
        :return: asset list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + '/asset/query'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get asset by id
        
        :param id: asset id
        :return: asset info dict
        """

        uri = self._console_url + '/asset/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get asset by name
        
        :param name: asset name
        :return: asset info dict
        """

        asset_list = self.list()
        return [asset for asset in asset_list if asset['assetName'] == name][0]

    def create_by_data(self, data):
        """Create asset
        
        :param data: asset data
        :return: asset id
        """

        uri = self._console_url + '/asset'
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, asset_name=None, ip_address=None, asset_type_name=None, data=None, **kwargs):
        """Create asset
        
        :param asset_name: asset name, required
        :param ip_address: asset ip address, required
        :param asset_type_name: asset type name, got asset type id from it, required
        :param data: asset data
        :param kwargs: other attrs
        :return: asset id
        """

        if data:
            create_data = data
        else:
            assert asset_name
            assert ip_address
            assert asset_type_name
            _asset_type = AssetType(self._console_url, self._session)
            asset_type_id = _asset_type.get_by_name(asset_type_name)['id']
            create_data = {
                'assetName': asset_name,
                'ipAddress': ip_address,
                'assetTypeName': asset_type_name,
                'assetTypeId': asset_type_id,
                'status': 3,
            }
            #kwargs handler
            status = kwargs.pop('status', None)
            if status:
                create_data['status'] = status

        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update asset
        
        :param id: asset id
        :param data: asset data
        :param kwargs: optional arguments to update asset
        :return: None
        """

        uri = self._console_url + '/asset/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            asset_name = kwargs.pop('asset_name', None)
            ip_address = kwargs.pop('ip_address', None)
            important = kwargs.pop('important', None)
            if asset_name:
                update_data['assetName'] = asset_name
            if ip_address:
                update_data['ipAddress'] = ip_address
            if important:
                update_data['important'] = important
            #other kwargs handler

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete asset by id
        
        :param id: asset id
        :return: None
        """

        uri = self._console_url + '/asset/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all assets

        :return: None
        """

        asset_list = self.list()
        for asset in asset_list:
            try:
                self.delete(asset['assetId'])
            except Exception as ex:
                pass

    def import_asset(self, local_file, strategy='skip'):
        """Import asset
        
        :param local_file: local asset file to import, xlsx format
        :param strategy: update strategy, default is skip
        :return: import uri
        """
        uri = self._console_url + '/asset/import/check'
        files = {'tempFile': open(local_file, 'rb')}
        response = self._session.post(uri, files=files)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        b_warn = len(response_content['data']['warnings'])
        uri = self._console_url + '/asset/import/'
        if b_warn:
            strategies = {
                'skip': 'skip',
                'update': 'update'
            }
            strategy = strategies.get(strategy, 'skip')
            uri = uri + strategy
        else:
            uri = uri + 'insert'
        payload = {'data': response_content['data']['assets']}
        response = self._session.post(uri, json=payload)
        status_code_check(response.status_code, 200)
        return uri

    def get_score(self, ip):
        """Get asset score
        
        :param ip: asset ip
        :return: asset score info
        """
        uri = self._console_url + '/api/node/asset/score/recent'
        payload = {"bool": {"must": [{"term": {"dim_scope": 1}}, {"term": {"score_ip_list": ip}}]}}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']



