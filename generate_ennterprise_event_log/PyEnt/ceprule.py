# -*- coding: utf-8 -*-

import json
import re

from ._internal_utils import status_code_check, response_status_check, AlarmInfo
from .ceptemplate import CepTemplate
from .contexts import Contexts

import logging
log = logging.getLogger(__name__)


class CEPRuleType(object):
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
        """Get CEP rule type list

        :return: cep rule type list
        """
        payload = {'paginate': False}
        uri = self._console_url + "/api/cep/rule-types"
        response = self._session.get(uri, params=payload)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get(self, id):
        """Get cep rule type by id

        :param id: cep rule type id
        :return: cep rule type info dict, better to improve response format, add statusCode and message
        """
        uri = self._console_url + "/api/cep/rule-types/" + id
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])
        # return response_content['data']
        return response_content

    def get_by_name(self, name):
        """Get  cep rule type by name

        :param name:  cep rule type name
        :return: cep rule type info dict, better to improve response format, add statusCode and message
        """
        rule_type_list = self.list()
        return [rule_type for rule_type in rule_type_list if rule_type['name'] == name][0]

    def create_by_data(self, data):
        """Create cep rule type by data

        :param data: cep rule type data
        :return: None, better to response, and give unified format
        """
        uri = self._console_url + '/api/cep/rule-types'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 201)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])
        # return response_content['data']['id']

    def create(self, name=None, parent_name=None, data=None, **kwargs):
        """Create cep rule tpye

        :param name: cep rule type name
        :param parent_name: parent name
        :param data: cep rule type data
        :param kwargs:  other attrs
        :return: None, better to response, and give unified format
        """
        if data:
            create_data = data
        else:
            assert name
            assert parent_name
            parent_id = self.get_by_name(parent_name)['id']
            create_data = {
                'name': name,
                'parentId': parent_id
            }
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update cep rule type by id

        :param id: cep rule type id
        :param data: update data
        :param kwargs: optional arguments to update cep rule type
        :return: None
        """
        uri = self._console_url + '/api/cep/rule-types/' + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            update_data = self.get(id)
            if name:
                update_data['name'] = name
        response = self._session.put(uri, json=update_data)
        # response_content = json.loads(response.content)
        status_code_check(response.status_code, 204)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete cep rule type by id

        :param id: cep rule type id
        :return: None
        """

        uri = self._console_url + '/api/cep/rule-types/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 204)

    def delete_all(self):
        """Delete all cep rule types

        :return: None
        """
        rule_type_list = self.list()
        for rule_type in rule_type_list:
            try:
                self.delete(rule_type['id'])
            except Exception as ex:
                pass


class CepRule(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self.inner_event = []

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def init_event_param(self):
        """Get cep event param info
        
        :return: cep event params, used to create or update cep rule
        """
        uri = self._console_url + "/event/search/getInitParams"
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def get_event_list(self):
        """Get cep event list info, include global event/inner event and parse event, context is exclude
        
        :return: cep event list, used to create or update cep rule
        """
        uri = self._console_url + "/api/cep/security/eventBase/query"
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get_event_attr_list(self, event_name):
        """Get event attr for specific event when cep init
        
        :param event_name: event name
        :return: attr name list
        """
        all_event = self.get_event_list()
        specific_event = [event for event in all_event if event['name'] == event_name][0]
        return [attr['attrField'] for attr in specific_event['eventType']['attributes']]

    def get_inner_event(self):
        """Get all inner event names
        
        :return: inner event name list
        """
        all_event = self.get_event_list()
        return [event['name'] for event in all_event if event['keyword'] == 'inner']

    def get_event_by_name(self, name):
        event_list = self.get_event_list()
        return [event for event in event_list if event['name'] == name][0]

    def get_eventattr_by_name(self, event, attr_name):
        attrs = event['eventType']['attributes']
        return [attr for attr in attrs if attr['attrName'] == attr_name][0]

    def get_alarm_attr_list(self):
        """Get alarm attrs
        
        :return: cep alarm attr list, used to create or update cep rule, and handling event attr rename with alarm attr
        """
        uri = self._console_url + "/api/cep/alarm/attr/query"
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get_alarm_attr_by_name(self, name):
        alarm_attr_list = self.get_alarm_attr_list()
        return [alarm_attr for alarm_attr in alarm_attr_list if alarm_attr['attrName']==name][0]

    def list(self):
        """Get cep rule list
        
        :return: cep rule list
        """
        payload = {'paginate': False}
        uri = self._console_url + "/api/cep/rules"
        response = self._session.get(uri, params=payload)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['list']

    def get(self, id):
        """Get cep rule by id
        
        :param id: cep rule id
        :return: cep rule dict
        """
        uri = self._console_url + "/api/cep/rules/" + str(id)
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        return json.loads(response.content)

    def get_by_name(self, name):
        """Get cep rule by name
        
        :param name: cep rule name
        :return: 
        """
        rule_list = self.list()
        return [rule for rule in rule_list if rule['name'] == name][0]

    def check_alarm_content_output(self):
        cep_rule_list = self.list()
        issue_rules = []
        ptn = re.compile(r'\${(.+?)}')
        for i in cep_rule_list:
            # name = i['name']
            # print 'check cep rule: ', name
            try:
                selects = i['selects']
                alert = i['alert']
                alert_content = ''
                alert_output = []
                try:
                    alert_enabled = alert['enabled']
                    if not alert_enabled:
                        continue
                    alert_content = alert['alarmContent']
                    alert_output = ptn.findall(alert_content)
                except:
                    pass
                if not alert_output:
                    continue
                output_list = []
                for select in selects:
                    event = select['event']
                    has_alias = select['hasAlias']
                    if has_alias:
                        output = select['alias']
                    else:
                        output = event['attrField']
                    output_list.append(output)
                for out in alert_output:
                    if out not in output_list:
                        raise Exception('%s output and alarm content not matched!' %i['name'])
            except:
                issue_rules.append(i['name'])
        return issue_rules


    def generate_default_event_selects(self):
        """Generate default event and selects section
        
        :return: tuple, items are events list and selects list 
        """
        event_name = u"全局事件"
        event = self.get_event_by_name(event_name)
        event_dict = self.generate_event_dict(event['id'], event['name'], event['typeId'], 'A')
        event_list = [event_dict]
        attrs = event['eventType']['attributes']
        select_list = []
        attr_occur_time = [attr for attr in attrs if attr['attrName']==u'发生时间'][0]
        select_list.append(self.generate_select_item(attr_occur_time, event_dict, True, 'start_time', False, 'min'))
        select_list.append(self.generate_select_item(attr_occur_time, event_dict, True, 'end_time', False, 'max'))
        attr_src_addr = [attr for attr in attrs if attr['attrName'] == u'源地址'][0]
        select_list.append(self.generate_select_item(attr_src_addr, event_dict))
        attr_src_port = [attr for attr in attrs if attr['attrName'] == u'源端口'][0]
        select_list.append(self.generate_select_item(attr_src_port, event_dict))
        attr_dst_addr = [attr for attr in attrs if attr['attrName'] == u'目的地址'][0]
        select_list.append(self.generate_select_item(attr_dst_addr, event_dict))
        attr_dst_port = [attr for attr in attrs if attr['attrName'] == u'目的端口'][0]
        select_list.append(self.generate_select_item(attr_dst_port, event_dict))
        return event_list, select_list

    def generate_event_dict(self, event_id, event_name, event_type, event_alias='', event_filter=None):
        """Generate event dict, for event source use, event source type is list, item type is dict as following
 
        :param event_id: event id
        :param event_name: event name
        :param event_type: event type id, these 3 attrs can be got by calling get_event_by_name, para is event_name, attr is id, typeId
        :param event_alias: 
        :param event_filter: 
        :return: event dict
        """
        ret_dict = {
            'event': {
                'id': event_id,
                'name': event_name,
                'typeId': event_type,
            },
            'as': event_alias,
            'filter': None
        }
        if event_filter:
            ret_dict['filter'] = str(dict(FilterExpression=event_filter)).replace("'", '"').replace('{"right": [u', '{"right": [')
        return ret_dict

    def generate_select_item(self, attr, event, has_alias=False, alias="", has_fn=False, fn=""):
        """Generate select item dict, for output result use, output result is list, item type is dict as following
        
        :param attr: event attribute
        :param event: event, generate by generate_event_dict
        :param has_alias: if has alias or not
        :param alias: alias name
        :param has_fn: if has function or not
        :param fn: function name
        :return: select item dict
        """
        event_dict = {
            "event": {
                "id": None,
                "attrField": attr["attrField"],
                "attrName": attr["attrName"],
                "attrType": attr["attrType"],
                "event": event['event'],
                "as": event['as']
            },
            "hasAlias": False,
            "hasFn": False,
            "alias": "",
            "fn": ""
        }
        if has_alias:
            assert alias
            event_dict['hasAlias'] = True
            event_dict['alias'] = alias
        if has_fn:
            assert fn
            event_dict['hasFn'] = True
            event_dict['fn'] = fn
        return event_dict

    def generate_default_alert(self):
        """Generate default alert
        
        :return: alert dict
        """
        alert_dict = {
            "enabled": False,
            "focus": 0,
            "alarmType": "-1",
            "alarmStage": "-1",
            "alarmLevel": "-1",
            "alarmContent": "",
            "emailEnabled": False,
            "recipients": [],
            "smsEnabled": False,
            "phoneNumbers": [],
            "ruleType": None,
            "knowledge": [],
            "assets": []
        }
        return alert_dict

    def generate_alert(self, b_enabled=False, focus=0, alarm_type="-1", alarm_stage="-1", alarm_level="-1", alarm_content=None,
                       email_enabled=False, email_rec=[], sms_enabled=False, phone_list=[], **kwargs):
        alert_dict = self.generate_default_alert()
        if not b_enabled:
            pass
        else:
            alert_dict['enabled'] = True
            assert alarm_type in AlarmInfo['alarm_type']
            assert alarm_stage in AlarmInfo['alarm_stage']
            assert alarm_level in AlarmInfo['alarm_level']
            alert_dict['alarmType'] = alarm_type
            alert_dict['alarmStage'] = alarm_stage
            alert_dict['alarmLevel'] = alarm_level
            if alarm_content:
                alert_dict['alarmContent'] = alarm_content
            if email_enabled:
                assert email_rec
                alert_dict['emailEnabled'] = True
                alert_dict['recipients'] = email_rec
            if sms_enabled:
                assert phone_list
                alert_dict['smsEnabled'] = True
                alert_dict['phoneNumbers'] = phone_list
        return alert_dict

    def generate_window(self, type="ext_timed", value=10, unit="min", event=None):
        """Generate window, used for time window
        
        :param type: type
        :param value: value
        :param unit: unit
        :param event: event dict, can be got from event attr in generate_select_item return value
        :return: 
        """
        return {'type': type, 'value': value, 'unit': unit, 'event': event}

    def generate_inner_event(self, enabled=False, name=''):
        """Generate inner event
        
        :param enabled: enable inner event or not
        :param name: inner event name
        :return: inner event dict
        """
        if enabled:
            assert name
        return {'enabled': enabled, 'name': name}

    def generate_having_condition(self, n1='', n2='', n3=''):
        """Generate having condition, triggering condition got from this, and groupby list, must be set with templateid 1/5/6
        
        :param n1: n1, can be empty
        :param n2: n2
        :param n3: n3
        :return: having condition dict
        """
        if (not n1) and (not n2) and (not n3):
            return {}
        else:
            return {
                'n1': n1,
                'n2': n2,
                'n3': n3,
            }

    def create_by_data(self, data):
        """Create cep rule by data
        
        :param data: cep rule data
        :return: None, better to return cep rule id created
        """
        uri = self._console_url + '/api/cep/rules'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 201)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])
        # return response_content['data']['id']

    def create_by_file(self, rule_file, name=''):
        """Create cep rule by file
        
        :param rule_file: cep rule file
        :param name: cep rule name replaced
        :return: None
        """
        with open(rule_file) as pf:
            content = pf.read().strip()
        rule_dict = json.loads(content)
        if name:
            rule_dict['name'] = name
        return self.create_by_data(rule_dict)

    def create(self, name=None, desc=None, status=1, type_name=None, template_name=None, events=None, selects=None,
               alert=None, inner_event=None, window=None, groupby=None, having=None, has_context=False, context_name="",
               where=None, editable=1, data=None, **kwargs):
        """Create cep rule
        
        :param name: refer to name, cep rule name, required
        :param desc: refer to desc, cep rule description, required
        :param status: refer to status, cep rule status, required, 1 means start, 0 means stop, default is 1
        :param type_name: cep rule type name, type item got from this, required 
        :param template_name: cep template name, templateId item got from this, required
        :param events: refer to events, list format, item is dict format, required
        :param selects: refer to selects, list format, item is dict format, required
        :param alert: refer to alarm, dict format
        :param inner_event: refer to InnerEvent, dict format
        :param window: refer to window
        :param groupby: refer to groupBy, must be set if templateid is 1/5/6, list format, item can be got from event attr in generate_select_item return value
        :param having: refer to having, must be set if templateid is 1/5/6
        :param has_context: refer to has_Context
        :param context_name: context name, ContextId item got from this
        :param where: where condition, you can set this by function in tool build_filter_base and build_filter when templateid is 3/4
        :param editable: default is 1
        :param data: cep rule data
        :param kwargs: other optional data
        :return: None
        """
        if data:
            create_data = data
        else:
            assert name
            if not status in [0, 1]:
                status = 0

            #get cep rule type, key is type
            assert type_name
            _cep_rule_type = CEPRuleType(self._console_url, self._session)
            type_info = _cep_rule_type.get_by_name(type_name)
            assert type_info
            type_id = type_info['id']

            #get cep template id, key is templateId
            assert template_name
            _cep_template = CepTemplate(self._console_url, self._session)
            template_info = _cep_template.get_by_name(template_name)
            assert template_info
            template_id = template_info['id']
            window_needed = template_info['hasWindow']
            groupby_needed = template_info['hasGroupBy']
            having_needed = template_info['hasHaving']
            if window_needed:
                assert window
            if groupby_needed:
                assert groupby
            if having_needed:
                assert having

            #get context info, key is hasContext, contextId
            if has_context:
                assert context_name
                _context = Contexts(self._console_url, self._session)
                context_info = _context.get_by_name(context_name)
                assert context_info
                context_id = context_info['id']

            #events and selects, event count must be greater than 1 when choose correlation analysis
            event_list, select_list = self.generate_default_event_selects()
            if not events:
                events = event_list
            if not selects:
                selects = select_list
            if template_id in [3, 4]:
                assert len(events) > 1

            #inner event
            if not inner_event:
                inner_event = self.generate_inner_event()
            #alert setting
            if not alert:
                alert = self.generate_default_alert()

            create_data = {
                'name': name,
                'desc': desc,
                'status': status,
                'type': type_id,
                'templateId': template_id,
                'events': events,
                'alert': alert,
                'selects': selects,
                'innerEvent': inner_event,
                'hasContext': has_context,
                'contextId': context_id if has_context else '',
                'window': window if window_needed else {},
                'groupBy': groupby if groupby_needed else [],
                'having': having if having_needed else {},
                'patternRepeat': {'low': None, 'high': None},
                'where': None,
                "editable": editable
            }
        if where:
            create_data['where'] = str(dict(FilterExpression=where)).replace("'", '"')
        return self.create_by_data(create_data)

    def _get_name_list(self):
        """Get cep rule name list
        
        :return: cep rule name list
        """
        rule_list = self.list()
        return [rule['name'] for rule in rule_list]

    def _create_valid_name(self, name):
        """Generate valid name
        
        :param name: name based
        :return: new name, for copy usage
        """
        name_list = self._get_name_list()
        count = 1
        while True:
            new_name = name + ' (' + str(count) + ')'
            if new_name in name_list:
                count = count + 1
            else:
                break
        return new_name

    def copy(self, id):
        """Copy cep rule

        :param id: cep rule id need to copy
        :return: None
        """
        create_data = self.get(id)
        name = self._create_valid_name(create_data['name'])
        create_data['name'] = name
        self.create_by_data(create_data)

    def delete(self, id):
        """Delete cep rule by id
        
        :param id: cep rule id
        :return: None
        """
        uri = self._console_url + "/api/cep/rules/" + str(id)
        response = self._session.delete(uri)
        status_code_check(response.status_code, 204)

    def update(self, id, data=None, **kwargs):
        """Update cep rule by id, currently support modify name/desc/status/alert, others not support yet
        
        :param id: cep rule id
        :param data: update data
        :param kwargs: optional kwargs, like name/desc/status/alert
        :return: None
        """
        uri = self._console_url + '/api/cep/rules/' + str(id)
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            desc = kwargs.pop('desc', None)
            status = kwargs.pop('status', None)
            alert = kwargs.pop('alert', None)
            update_data = self.get(id)
            if name:
                update_data['name'] = name
            if desc:
                update_data['desc'] = desc
            if status:
                update_data['status'] = status
            if alert:
                update_data['alert'] = alert

        response = self._session.put(uri, json=update_data)
        #response_content = json.loads(response.content)
        status_code_check(response.status_code, 204, 200)
        #response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def start(self, id):
        """Start cep rule
        
        :param id: cep rule id
        :return: None
        """
        uri = self._console_url + "/api/cep/rules/" + str(id)
        data = {'status': 1}
        response = self._session.post(uri, json=data)
        status_code_check(response.status_code, 200)

    def start_all(self):
        """Start all cep rules
        
        :return: None
        """
        cep_rule_list = self.list()
        for cep_rule in cep_rule_list:
            try:
                self.start(cep_rule['id'])
            except:
                pass

    def stop(self, id):
        """Stop cep rule
        
        :param id: cep rule id
        :return: 
        """
        uri = self._console_url + "/api/cep/rules/" + str(id)
        data = {'status': 0}
        response = self._session.post(uri, json=data)
        status_code_check(response.status_code, 200)

    def stop_all(self):
        """Stop all cep rules
        
        :return: None
        """
        cep_rule_list = self.list()
        for cep_rule in cep_rule_list:
            try:
                self.stop(cep_rule['id'])
            except:
                pass

    def import_rule(self, localfile, strategy='skip'):
        """Import cep rule
        
        :param localfile: cep rule file
        :param strategy: import strategy, default is rename, can be rename, overwrite, skip
        :return: None
        """
        uri = self._console_url + '/api/cep/import-check'
        with open(localfile) as pf:
            content = pf.read()
        response = self._session.post(uri, data=content)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        b_dup = response_content['duplicate']
        uri = self._console_url + '/api/cep/import-batch'
        if b_dup:
            strategies = {
                'rename': 'rename',
                'skip': 'skip',
                'overwrite': 'overwrite'
            }
            strategy = strategies.get(strategy, 'skip')
            uri = uri + '?strategy=' + strategy
            #print uri
        response = self._session.post(uri, json=response_content)
        status_code_check(response.status_code, 200)
        return uri

    def export_rule(self, localfile, id_list=[]):
        """Export cep rule
        
        :param localfile: cep rule storing file
        :param id_list: cep rule ids need to export
        :return: None
        """
        uri = self._console_url + '/api/cep/rules-importexport'
        if id_list:
            id_list = [str(i) for i in id_list]
            uri = uri + '?ids=' + ','.join(id_list)
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        with open(localfile, 'wb') as pf:
            pf.write(response.content)

    def _cep_rule_check_normal(self, rule):
        """check if cep rule output with normal template is correct, raise exception if error occurred
        
        :param rule: rule info dict
        :return: None
        """
        events = rule['events']
        assert len(events) == 1
        event_name = events[0]['event']['name']
        b_inner_event = False
        time_field_list = ['occur_time']
        if event_name in self.inner_event:
            b_inner_event = True
            time_field_list.extend(['start_time', 'end_time'])
        start_time_alias = False
        end_time_alias = False
        start_time_event = None
        end_time_event = None
        selects = rule['selects']
        for select in selects:
            if select['event']['attrField'] in time_field_list and select['alias'] == 'start_time':
                start_time_event = select['event']['as']
                if select['hasAlias'] and (not select['hasFn']):
                    start_time_alias = True

            if select['event']['attrField'] in time_field_list and select['alias'] == 'end_time':
                end_time_event = select['event']['as']
                if select['hasAlias'] and (not select['hasFn']):
                    end_time_alias = True

        #print start_time_event, end_time_event, start_time_alias, end_time_alias
        assert start_time_event is not None, 'no event contains start time'
        assert end_time_event is not None, 'no event contains end time'
        assert start_time_event == end_time_event, 'not the same event'
        assert (start_time_alias and end_time_alias), 'start end time alias or func error'

    def _cep_rule_check_having(self, rule):
        """check if cep rule output with having template is correct, raise exception if error occurred

        :param rule: rule info dict
        :return: None
        """
        events = rule['events']
        assert len(events) == 1
        event_name = events[0]['event']['name']
        b_inner_event = False
        time_field_list = ['occur_time']
        if event_name in self.inner_event:
            b_inner_event = True
            time_field_list.extend(['start_time', 'end_time'])
        start_time_alias = False
        end_time_alias = False
        start_time_event = None
        end_time_event = None
        selects = rule['selects']
        for select in selects:
            if select['event']['attrField'] in time_field_list and select['alias'] == 'start_time':
                start_time_event = select['event']['as']
                if select['hasAlias'] and select['hasFn']:
                    start_time_alias = True

            if select['event']['attrField'] in time_field_list and select['alias'] == 'end_time':
                end_time_event = select['event']['as']
                if select['hasAlias'] and select['hasFn']:
                    end_time_alias = True

        #print start_time_event, end_time_event, start_time_alias, end_time_alias
        assert start_time_event is not None, 'no event contains start time'
        assert end_time_event is not None, 'no event contains end time'
        assert start_time_event == end_time_event, 'not the same event'
        assert (start_time_alias and end_time_alias), 'start end time alias or func error'

    def _cep_rule_check_multi_event(self, rule):
        """check if cep rule output with multi event(follow-by, repeat-until) template is correct, raise exception if error occurred

        :param rule: rule info dict
        :return: None
        """
        events = rule['events']
        assert len(events) > 1
        start_time_alias = False
        end_time_alias = False
        start_time_event = None
        end_time_event = None
        selects = rule['selects']
        for select in selects:
            if select['alias'] == 'start_time':#select['event']['attrField'] == 'occur_time' and
                start_time_event = select['event']['as']
                if select['hasAlias'] and (not select['hasFn']):
                    start_time_alias = True

            if select['alias'] == 'end_time':#select['event']['attrField'] == 'occur_time' and
                end_time_event = select['event']['as']
                if select['hasAlias'] and (not select['hasFn']):
                    end_time_alias = True

        #print start_time_event, end_time_event, start_time_alias, end_time_alias
        assert start_time_event is not None, 'no event contains start time'
        assert end_time_event is not None, 'no event contains end time'
        assert start_time_event != end_time_event, 'same event'
        assert (start_time_alias and end_time_alias), 'start end time alias or func error'

    def cep_rule_single_check(self, name):
        """check if cep rule output is correct, raise exception if error occurred
        
        :param name: rule name
        :return: None
        """
        rule = self.get_by_name(name)
        self.inner_event = self.get_inner_event()
        if rule['templateId'] == 2:
            self._cep_rule_check_normal(rule)
        elif rule['templateId'] in (1, 5, 6):
            self._cep_rule_check_having(rule)
        elif rule['templateId'] in (3, 4):
            self._cep_rule_check_multi_event(rule)
        else:
            raise Exception('%s template not exits.' % (rule['name']))

    def cep_rule_output_check(self):
        """check if all cep rules output are correct, raise exception if error occurred

        :return: None
        """
        issue_rules = []
        rule_list = self.list()
        self.inner_event = self.get_inner_event()
        for rule in rule_list:
            try:
                if rule['templateId'] == 2:
                    self._cep_rule_check_normal(rule)
                elif rule['templateId'] in (1, 5, 6):
                    self._cep_rule_check_having(rule)
                elif rule['templateId'] in (3, 4):
                    self._cep_rule_check_multi_event(rule)
                else:
                    raise Exception('%s template not exits.' %(rule['name']))
            except:
                issue_rules.append(rule['name'])
        return issue_rules

    def cep_rule_alarm_notification_check(self):
        """Check if alert notification is set in cep rule
        
        :return: issue cep rule list
        """
        issue_rules = []
        rule_list = self.list()
        for rule in rule_list:
            if not rule['system']:
                continue
            if not rule['alert']['enabled']:
                continue
            if (not rule['alert']['notificationEnabled']) or (rule['alert']['notificationEnabled'] and len(rule['alert']['notificationConfig'])<1):
                issue_rules.append(rule['name'])
        return issue_rules

    def get_buildin_cep_rule_list(self):
        """get cep bule in rule list

        :return: buildin cep rule name list
        """
        issue_rules = []
        rule_list = self.list()
        for rule in rule_list:
            if not rule['system']:
                issue_rules.append(rule['name'])
        return issue_rules

    def get_cep_rule_with_inner_event(self):
        """Get cep rule with inner event
        
        :return: cep rule dict, key is cep rule name, value is inner event list 
        """
        rule_list = self.list()
        self.inner_event = self.get_inner_event()
        rule_dict = dict()
        inner_event_set = set()
        for rule in rule_list:
            has_inner_event = False
            events = rule['events']
            assert len(events) >= 1
            for event in events:
                event_name = event['event']['name']
                if event_name in self.inner_event:
                    has_inner_event = True
                    if rule['name'] not in rule_dict.keys():
                        rule_dict[rule['name']] = []
                    rule_dict[rule['name']].append(event_name)
                    inner_event_set.add(event_name)
                    #print rule['name'], rule['templateId'], 'need inner event', event_name
        # print 'rules that need inner event list', len(rule_dict.keys())
        # for i in rule_dict:
        #     print i, json.dumps(rule_dict[i], ensure_ascii=False)
        # print 'inner event that being called', len(inner_event_set)
        # for i in inner_event_set:
        #     print i
        return rule_dict

    def get_inner_event_with_cep_rule_dict(self):
        """Get inner event with cep rule dict
        
        :return: dict, key is inner event, value is cep rule name uses this inner event
        """
        rule_list = self.list()
        self.inner_event = self.get_inner_event()
        event_dict = dict()
        for rule in rule_list:
            events = rule['events']
            assert len(events) >= 1
            for event in events:
                event_name = event['event']['name']
                if event_name in self.inner_event:
                    if event_name not in event_dict:
                        event_dict[event_name] = []
                    event_dict[event_name].append(rule['name'])
        return event_dict

    def get_cep_rule_gen_inner_event(self):
        """Get cep rule generate inner event
        
        :return: None
        """
        rule_list = self.list()
        event_dict = self.get_inner_event_with_cep_rule_dict()
        for rule in rule_list:
            if rule['innerEvent']['enabled']:
                if rule['innerEvent']['name'] in event_dict:
                    print rule['name'],'\t', rule['innerEvent']['name'],'\t', json.dumps(event_dict[rule['innerEvent']['name']], ensure_ascii=False)
                else:
                    print rule['name'],'\t', rule['innerEvent']['name'],'\t', 'no rule used this inner event'

