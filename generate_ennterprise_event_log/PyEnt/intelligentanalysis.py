# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time

from datetime import datetime, date, timedelta
import logging

log = logging.getLogger(__name__)


class IntelligentAnalysis(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def get_relation_chart_data(self, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """Get alarm relation chart data

        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        uri = self._console_url + '/alarm/analysis/relation/getRelationChartData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_chord_chart_data(self, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """Get alarm chord chart data

        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        uri = self._console_url + '/alarm/analysis/chord/getChordChartData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_river_chart_data(self, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """Get alarm river chart data

        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        uri = self._console_url + '/alarm/analysis/river/getRiverChartData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_cascade_data(self, start_time=date.today(), end_time=date.today() + timedelta(days=1), flag=2):
        """Get alarm cascade data

        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :param flag: do not know, default is 2
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
            'flag': flag
        }
        uri = self._console_url + '/alarm/analysis/cascade/getCascadeData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_alarm_type_chart_data(self, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """Get alarm multi-dim tree data

        :param start_time: start date, default is today
        :param end_time: end date, default is tomorrow
        :return: data
        """
        payload = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        uri = self._console_url + '/alarm/analysis/type/getAlarmTypeChartData'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']