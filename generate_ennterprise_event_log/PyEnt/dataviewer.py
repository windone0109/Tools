# -*- coding: utf-8 -*-

import json
import codecs
import re
from .assettype import AssetType
from ._internal_utils import status_code_check, response_status_check

import logging

log = logging.getLogger(__name__)


class DVCollector(object):
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
        """Get all collectors

        :return: collector list
        """
        uri = self._console_url + "/dv/collector"
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.get(uri, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content

    def get_by_id(self, id):
        """Get collector by id

        :param id: collector id
        :return: collector info dict
        """
        collector_list = self.list()
        return [collector for collector in collector_list if collector['id'] == id][0]

    def get_worker_status(self, id):
        """Get worker status 
        
        :param id: worker id
        :return: worker status, RUNNING if work normally
        """
        collector_list = self.list()
        return [collector for collector in collector_list if collector['id'] == id][0]['status']


class DVParser(object):
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
        """Get all parsers in dv
        
        :return: parser list
        """
        uri = self._console_url + '/dv/resolver'
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.get(uri, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        return response_content

    def get(self, id):
        """Get parser by id
        
        :param id: parser id
        :return: parser info dict
        """
        uri = self._console_url + '/dv/resolver/' + id
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.get(uri, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        return response_content

    def get_by_name(self, name):
        """Get parser by name
        
        :param name: parser name
        :return: parser info dict
        """
        parsers = self.list()
        return [parser for parser in parsers if parser['name'] == name][0]

    def preview(self, data):
        """Preview for dv, get properties attr
        
        :param data: parser and normalize info dict for a parser
        :return: properties attr
        """
        uri = self._console_url + '/dv/previewer'
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.post(uri, json=data, headers=header)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        return response_content

    def create_by_data(self, data):
        """Create parser by data
        
        :param data: parser data, need to get preview info first
        :asset_type: asset type
        :return: parser id and name tuple
        """
        uri = self._console_url + '/dv/resolver'
        header = {'Content-Encoding': 'UTF-8'}
        response = self._session.post(uri, json=data, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])
        # u'保存成功，解析规则[id=6fc4b5a1-f125-42a8-81c4-7016e5163fce, 名称=test3]'
        ptn = re.compile(u'保存成功，解析规则\[id=(.+), 名称=(.+)\]')
        res = ptn.search(response_content['message'])
        if res:
            return res.groups()
        else:
            raise Exception('save parser failed')

    def create(self, data, asset_type_name='Linux'):
        """Create parser by data
        
        :param data: parser info data
        :return: parser id and name tuple
        """
        _asset_type = AssetType(self._console_url, self._session)
        asset_type = _asset_type.get_by_name(asset_type_name)
        data['assetType'] = {
            "name": asset_type_name,
            "id": asset_type['id'],
        }
        preview = dict()
        preview['parser'] = [[data["sample"], ], data["parser"]]
        preview['normalize'] = data["normalize"]
        properties = self.preview(preview)
        data['properties'] = properties
        return self.create_by_data(data)

    def create_by_file(self, local_file, name=None):
        """Create parser by file
        
        :param local_file: parser file
        :param name: parser name
        :return: parser id and name tuple
        """
        with codecs.open(local_file, 'r', 'utf-8') as pf:
            content = pf.read().strip()
        parser_dict = json.loads(content)
        if name:
            parser_dict['name'] = name
        return self.create_by_data(parser_dict)

    def delete(self, id):
        """Delete parser by id
        
        :param id: parser id
        :return: None
        """
        uri = self._console_url + '/dv/resolver/' + id
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.delete(uri, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])

    def delete_by_name(self, name):
        """Delete parser by name
        
        :param name: parser name
        :return: None
        """
        parser_id = self.get_by_name(name)['id']
        self.delete(parser_id)

    def delete_all(self):
        """Delete all parsers

        :return: None
        """

        for parser in self.list():
            try:
                self.delete(parser['id'])
            except Exception as ex:
                pass

    def update(self, id, data=None, **kwargs):
        """Update parser

        :param id: parser id
        :param data: update data
        :param kwargs: optional data
        :return: 
        """
        uri = self._console_url + '/dv/resolver'
        header = {'Content-Encoding': 'UTF-8'}
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            if name:
                update_data['name'] = name
                # other kwargs handler

        response = self._session.post(uri, json=update_data, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])


class DVSource(object):
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
        """Get all datasources in dv
        
        :return: datasource list
        """
        uri = self._console_url + '/dv/datasource'
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.get(uri, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        return response_content

    def get(self, id):
        """Get datasource info by id
        
        :param id: datasource id
        :return: datasource info dict
        """
        uri = self._console_url + '/dv/datasource/' + id
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.get(uri, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        return response_content

    def get_by_name(self, name):
        """Get datasource info by name
        
        :param name: datasource name
        :return: None
        """
        parsers = self.list()
        return [parser for parser in parsers if parser['name'] == name][0]

    def create(self, name=None, collector=None, resolver=None, source_data=None, data=None, **kwargs):
        """Create datasource
        
        :param name: datasource name
        :param collector: collector id
        :param resolver: parser name
        :param source_data: source data info dict
        :param data: create data
        :param kwargs: optional info
        :return: None
        """
        if data:
            create_data = data
        else:
            assert name
            assert collector
            assert resolver
            assert source_data
            _parser = DVParser(self._console_url, self._session)
            # need to use assetType id and name
            _parser_info = _parser.get_by_name(resolver)
            assert _parser_info
            create_data = {
                "name": name,
                "collectorId": collector,
                "resolverId": _parser_info["id"],
                "assetTypeId": _parser_info["assetType"]["id"],
                "assetTypeName": _parser_info["assetType"]["name"],
                "assetType": {
                    "name": _parser_info["assetType"]["name"],
                    "id": _parser_info["assetType"]["id"],
                },
                "data": source_data,
                "writers": [{
                    "id": "es",
                    "name": "ES"
                }, {
                    "id": "kafka",
                    "name": "KAFKA"
                }],
                "properties": {
                    "polling_ms": "1000",
                    "timeout_ms": "100"
                },
            }
        return self.create_by_data(create_data)

    def create_by_data(self, data):
        """Create datasource by data
        
        :param data: datasource info data
        :return: None
        """
        uri = self._console_url + '/dv/datasource'
        header = {'Content-Encoding': 'UTF-8'}
        response = self._session.post(uri, json=data, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])

    def create_by_file(self, local_file, collector, resolver, name=None):
        """Create datasource by file
        
        :param local_file: local file
        :param collector: collector id
        :param resolver: parser name
        :param name: datasource name
        :return: None
        """
        with codecs.open(local_file, 'r', 'utf-8') as pf:
            content = pf.read().strip()
        parser_dict = json.loads(content)
        parser_dict['collectorId'] = collector
        _parser = DVParser(self._console_url, self._session)
        # need to use assetType id and name
        _parser_info = _parser.get_by_name(resolver)
        parser_dict['resolverId'] = _parser_info["id"]
        parser_dict['assetTypeId'] = _parser_info["assetType"]["id"]
        parser_dict['assetTypeName'] = _parser_info["assetType"]["name"]
        parser_dict['assetType'] = {
                "name": _parser_info["assetType"]["name"],
                "id": _parser_info["assetType"]["id"],
            }
        if name:
            parser_dict['name'] = name
        return self.create_by_data(parser_dict)

    def start(self, id):
        """Start datasource by id
        
        :param id: datasource id
        :return: None
        """
        status = self.get(id)['status']
        if status == "RUNNING":
            print id, " is running, need not to start"
            return
        payload = {
            'opt': 'start',
            'id': id,
        }
        uri = self._console_url + '/dv/config/start/' + id
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.put(uri, json=payload, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])

    def start_by_name(self, name):
        """Start datasource by name
        
        :param name: datasource name
        :return: None
        """
        s = self.get_by_name(name)
        self.start(s['id'])

    def stop(self, id):
        """Stop datasource by id
        
        :param id: datasource id
        :return: None
        """
        status = self.get(id)['status']
        if status == "STOPPED":
            print id, " is stopped, need not to stop"
            return
        payload = {
            'opt': 'stop',
            'id': id,
        }
        uri = self._console_url + '/dv/config/stop/' + id
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.put(uri, json=payload, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])

    def stop_by_name(self, name):
        """Stop datasource by name
        
        :param name: datasource name
        :return: None
        """
        s = self.get_by_name(name)
        self.stop(s['id'])

    def delete(self, id):
        """Delete datasource by id
        
        :param id: datasource id
        :return: None
        """
        uri = self._console_url + '/dv/datasource/' + id
        header = {'Content-Encoding': 'UTF-8'}

        response = self._session.delete(uri, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])

    def delete_by_name(self, name):
        """Delete datasource by name
        
        :param name: datasource name
        :return: None
        """
        source_id = self.get_by_name(name)['id']
        self.delete(source_id)

    def delete_all(self):
        """Delete all datasources

        :return: None
        """

        for ds in self.list():
            try:
                self.delete(ds['id'])
            except Exception as ex:
                pass

    def stop_delete_all(self):
        """Stop and delete all datasources
        
        :return: None
        """
        import time
        for ds in self.list():
            try:
                self.stop(ds['id'])
                time.sleep(5)
                self.delete(ds['id'])
                time.sleep(5)
            except Exception as ex:
                pass

    def update(self, id, data=None, **kwargs):
        """Update datasource
        
        :param id: datasource id
        :param data: update data
        :param kwargs: optional data
        :return: 
        """
        uri = self._console_url + '/dv/datasource'
        header = {'Content-Encoding': 'UTF-8'}
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            if name:
                update_data['name'] = name
                # other kwargs handler

        response = self._session.post(uri, json=update_data, headers=header)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['status'], '200', response_content['message'])