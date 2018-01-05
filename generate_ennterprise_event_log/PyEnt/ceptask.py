# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time
from .ceprule import CepRule

from datetime import datetime, date, timedelta
import logging
log = logging.getLogger(__name__)

class CepTask(object):
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
        """Get all cep tasks

        :return: cep task list
        """

        uri = self._console_url + '/api/cep/tasks'
        response = self._session.get(uri)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get_by_name(self, name):
        """Get task by name

        :param name: task name
        :return: task info dict
        """

        task_list = self.list()
        return [task for task in task_list if task['name'] == name][0]

    def create_by_data(self, data):
        """Create cep history task by data

        :param data: cep task data
        :return: None
        """

        uri = self._console_url + '/api/cep/tasks'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 201)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])

        #return response_content['data']['id']

    def create(self, name=None, description='', cron_time='', rule_list=[],
               begin_time=date.today() + timedelta(days=-7), end_time=date.today(), data=None, **kwargs):
        """Create cep task
        
        :param name: task name, required
        :param description: description, optional
        :param cron_time: refer to cron, if empty, start now, cron format example: 0 0 12 19 6 ? 2017
        :param rule_list: cep rule name list, required
        :param begin_time: begin time, required, default is a week ago
        :param end_time: end time, required, default is now
        :param data: create data
        :param kwargs: other keywords
        :return: None
        """
        if data:
            create_data = data
        else:
            assert name
            assert rule_list
            rules = []
            _cep_rules = CepRule(self._console_url, self._session)
            for rule in rule_list:
                rules.append(_cep_rules.get_by_name(rule)['id'])
            create_data = {
                'name': name,
                'description': description,
                'cron': cron_time,
                'beginTime': convert_date_time(begin_time),
                'endTime': convert_date_time(end_time),
                'relativeRule': rules
            }
            return self.create_by_data(create_data)

    def delete(self, id):
        """Delete task by id

        :param id: task id
        :return: None
        """

        uri = self._console_url + '/api/cep/tasks/' + str(id)
        response = self._session.delete(uri)
        status_code_check(response.status_code, 204)
