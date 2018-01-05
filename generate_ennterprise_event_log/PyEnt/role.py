import json

from ._internal_utils import status_code_check, response_status_check

import logging

log = logging.getLogger(__name__)


class Role(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def get_menu(self):
        """Get current menu and submenu info
        
        :return: menu list
        """
        uri = self._console_url + "/api/node/system/menus"

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['menus']

    def get_children_menu_list(self):
        """Get current submenu list
        
        :return: menu list
        """
        menus = self.get_menu()
        menu_list = []
        for menu in menus:
            if 'children' in menu:
                ids = [child['id'] for child in menu['children']]
                menu_list.extend(ids)
            else:
                menu_list.append(menu['id'])
        return menu_list

    def list(self):
        """Get all roles

        :return: user list
        """

        payload = {'paginate': False, 'pagination': {}}
        uri = self._console_url + "/api/node/system/roles"

        response = self._session.get(uri, params=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get role info by id
        
        :param id: role id
        :return: role info dict
        """
        uri = self._console_url + '/api/node/system/roles/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)
        print response.content
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get role info by role name

        :param name: role name
        :return: role info dict
        """

        role_list = self.list()
        return [role for role in role_list if role['name'] == name][0]

    def create_by_data(self, data):
        """Create role by data
        
        :param data: create data
        :return: None, better to return id
        """
        uri = self._console_url + '/api/node/system/roles'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        #return response_content['data']['id']

    def create(self, name=None, description=None, menu=[], data=None, **kwargs):
        """Create role
        
        :param name: role name
        :param description: role description
        :param menu: menu list, item is dict, key is id and allow_type, 10 means r, 20 means rw
        :param data: create data
        :param kwargs: other args
        :return: None
        """
        if data:
            create_data = data
        else:
            assert name
            assert menu
            create_data = {
                'name': name,
                'description': description,
                'menus': menu
            }
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update role

        :param id: role id
        :param data: role data
        :param kwargs: optional arguments to update role
        :return: None
        """

        uri = self._console_url + '/api/node/system/roles/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            description = kwargs.pop('description', None)
            menus = kwargs.pop('menus', None)
            if name:
                update_data['name'] = name
            if description:
                update_data['description'] = description
            if menus is not None:
                update_data['menus'] = menus
                # other kwargs handler

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete role by id

        :param id: role id
        :return: None
        """

        uri = self._console_url + '/api/node/system/roles/' + id
        response = self._session.delete(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete_all(self):
        """Delete all roles

        :return: None
        """

        role_list = self.list()
        for role in role_list:
            try:
                self.delete(role['id'])
            except Exception as ex:
                print 'delete role exception', role['id']

