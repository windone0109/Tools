# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time

from datetime import datetime, date, timedelta
import logging

log = logging.getLogger(__name__)


class Alarm(object):
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
        """Get alarm init params
        
        :return: alarm init info dict, keys: attrDatasMap, dynamicOptionDatasMap, operationMap, optionDatasMap and referOptionDatasMap
        """
        uri = self._console_url + '/alarm/search/getInitParams'

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['alarmAttrsMap']

    def get_alarm_option_data(self):
        """Get alarm option data info
        
        :return: alarm option data info dict, keys: alarm_focus, alarm_level, alarm_stage, alarm_status, alarm_type
        """
        return self.init_param()['optionDatasMap']

    def get_filter_options(self):
        ret_list = []
        alarm_attr = self.init_param()['attrDatasMap']
        for i in alarm_attr:
            ret_list.append(alarm_attr[i]['value'])
        ret_list.append('rule_type')
        return ret_list

    def list(self, start_time=date.today(), end_time=date.today() + timedelta(days=1), filter_expression=None):
        """Get alarm list
        
        :param start_time: query start time
        :param end_time: query end time
        :return: merged alarm list
        """
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')

        payload = {
            'paginate': False,
            'alarmScene': {
                #'commonFilters': {},
                'startTime': convert_date_time(start_time),
                'endTime': convert_date_time(end_time) - 1,
            }
        }
        if filter_expression:
            payload['alarmScene']['commonFilters'] = dict(FilterExpression = filter_expression)
        uri = self._console_url + '/api/node/alarm/list'
        print uri
        print payload
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get_detail(self, id):
        """Get detail alarm info
        
        :param id: alarm id
        :return: alarm detail info, compare to list, srcCity is added, totally 25 attrs
        """
        #payload = {'alarmId': str(id)}
        uri = self._console_url + '/api/node/alarm/detail/' + str(id)
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_alarm_detail_list(self, alarm_key, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """Get alarm detail list, ent 3.5 use
        
        :param alarm_key: alarm key
        :param start_time: start time
        :param end_time: end time
        :return: alarm list
        """
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')

        payload = {
            'alarmKey': alarm_key,
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        uri = self._console_url + '/api/node/alarm/detailList'
        response = self._session.get(uri, params=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get_event_detail_list(self, node_chain, event_ids):
        """get event list for specific alarm, ent 3.5 use
        
        :param node_chain: node id
        :param event_ids: event ids
        :return: event list
        """
        payload = {
            'id': event_ids,
            'nodeChain': node_chain,
        }
        uri = self._console_url + '/api/node/alarm/eventList'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get_original_trace(self, org_id, org_info):
        """Get original trace asset and event for original alarm
        
        :param org_id: original alarm id
        :param org_info: original alarm info
        :return: original asset list and event list traced
        """
        payload = {
            'paginate': True,
            'pagination': {'page': 1, 'pageSize': 10},
            'sorts': [],
            'alarmId': org_id,
            "startTime": org_info['start_time'],
            "endTime": org_info['end_time'],
            'traceType': 'event'
        }
        uri = self._console_url + '/alarm/search/original/trace'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        event = response_content['data']['list']

        payload['traceType'] = 'asset'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        asset = response_content['data']['list']

        return asset, event

    def filter(self, **kwargs):
        """Get filtered alarm list 
        
        :param kwargs: filter conditions, and operation
        :return: alarm info generator
        """
        alarm_list = self.list()
        for alarm in alarm_list:
            object_valid = True
            for key, value in kwargs.iteritems():
                alarm_val = alarm.get(key, None)
                if alarm_val is None:
                    object_valid = False
                    continue
                if alarm_val != value:
                    object_valid = False
                    continue
            if object_valid:
                yield alarm

