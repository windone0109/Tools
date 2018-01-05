# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check
from .assettype import AssetType

import logging

log = logging.getLogger(__name__)


class AssetView(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self._dims = {
            'business': 3,
            'domain': 2,
            'location': 4,
            'org': 5,
        }

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def list(self):
        """List all assets

        :return: asset list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + '/asset/view/query'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def _gen_score_payload(self, scope, related_id=None):
        """Generate payload, for function use
        
        :param scope: dim scope, int
        :param related_id: dim scope id
        :return: request payload dict
        """
        if scope == 2:
            if not related_id:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_domain_id": str(scope)}}]}}
            else:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_domain_id": related_id}}]}}
        elif scope == 3:
            if not related_id:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_business_id": str(scope)}}]}}
            else:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_business_id": related_id}}]}}
        elif scope == 4:
            if not related_id:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_location_id": str(scope)}}]}}
            else:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_location_id": related_id}}]}}
        elif scope == 5:
            if not related_id:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_organization_id": "1"}}]}}
            else:
                return {"bool": {"must": [{"term": {"dim_scope": scope}}, {"term": {"related_asset_organization_id": related_id}}]}}
        else:
            return None

    def get_score(self, scope, related_id=None):
        """Get recent score for dim scope
        
        :param scope: scope name
        :param related_id: scope id
        :return: scope score 
        """
        dim = self._dims.get(scope, None)
        assert dim is not None
        payload = self._gen_score_payload(dim, related_id)
        assert payload is not None
        uri = self._console_url + '/api/node/asset/score/recent'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']


class AssetBusiness(object):
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
        """List asset business

        :return: asset business list
        """

        payload = {'paginate': False}
        uri = self._console_url + "/asset/business/query"

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get asset business by id

        :param id: asset business id
        :return: asset business info dict
        """

        uri = self._console_url + "/asset/business/" + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name, **kwargs):
        """Get asset business by name

        :param name: asset business name
        :return: asset business info dict
        """

        unit_list = self.list()
        ret_a = [unit for unit in unit_list if unit['name'] == name]
        if len(ret_a) <= 1:
            return ret_a[0]
        path = kwargs.pop('path', None)
        if path is not None:
            return [unit for unit in ret_a if unit['namePath'] == path][0]
        else:
            return ret_a[0]


    def create_by_data(self, data):
        """Create asset business by data

        :param data: asset business data
        :return: asset business id
        """

        uri = self._console_url + "/asset/business"
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name=None, description=None, parent_name=None, data=None, **kwargs):
        """Create asset business

        :param name: refer to name. required
        :param description: refer to description, optional
        :param parent_name: parentId related, required
        :param data: stereotypes of the parameters, do not need to construct.
        :param kwargs: other attrs
        :return: asset business id
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
        """Update asset business

        :param id: asset business id
        :param data: update data
        :param kwargs: optional arguments to update asset business
        :return: None
        """

        uri = self._console_url + "/asset/business/" + id
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
        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete asset business

        :param id: asset business id
        :return: None
        """

        uri = self._console_url + '/asset/business/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)


class AssetDomain(object):
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
        """List asset domain

        :return: asset domain list
        """

        payload = {'paginate': False}
        uri = self._console_url + "/asset/domain/query"

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get asset domain by id

        :param id: asset domain id
        :return: asset domain info dict
        """

        uri = self._console_url + "/asset/domain/" + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name, **kwargs):
        """Get asset domain by name

        :param name: asset domain name
        :return: asset domain info dict
        """

        unit_list = self.list()
        ret_a = [unit for unit in unit_list if unit['name'] == name]
        if len(ret_a) <= 1:
            return ret_a[0]
        path = kwargs.pop('path', None)
        if path is not None:
            return [unit for unit in ret_a if unit['namePath'] == path][0]
        else:
            return ret_a[0]

    def create_by_data(self, data):
        """Create asset domain by data

        :param data: asset domain data
        :return: asset domain id
        """

        uri = self._console_url + "/asset/domain"
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name=None, description=None, parent_name=None, data=None, **kwargs):
        """Create asset domain

        :param name: refer to name. required
        :param description: refer to description, optional
        :param parent_name: parentId related, required
        :param data: stereotypes of the parameters, do not need to construct.
        :param kwargs: other attrs
        :return: asset domain id
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
        """Update asset domain

        :param id: asset domain id
        :param data: update data
        :param kwargs: optional arguments to update asset domain
        :return: None
        """

        uri = self._console_url + "/asset/domain/" + id
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
        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete asset domain

        :param id: asset domain id
        :return: None
        """

        uri = self._console_url + '/asset/domain/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)


class AssetLocation(object):
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
        """List asset location

        :return: asset location list
        """

        payload = {'paginate': False}
        uri = self._console_url + "/asset/location/query"

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get asset location by id

        :param id: asset location id
        :return: asset location info dict
        """

        uri = self._console_url + "/asset/location/" + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name, **kwargs):
        """Get asset location by name

        :param name: asset location name
        :return: asset location info dict
        """

        unit_list = self.list()
        ret_a = [unit for unit in unit_list if unit['name'] == name]
        if len(ret_a) <= 1:
            return ret_a[0]
        path = kwargs.pop('path', None)
        if path is not None:
            return [unit for unit in ret_a if unit['namePath'] == path][0]
        else:
            return ret_a[0]

    def create_by_data(self, data):
        """Create asset location by data

        :param data: asset location data
        :return: asset location id
        """

        uri = self._console_url + "/asset/location"
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name=None, description=None, parent_name=None, data=None, **kwargs):
        """Create asset location

        :param name: refer to name. required
        :param description: refer to description, optional
        :param parent_name: parentId related, required
        :param data: stereotypes of the parameters, do not need to construct.
        :param kwargs: other attrs
        :return: asset location id
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
        """Update asset location

        :param id: asset location id
        :param data: update data
        :param kwargs: optional arguments to update asset location
        :return: None
        """

        uri = self._console_url + "/asset/location/" + id
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
        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete asset location

        :param id: asset location id
        :return: None
        """

        uri = self._console_url + '/asset/location/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)