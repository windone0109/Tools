# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check


import logging
log = logging.getLogger(__name__)


class AttackType(object):
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
        """Get all attack type

        :return: attack type list
        """

        uri = self._console_url + '/security/attackType/query'
        payload = {'paginate': False}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get attacktype by id

        :param id: attacktype id
        :return: attacktype info dict
        """

        uri = self._console_url + '/security/attackType/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get attacktype by name

        :param name: attacktype name
        :return: attacktype info dict
        """

        attack_list = self.list()
        return [attack for attack in attack_list if attack['name'] == name][0]

    def create_by_data(self, data):
        """Create attack type by data

        :param data: create data
        :return: attack type id
        """
        uri = self._console_url + '/security/attackType'
        response = self.session.put(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['id']

    def create(self, name=None, description=None, parent_name=None, data=None, **kwargs):
        """Create attack type

        :param name: type name, required
        :param description: description
        :param parent_name: parent type name, required
        :param data: create data
        :param kwargs: other opts
        :return: attack type id
        """
        if data:
            create_data = data
        else:
            assert name
            assert parent_name
            parent_info = self.get_by_name(parent_name)
            parent_id = parent_info['id']
            create_data = {
                'name': name,
                'parentId': parent_id
            }
            if description:
                create_data['description'] = description
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update attack type id

        :param id: attack type id
        :param data: update data
        :param kwargs: update opts
        :return: None
        """
        uri = self._console_url + '/security/attackType/' + id
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
        response = self._session.post(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete attack type by id

        :param id: attack id need to delete
        :return: None
        """
        uri = self._console_url + '/security/attackType/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)


class Attack(object):
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
        """Get all attacks

        :return: attack list
        """

        uri = self._console_url + '/security/attack/query'
        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get attack by id

        :param id: attack id
        :return: attack info dict
        """

        uri = self._console_url + '/security/attack/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get attack by name

        :param name: attack name
        :return: attack info dict
        """

        attack_list = self.list()
        return [attack for attack in attack_list if attack['name'] == name][0]

    def create_by_data(self, data):
        """Create attack

        :param data: attack data
        :return: attack id
        """

        uri = self._console_url + '/security/attack'
        response = self._session.put(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name=None, description=None, type_name=None, data=None, **kwargs):
        """Create attack
        
        :param name: attack name, required
        :param description: desc, required
        :param type_name: attack type name, required
        :param data: create data
        :param kwargs: other opts
        :return: create id
        """
        if data:
            create_data = data
        else:
            assert name
            assert description
            assert type_name
            _attack_type = AttackType(self._console_url, self._session)
            attack_type_id = _attack_type.get_by_name(type_name)['id']
            create_data = {
                'name': name,
                'description': description,
                'attackName': type_name,
                'typeId': attack_type_id
            }
            incidence = kwargs.pop('incidence', None)
            solution = kwargs.pop('solution', None)
            attachment = kwargs.pop('attachment', None)
            if incidence:
                create_data['incidence'] = incidence
            if solution:
                create_data['solution'] = solution
            if attachment:
                attachment_str = ',' + ','.join(attachment)
                create_data['attachmentss'] = attachment_str
                create_data['addAttachmentss'] = attachment_str

        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update attack info
        
        :param id: attack id
        :param data: update data
        :param kwargs: optional keywords
        :return: None
        """
        uri = self._console_url + '/security/attack/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            attack_name = kwargs.pop('name', None)
            desc = kwargs.pop('description', None)
            incidence = kwargs.pop('incidence', None)
            solution = kwargs.pop('solution', None)
            attachment_add = kwargs.pop('attachment_add', None)
            attachment_del = kwargs.pop('attachment_del', None)
            if attack_name:
                update_data['name'] = attack_name
            if desc:
                update_data['description'] = desc
            if incidence:
                update_data['incidence'] = incidence
            if solution:
                update_data['solution'] = solution
            if attachment_add:
                update_data['addAttachmentss'] = ','.join(attachment_add)
            if attachment_del:
                update_data['deleteAttachmentss'] = ','.join(attachment_del)
                # other kwargs handler

        response = self._session.post(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete attack by id

        :param id: attack id
        :return: None
        """

        uri = self._console_url + '/security/attack/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all attacks

        :return: None
        """

        attack_list = self.list()
        for attack in attack_list:
            try:
                self.delete(attack['id'])
            except Exception as ex:
                pass

    def upload_file(self, local_file):
        """Upload local file to attack database

        :param local_file: localfile need to update
        :return: upload info dict
        """
        uri = self._console_url + '/security/attack/uploadAttachment'
        import os
        multiple_files = [
            ('attachment', (os.path.basename(local_file), open(local_file, 'rb'), 'multipart/form-data'))]
        response = self._session.post(uri, files=multiple_files)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def download_file(self, file_id, local_file):
        """download file to local

        :param local_file: localfile need to store
        :return: None
        """
        uri = self._console_url + '/security/attack/downloadAttachment/' + file_id
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)

        with open(local_file, 'wb') as pf:
            pf.write(response.content)
