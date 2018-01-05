# -*- coding: utf-8 -*-

import json
import hashlib

from ._internal_utils import status_code_check, response_status_check
from .systemunit import SystemUnit
from .role import Role
from .tool import generate_menu_item_dict

import logging
log = logging.getLogger(__name__)


class User(object):
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
        """Get all users
        
        :return: user list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + "/api/node/system/user/query"

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get user by id
        
        :param id: user id
        :return: user info dict
        """

        uri = self._console_url + '/api/node/system/user/' + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_by_name(self, name):
        """Get user info by user name
        
        :param name: user name
        :return: user info dict
        """

        user_list = self.list()
        return [user for user in user_list if user['loginName'] == name][0]

    def create_by_data(self, data):
        """Create user by data
        
        :param data: user data
        :return: None
        """

        uri = self._console_url + '/api/node/system/user'
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        #return response_content['data']['id']

    def create(self, login_name=None, real_name=None, password=None, unit_name=None,
               email=None, mobile=None, roles=None, data=None,**kwargs):
        """Create user
        
        :param login_name: refer to loginName, required
        :param real_name: refer to realName, required
        :param password: refer to loginPassword and repassword, required
        :param unit_name: refer to unitName, uiitId created by this, required
        :param email: refer to email
        :param mobile: refer to mobile
        :param roles: refer to roles, list format
        :param data: stereotypes of the parameters, do not need to construct.
        :param kwargs: other attrs
        :return: user id
        """

        if data:
            create_data = data
        else:
            assert login_name
            assert real_name
            assert password
            assert unit_name
            assert roles
            _system_unit = SystemUnit(self._console_url, self._session)
            unit_id = _system_unit.get_by_name(unit_name)['id']

            _role = Role(self._console_url, self._session)
            _role_list = [_role.get_by_name(r)['id'] for r in roles]

            m = hashlib.md5()
            m.update(password)

            create_data = {
                'loginName': login_name,
                'realName': real_name,
                'loginPassword': m.hexdigest(),
                'repassword': m.hexdigest(),
                'unitName': unit_name,
                'unitId': unit_id,
                'roles': _role_list,
                'email': '',
                'mobile': '',
            }
            if email:
                create_data['email'] = email
            if mobile:
                create_data['mobile'] = mobile
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update user
        
        :param id: user id
        :param data: update data
        :param kwargs: optional arguments to update user
        :return: None
        """

        uri = self._console_url + '/api/node/system/user/' + id
        if data:
            update_data = data
        else:
            login_name = kwargs.pop('login_name', None)
            password = kwargs.pop('password', None)
            real_name = kwargs.pop('real_name', None)
            unit_name = kwargs.pop('unit_name', None)
            roles = kwargs.pop('roles', None)
            email = kwargs.pop('email', None)
            mobile = kwargs.pop('mobile', None)

            update_data = self.get(id)
            if update_data['email'] is None:
                update_data['email'] = ''
            if update_data['mobile'] is None:
                update_data['mobile'] = ''

            role_list = []
            for r in update_data['roles']:
                role_list.append(r['id'])
            update_data['roles'] = role_list

            if login_name:
                update_data['loginName'] = login_name
            if password:
                m = hashlib.md5()
                m.update(password)
                update_data['loginPassword'] = m.hexdigest()
                update_data['repassword'] = m.hexdigest()
            else:
                update_data['loginPassword'] = ''
                update_data['repassword'] = ''
            if real_name:
                update_data['realName'] = real_name
            if unit_name:
                _system_unit = SystemUnit(self._console_url, self._session)
                unit_id = _system_unit.get_by_name(unit_name)['id']
                update_data['unitName'] = unit_name
                update_data['unitId'] = unit_id
            if roles:
                _role = Role(self._console_url, self._session)
                _role_list = [_role.get_by_name(r)['id'] for r in roles]
                update_data['roles'] = _role_list
            if email is not None:
                update_data['email'] = email
            if mobile is not None:
                update_data['mobile'] = mobile
        print update_data
        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def lock(self, id):
        """Lock user by id
        
        :param id: user id
        :return: None
        """

        uri = self._console_url + '/system/user/' + id + '/lock'
        response = self._session.put(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def unlock(self, id):
        """Unlock user by id
        
        :param id: user id
        :return: None
        """

        uri = self._console_url + '/system/user/' + id + '/unlock'
        response = self._session.put(uri)
        #print response.status_code, response.content
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def change_pwd(self, old_pwd, new_pwd):
        """Change user password
        
        :param old_pwd: old password
        :param new_pwd: new password
        :return: None
        """

        old_md5 = hashlib.new("md5", old_pwd).hexdigest()
        new_md5 = hashlib.new("md5", new_pwd).hexdigest()
        uri = self._console_url + '/api/node/system/change-password'
        payload = {
            'originalPassword': old_md5,
            'newPassword': new_md5,
            'confirmNewPassword': new_md5,
        }

        response = self._session.put(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete user
        
        :param id: user id
        :return: None
        """

        uri = self._console_url + '/api/node/system/user/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete user

        :param id: user id
        :return: None
        """

        user_list = self.list()
        for user in user_list:
            try:
                self.delete(user['id'])
            except Exception as ex:
                print 'delete user exception', user['id']

    def get_login_info(self):
        """Get current login info
        
        :return: login info dict, menu and user
        """
        uri = self._console_url + "/api/node/menus"

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content

    def get_login_user(self):
        """Get current login user info
        
        :return: login user info dict
        """
        return self.get_login_info()['user']

    def get_login_menu(self):
        """Get current login menu info
        
        :return:  login menu list
        """
        login_info = self.get_login_info()
        b_super = login_info['user']['superAdmin']
        menus = login_info['menus']
        menu_list = []
        for menu in menus:
            if 'children' in menu:
                for child in menu['children']:
                    if b_super:
                        menu_list.append(generate_menu_item_dict(child['id'], 20))
                    else:
                        menu_list.append(generate_menu_item_dict(child['id'], child['allow_type']))
            else:
                if b_super:
                    menu_list.append(generate_menu_item_dict(menu['id'], 20))
                else:
                    menu_list.append(generate_menu_item_dict(menu['id'], menu['allow_type']))
        return menu_list
