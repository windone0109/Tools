# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time, EntityType, ShareType, ReportFileFormat
from datetime import datetime, date, timedelta
import logging

log = logging.getLogger(__name__)


class TimeReport(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self._entity_type = EntityType['report']

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def list(self):
        """List all time reports

        :return: time report list
        """

        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        uri = self._console_url + '/report/reports/list'
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get(self, id):
        """Get time report by id

        :param id: time report id
        :return: time report info dict
        """

        uri = self._console_url + '/report/reports/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get time report by name

        :param name: time report name
        :return: time report info dict
        """

        report_list = self.list()
        return [report for report in report_list if report['name'] == name][0]

    def create_by_data(self, data):
        """Create report

        :param data: time report data
        :return: None
        """

        uri = self._console_url + '/report/reports'
        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        #return response_content['data']['id']

    def create(self, name=None, frequency=1, enabled=True, mail_enabled=False, recipients=[], templates=[], data=None, **kwargs):
        """Create time report
        
        :param name: report name
        :param frequency: report frequency, 1/2/3 means daily/weekly/monthly
        :param enabled: report enable
        :param mail_enabled: enable email
        :param recipients: email recipients, if mail_enabled is true, this cannot be empty
        :param templates: report template
        :param data: create data
        :param kwargs: other optional kwargs
        :return: None
        """
        if data:
            create_data = data
        else:
            assert name
            assert templates
            if frequency not in [1, 2, 3]:
                raise ValueError('invalid frequency parameter')
            if mail_enabled:
                assert recipients
            create_data = {
                'name': name,
                'frequency': frequency,
                'enabled': enabled,
                'mailEnabled': mail_enabled,
                'templates': templates,
                'recipients': recipients
            }

        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update report

        :param id: report id
        :param data: report data
        :param kwargs: optional arguments to update report
        :return: None
        """

        uri = self._console_url + '/report/reports/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            frequency = kwargs.pop('frequency', None)
            enabled = kwargs.pop('enabled', None)
            mail_enabled = kwargs.pop('mail_enabled', None)
            recipients = kwargs.pop('recipients', None)
            templates = kwargs.pop('templates', None)
            if name:
                update_data['name'] = name
            if frequency and frequency in [1, 2, 3]:
                update_data['frequency'] = frequency
            if enabled is not None:
                update_data['enabled'] = enabled
            if mail_enabled is not None:
                update_data['mailEnabled'] = mail_enabled
            if mail_enabled:
                assert recipients
                update_data['recipients'] = recipients
            if templates is not None:
                assert templates
                update_data['templates'] = templates
                # other kwargs handler
        #print update_data
        response = self._session.put(uri, json=update_data)
        response_content = json.loads(response.content)
        #print response.content
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete time report by id

        :param id: time report id
        :return: None
        """

        uri = self._console_url + '/report/reports/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all time report

        :return: None
        """

        report_list = self.list()
        for report in report_list:
            try:
                self.delete(report['id'])
            except:
                pass

    def get_share_type(self, id):
        """Get share type for time report
        
        :param id: report id
        :return: shareType
        """
        payload = {'entityType': self._entity_type}
        uri = self._console_url + '/system/share/' + id
        print uri

        response = self._session.get(uri, params=payload)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['shareType']

    def set_share_type(self, id, share_type, users=[]):
        """Set share type for time report
        
        :param id: report id
        :param share_type: share type
        :param users: users if set shareType=2
        :return: None
        """
        uri = self._console_url + '/system/share/' + id
        _share_type = ShareType.get(share_type, 1)
        payload = {
            'entityType': self._entity_type,
            'shareType': _share_type
        }
        if share_type == 'specific':
            assert users
            payload['users'] = users

        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def retrive_report(self, id, start_time=date.today(), end_time=date.today() + timedelta(days=1)):
        """retrive time report
        
        :param id: report id, required
        :param start_time: start time, default is today timestamp
        :param end_time: end time, default is tomorrow timestamp
        :return: None
        """

        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')

        payload = {
            'forceTime': True,
            'startTime': convert_date_time(start_time),
            'endTime': convert_date_time(end_time),
        }
        uri = self._console_url + '/report/reports/run-report/' + id
        response = self._session.post(uri, data=payload)
        status_code_check(response.status_code, 200)
        # response_content = json.loads(response.content)#response.content is null, if want to get report, need to query db
        #get report, now support pdf/html/zip formats
        import time
        time.sleep(60)
        report_list = self.list()
        report = None
        for i in report_list:
            if i['id'] == id:
                report = i
                break
        assert report
        assert report['reportItems']
        for p in report['reportItems']:
            path = p['path'][1:]
            for f in ReportFileFormat:
                uri = self._console_url + path + f
                print uri
                response = self._session.get(uri)
                status_code_check(response.status_code, 200)
