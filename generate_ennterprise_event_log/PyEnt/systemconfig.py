import json
import hashlib

from ._internal_utils import status_code_check, response_status_check

import logging

log = logging.getLogger(__name__)

class SMTP(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def get(self):
        """Get SMTP server info
        
        :return: SMTP server info dict, better to check status
        """
        uri = self._console_url + '/system/config/smtp'
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])
        #return response_content['data']
        return response_content

    def update(self, data=None, **kwargs):
        """Update SMTP server info
        
        :param data: SMTP data
        :param kwargs: optional arguments to update SMTP
        :return: None, better to check status
        """
        uri = self._console_url + '/system/config/smtp'
        if data:
            update_data = data
        else:
            update_data = self.get()
            host = kwargs.pop('host', None)
            port = kwargs.pop('port', None)
            username = kwargs.pop('username', None)
            password = kwargs.pop('password', None)
            if host:
                update_data['host'] = host
            if port is not None:
                update_data['port'] = port
            if username:
                update_data['username'] = username
            if password:
                update_data['password'] = password

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])



class Intranet(object):
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
        """Get all intranet info

        :return: intranet list
        """

        uri = self._console_url + "/system/config/intranet"

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        intranet_list = response_content['data']
        for intranet in intranet_list:
            intranet['config'] = json.loads(intranet['config'])
        return intranet_list

    def get(self, id):
        """Get intranet info by id
        
        :param id: intranet id
        :return: intranet info dict
        """
        uri = self._console_url + '/system/config/intranet/' + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_by_name(self, name):
        """Get intranet info by name
        
        :param name: intranet name
        :return: in intranet info dict
        """
        intranet_list = self.list()
        return [intranet for intranet in intranet_list if intranet['config']['name'] == name][0]

    def create_by_data(self, data):
        """Create intranet by data
        
        :param data: intranet data
        :return: None, better to return intranet id created
        """
        uri = self._console_url + "/system/config/intranet"
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        #return response_content['data']['id']

    def create(self, name=None, intranet=None, longitude=None, latitude=None, data=None, **kwargs):
        """Create intranet
        
        :param name: name, refer to name
        :param intranet: intranet list, refer to intranet
        :param longitude: longitude, refer to longitude
        :param latitude: latitude, refer to latitude
        :param data: intranet data
        :param kwargs: other attrs
        :return: None
        """
        if data:
            create_data = data
        else:
            assert name
            assert intranet
            assert longitude is not None
            assert latitude is not None
            create_data = {
                'name': name,
                'geo': {
                    'longitude': longitude,
                    'latitude': latitude
                },
                'intranet': intranet
            }
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update intranet
        
        :param id: intranet id
        :param data: update data
        :param kwargs: optional arguments to update intranet
        :return: None
        """
        uri = self._console_url + '/system/config/intranet/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            longitude = kwargs.pop('longitude', None)
            latitude = kwargs.pop('latitude', None)
            intranet = kwargs.pop('intranet', None)
            if name:
                update_data['name'] = name
            if longitude is not None:
                update_data['geo']['longitude'] = longitude
            if latitude is not None:
                update_data['geo']['latitude'] = latitude
            if intranet:
                update_data['intranet'] = intranet

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])


    def delete(self, id):
        """Delete intranet by id
        
        :param id: intranet id
        :return: None
        """
        uri = self._console_url + "/system/config/intranet/" + id
        response = self._session.delete(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)


class InitConfig(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self._types = {
            'event': ['Event'],
            'parser': ['Event', 'ParseRule'],
            'intelligence': ['Intelligence'],
            'knowledge': ['Knowledge_AttackData'],
            'cep': ['Event', 'Intelligence', 'CEP_Analysis'],
            'component': ['Component'],
            'dashboard': ['Component', 'Dashboard'],
        }

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def import_module(self, local_file):
        """Import information
        
        :param local_file: local file to import
        :return: None
        """
        uri = self._console_url + '/system/config/import'
        files = {'attachment': open(local_file, 'rb')}
        response = self._session.post(uri, files=files)
        response_content = json.loads(response.content)
        print response.content

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def export_module(self, local_file, args=[]):
        """Export information
        
        :param local_file: filename to store
        :param args: modules to export
        :return: None
        """
        uri = self._console_url + '/system/config/export/'
        modules = set()
        for i in args:
            j = self._types.get(i, None)
            if j:
                modules.update(j)
        uri = uri + ','.join(modules)
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        with open(local_file, 'wb') as pf:
            pf.write(response.content)

