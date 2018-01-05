# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time
from datetime import datetime, date, timedelta

import logging

log = logging.getLogger(__name__)


class AuditLog(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def query(self, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """query all audit logs
        
        :param start_time: query start time
        :param end_time: query end time
        :return: audit log list
        """
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')
        audit_log = {
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        payload = {'paginate': False, 'auditLog': audit_log,'pagination': {}, 'sorts': []}
        uri = self._console_url + '/system/audit_log/query'

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']