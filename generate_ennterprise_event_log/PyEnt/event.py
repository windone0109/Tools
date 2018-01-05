# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time

from datetime import datetime, date, timedelta
import logging

log = logging.getLogger(__name__)


class Event(object):
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
        uri = self._console_url + '/event/search/getInitParams'

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_col_show_list(self):
        return self.init_param()['scene']['colShowList']

    def get_col_show_string(self):
        return self.init_param()['scene']['colShow']

    def set_col_show(self, fields):
        _col_list = []
        _event_attr = EventAttribute(self._console_url, self._session)
        for field in fields:
            _col_list.append(_event_attr.create_event_field_by_name(field))
        uri = self._console_url + '/event/search/saveColShows'
        payload = {
            'colShows': _col_list,
        }
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def _create_event_field_by_name(self, name_list):
        """create event field dict by attribute name, for event query use

        :param name: attribute name, specially handled for event_content and original_log
        :return: event field dict
        """
        attr_list = self.init_param()['eventAttrsMap']['attrDatasMap']
        field_list = []
        for attr in attr_list.values():
            try:
                if attr['text'] in name_list:
                    field_list.append(attr)
                if len(field_list) == len(name_list):
                    break
            except:
                raise Exception('Get event attribute failed!')
        return field_list

    def list_header(self, start_time=date.today(), end_time=date.today()+timedelta(days=1),
                    fields=[u'发生时间',u'事件名称',u'事件级别',u'事件分类',u'源地址',u'目的地址',u'事件内容',u'原始日志'],
                    *args):
        """Get event list table header
        
        :param start_time: query start time
        :param end_time: query end time
        :param fields: query fields
        :param args: other optional args
        :return: table header
        """
        assert fields
        _col_list = self._create_event_field_by_name(fields)

        payload = {
            'scene':{
                'startTime': convert_date_time(start_time),
                'endTime': convert_date_time(end_time),
                'colShowList': _col_list
            }
        }
        uri = self._console_url + '/event/search/event/query'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['headerList']


    def list(self, start_time=date.today(), end_time=date.today()+timedelta(days=1),
                    fields=[u'发生时间',u'事件名称',u'事件级别',u'事件分类',u'源地址',u'目的地址',u'事件内容',u'原始日志'],
                     filter_expression=None, **kwargs):
        """Get event list
        
        :param start_time: query start time
        :param end_time: query end time
        :param fields: query fields
        :param kwargs: other optional args
        :return: event list
        """
        assert fields
        _col_list = self._create_event_field_by_name(fields)
        # _event_attr = EventAttribute(self._console_url,self._session)
        # for field in fields:
        #     _col_list.append(_event_attr.create_event_field_by_name(field))

        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')

        payload = {
            'page': 1,
            'pageSize': 1000,
            'scene': {
                'startTime': convert_date_time(start_time),
                'endTime': convert_date_time(end_time),
                'colShowList': _col_list,
            }
        }
        if filter_expression:
            payload['scene']['filters'] = dict(FilterExpression = filter_expression)
        uri = self._console_url + '/event/search/event/query'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get(self, id):
        """Get event by id
        
        :param id: event id
        :return: event info dict
        """
        payload = {
            'eventId': id,
        }
        uri = self._console_url + '/event/search/get'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def filter(self, **kwargs):
        """Get filtered event list 
        
        :param kwargs: filter conditions, and operation, key and value must come from realText and realVal in attrValueList
        :return: event info generator
        """
        event_list = self.list()
        for event in event_list:
            attr_value = event['attrValueList']
            object_valid = True
            for key, value in kwargs.iteritems():
                for item in attr_value:
                    real_txt = item.get('realText', None)
                    real_val = item.get('realVal', None)
                    if (real_txt is None) or (real_val is None):
                        continue
                    if real_txt != key:
                        continue
                    if real_val != value:
                        object_valid = False
            if object_valid:
                yield event