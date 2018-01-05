# -*- coding: utf-8 -*-

import json
import os
from ._internal_utils import status_code_check, response_status_check
from ._internal_utils import ParserType, MappingType
from .eventtype import EventType
from .assettype import AssetType
from .exceptions import InvalidAttribute

import logging
log = logging.getLogger(__name__)


class EventParser(object):
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
        """Get all event parsers

        :return: event parser list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + '/event/eventParser/query'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        print "list:",response_content['data']['list']
        return response_content['data']['list']

    def get(self, id):
        """Get event parser by id

        :param id: event parser id
        :return: event parser info dict
        """

        uri = self._console_url + '/event/eventParser/' + id
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_by_name(self, name):
        """Get event parser by name
        
        :param name: event parser name
        :return: event parser info dict
        """

        event_parser_list = self.list()
        return [event_parser for event_parser in event_parser_list if event_parser['parserName'] == name][0]

    def create_by_data(self, data):
        """Create event parser by data
        
        :param data: event parser data
        :return: event parser id
        """

        uri = self._console_url + '/event/eventParser'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create_by_file(self, rule_file, name=''):
        """Create event parser rule by file

        :param rule_file: event parser rule file
        :param name: event parser rule name replaced
        :return: None
        """
        with open(rule_file) as pf:
            content = pf.read().strip()
        rule_dict = json.loads(content)
        if name:
            rule_dict['parserName'] = name
        return self.create_by_data(rule_dict)

    def create(self, name=None, description='', event_type_name=None, asset_type_name=None, content=None,
               parser_type=None, regex=None, field_delimitor=None, kv_delimitor=None, preview_data=None,
               attri_mappings=None, data=None, **kwargs):
        """Create an event parser

        :param name: refer to parserName, required
        :param description: refer to description
        :param event_type_name: refer to eventTypeName, required, got eventType info by it
        :param asset_type_name: refer to assetName, required, got assert type info by it
        :param content: refer to orgEventContent, required
        :param parser_type: refer to parserType, two tpyes, regex, WELF_value
        :param regex: refer to regex, used by regex parser type
        :param field_delimitor: refer to fieldDelimitor, used by WELF_value parser type
        :param kv_delimitor: refer to kvDelimitor, used by WELF_value parser type
        :param preview_data: refer to previewData, optional
        :param attri_mappings: optional
        :param data: stereotypes of the parameters, do not need to construct.
        :param kwargs: other attrs
        :return: event parser id
        """

        if data:
            create_data = data
        else:
            assert name

            assert event_type_name
            _event_type = EventType(self._console_url, self._session)
            event_type = _event_type.get(_event_type.get_by_name(event_type_name)['id'])

            for event_attribute in event_type['attributes']:
                event_attribute['attrMapping'] = {'mappingIdx': ''}
                event_attribute['mappingList'] = []

            assert asset_type_name
            _asset_type = AssetType(self._console_url, self._session)
            asset_type = _asset_type.get_by_name(asset_type_name)

            assert content
            #assert preview_data
            #assert attri_mappings

            parser_type = ParserType.get(parser_type, None)
            assert parser_type
            index = 2
            if preview_data:
                index = len(preview_data)

            create_data = {
                'parserName': name,
                'description': description,
                'eventTypeId': event_type['id'],
                'eventTypeName': event_type_name,
                'assetIdPath': asset_type['idPath'],
                'assetName': asset_type_name,
                'attributes': event_type['attributes'],
                'orgEventContent': content,
                'index': index,
                'parserType': parser_type
            }

            if parser_type == 'regex':
                assert regex
                create_data['regex'] = regex
            elif parser_type == 'WELF_value':
                assert field_delimitor
                assert kv_delimitor
                create_data['fieldDelimitor'] = field_delimitor
                create_data['kvDelimitor'] = kv_delimitor
            else:
                raise NotImplementedError()
            if attri_mappings:
                for attri_mapping in attri_mappings:
                    # get attribute_name
                    attribute_name_filter = [attribute for attribute in create_data['attributes']
                                             if attribute['attrName'] == attri_mapping['attribute_name']]
                    #print attribute_name_filter
                    if not len(attribute_name_filter):
                        raise InvalidAttribute(attri_mapping['attribute_name'])
                    event_attribute = attribute_name_filter[0]
                    if 'default_value' in attri_mapping:#default value handler
                        event_attribute['attrMapping']['defaultVal'] = attri_mapping['default_value']

                    if 'parser_item' in attri_mapping:#attribute mapping index handler
                        parser_item_split = attri_mapping['parser_item'].split(',')
                        for i in parser_item_split:
                            if i not in preview_data:
                                raise Exception('Parser item not in preview data!')
                        event_attribute['attrMapping']['mappingIdx'] = attri_mapping['parser_item']

                    # if attri_mapping['parser_item'] not in preview_data:
                    #     raise Exception('Parser item not in preview data!')

                    if 'mappings' in attri_mapping:
                        for mapping in attri_mapping['mappings']:
                            mapping_type = MappingType.get(mapping['mapping_type'], None)
                            mapping_value = mapping.get('mapping_value', None)
                            mapping_key = mapping.get('mapping_key', None)
                            assert mapping_type
                            assert mapping_value
                            map_dict = {
                                'mappingType': mapping_type,
                                'mappingValue': mapping_value
                            }
                            if mapping_key:
                                map_dict['orgValue'] = mapping_key
                            event_attribute['mappingList'].append(map_dict)
        #print create_data
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update an event parser
        
        :param id: event parser id
        :param data: event parser data
        :param kwargs: event parser keywords
        :return: None
        """

        uri = self._console_url + '/event/eventParser/' + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('parserName', None)
            description = kwargs.pop('description', None)
            content = kwargs.pop('orgEventContent', None)
            parser_type = kwargs.pop('parserType', None)
            parser_type = ParserType.get(parser_type, None)

            update_data = self.get(id)
            if name:
                update_data['parserName'] = name
            if description:
                update_data['description'] = description
            if content:
                update_data['orgEventContent'] = content
            if parser_type:
                update_data['parserType'] = parser_type
            if parser_type == 'regex':
                regex = kwargs.pop('regex', None)
                if regex:
                    update_data['regex'] = regex
            elif parser_type == 'WELF_value':
                field_delimitor = kwargs.pop('fieldDelimitor', None)
                kv_delimitor = kwargs.pop('kvDelimitor', None)
                if field_delimitor:
                    update_data['fieldDelimitor'] = field_delimitor
                if kv_delimitor:
                    update_data['kvDelimitor'] = kv_delimitor
            else:
                pass

        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """ Delete event parser by id

        :param id: event parser id
        :return: None
        """

        uri = self._console_url + '/event/eventParser/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all event parsers
        
        :return: None
        """

        parser_list = self.list()
        for parser in parser_list:
            try:
                self.delete(parser['id'])
            except Exception as ex:
                pass

    def filter(self, **kwargs):
        pass

    def parse(self, id):
        """Get parse time
        
        :param id: parser id
        :return: parse time string
        """
        uri = self._console_url + '/event/eventParser/group'
        payload = self.get(id)
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['messages'][0]

    def import_parser(self, localfile, strategy='update'):
        """Import event parser from local
        
        :param localfile: local file
        :return: None
        """
        uri = self._console_url + '/parseRule/import/check'
        with open(localfile) as pf:
            content = pf.read()
        response = self._session.post(uri, data=content)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        conficts = response_content['data']
        uri = self._console_url + '/parseRule/import/'
        if conficts:
            strategies = {
                'rename': 'rename',
                'skip': 'skip',
                'update': 'update'
            }
            strategy = strategies.get(strategy, 'update')
            uri = uri + strategy
        else:
            uri = uri + 'add'
        response = self._session.post(uri, data=content)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return uri

    def export_parser(self, localfile, id_list=[]):
        """Export event parser to local
        
        :param localfile: local file to store event parser
        :param id_list: event parser id list need to export
        :return: None
        """
        uri_tmp = ''
        if id_list:
            uri_tmp = ','.join(id_list)
        else:
            uri_tmp = 'all'
        uri = self._console_url + '/parseRule/export/' + uri_tmp

        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        with open(localfile, 'wb') as pf:
            pf.write(response.content)


