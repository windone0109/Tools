# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time

from datetime import datetime, date, timedelta
import logging

log = logging.getLogger(__name__)


class EventAnalysis(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def get_relation_chart_data(self, start_time=date.today(), end_time=date.today()+timedelta(days=1), height=200, width=1000):
        """Get event relation chart data
        
        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :param height: chart height
        :param width: chart width
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
            'height': height,
            'width': width
        }
        uri = self._console_url + '/event/analysis/relation/getRelationChartData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_flow_chart_data(self, start_time=date.today(), end_time=date.today()+timedelta(days=1)):
        """Get event flow chart data
        
        :param start_time: start date, default is today 
        :param end_time: end date, default is tomorrow 
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time)
        }
        uri = self._console_url + '/event/analysis/flow/getFlowChartData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_river_chart_data(self, start_time=date.today(), end_time=date.today()+timedelta(days=1)):
        """
        
        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time)
        }
        uri = self._console_url + '/event/analysis/river/getRiverChartData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']