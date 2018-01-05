# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check
from ._internal_utils import CollectorType, Charset

from .eventparser import EventParser

import logging
log = logging.getLogger(__name__)


class Collector(object):
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

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + "/system/event/collector/query"

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get collector by id

        :param id: collector id
        :return: collector info dict
        """

        uri = self._console_url + "/system/event/collector/" + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get collector by name
        
        :param name: collector name
        :return: collector info dict
        """

        collector_list = self.list()
        return [collector for collector in collector_list if collector['collectorName'] == name][0]

    def create_by_data(self, data):
        """Create a collector by data

        :param data: collector data
        :return: collector id
        """

        uri = self._console_url + "/system/event/collector"
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, name, type, host_address, charset, parser_rules=None):
        """Create a collector

        :param name: refer to collectorName, required
        :param type: refer to collectorType, required
        :param host_address: refer to hostAddress, required
        :param charset: refer to logCharset, required
        :param parser_rules: refer to parseRules, optional
        :return: collector id
        """

        uri = self._console_url + "/system/event/collector/"

        assert name
        assert host_address

        collector_type = CollectorType.get(type, None)
        assert collector_type
        charset = Charset.get(charset, None)
        assert charset

        parser_rules = parser_rules or []

        create_data = {
            'collectorName': name,
            'collectorType': collector_type,
            'hostAddress': host_address,
            'logCharset': charset,
            'parseRules': []
        }

        _event_parser = EventParser(self._console_url, self._session)
        for parser_rule in parser_rules:
            create_data['parseRules'].append(_event_parser.get(parser_rule))

        return self.create_by_data(create_data)

    def delete(self, id):
        """Delete collector

        :param id: collector id
        :return: None
        """

        uri = self._console_url + "/system/event/collector/" + id
        response = self._session.delete(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all collectors

        :return: None
        """

        for collector in self.list():
            try:
                self.delete(collector['id'])
            except Exception as ex:
                pass

    def update(self, id, data=None, **kwargs):
        """Update collector info
        
        :param id: collector id
        :param data:  collector data
        :param kwargs: optional arguments to update asset type
        :return: None
        """
        uri = self._console_url + "/system/event/collector/" + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            rule_name = kwargs.pop('name', None)
            rule_type = kwargs.pop('type', None)
            host_address = kwargs.pop('host_address', None)
            charset = kwargs.pop('charset', None)
            parser_rules = kwargs.pop('parser_rules', [])

            if rule_name:
                update_data['collectorName'] = rule_name
            if rule_type:
                update_data['collectorType'] = rule_type
            if host_address:
                update_data['hostAddress'] = host_address
            if charset:
                update_data['logCharset'] = charset

            if parser_rules:
                update_data['parseRules'] = []
                _event_parser = EventParser(self._console_url, self._session)
                for parser_rule in parser_rules:
                    update_data['parseRules'].append(_event_parser.get(parser_rule))

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

