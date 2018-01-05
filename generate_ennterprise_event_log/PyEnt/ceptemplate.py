# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check
from ._internal_utils import TemplateType, PatternOpType

import logging
log = logging.getLogger(__name__)


class CepTemplate(object):
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
        """Get cep rule template list
        
        :return: cep rule template list
        """
        payload = {'paginate': False}
        uri = self._console_url + '/api/cep/templates'
        response = self._session.get(uri, params=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return json.loads(response.content)['data']['list']

    def get(self, id):
        """Get cep rule template by id

        :param id: cep rule template id
        :return: cep rule template info dict, better to improve response format, add statusCode and message
        """
        uri = self._console_url + '/api/cep/templates/' + id
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])
        # return response_content['data']
        return response_content

    def get_by_name(self, name):
        """Get  cep rule template by name

        :param name:  cep template type name
        :return: cep rule template info dict
        """
        rule_temp_list = self.list()
        return [rule_temp for rule_temp in rule_temp_list if rule_temp['name'] == name][0]

    def create_by_data(self, data):
        """Create cep rule template by data
        
        :param data: cep rule template data
        :return: None, better to improve response format, add statusCode and message
        """
        uri = self._console_url + '/api/cep/templates'

        response = self._session.post(uri, json=data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 201)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])
        # return response_content['data']['id']

    def create(self, name=None, desc=None, temp_type=None, pattern_op=None, has_content=False, has_select=True, has_filter=True,
               has_window=False, has_groupby=False, has_having=False, having={}, data=None, **kwargs):
        """Create cep rule template
        
        :param name: cep rule template name, refer to name, required
        :param desc: cep rule template desc, refer to desc
        :param temp_type: cep rule template type, normal or pattern, refer to type, required
        :param pattern_op: cep rule template pattern operator, followby or repeat, refer to patternOperator, required
        :param has_content: refer to hasContext, required
        :param has_select: refer to hasSelect, required
        :param has_filter: refert to hasFilter
        :param has_window: refer to hasWindow 
        :param has_groupby: refer to hasGroupBy
        :param has_having: refer to hasHaving
        :param having: refer to having
        :param data: cep rule template data 
        :param kwargs: other attrs
        :return: None, better to improve response format, add statusCode and message
        """
        if data:
            create_data = data
        else:
            assert name
            temp_type = TemplateType.get(temp_type, None)
            assert temp_type
            pattern_op = PatternOpType.get(pattern_op, None)
            assert pattern_op
            if temp_type == 'normal' and has_window:
                assert has_having
            if temp_type == 'normal' and has_groupby:
                assert has_window and has_having
            if temp_type == 'pattern':
                assert has_window and (not has_groupby) and (not has_having)
            if has_having:
                epl_temp = having.get('epl', None)
                desc_temp = having.get('desc', None)
                assert (epl_temp is not None) and (desc_temp is not None)
            create_data = {
                'name': name,
                'desc': desc,
                'type': temp_type,
                "patternOperator": pattern_op,
                "hasContext": has_content,
                "hasSelect": has_select,
                "hasFilter": has_filter,
                "hasWindow": has_window,
                "hasGroupBy": has_groupby,
                "hasHaving": has_having,
                "having": {
                    "eplTpl": epl_temp if has_having else '',
                    "descTpl": desc_temp if has_having else ''
                }
            }
            return self.create_by_data(create_data)

    def _get_name_list(self):
        """Get cep template name list

        :return: cep template name list
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
        """Copy cep template
        
        :param id: cep template id need to copy
        :return: None
        """
        create_data = self.get(id)
        name = self._create_valid_name(create_data['name'])
        create_data['name'] = name
        self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update cep rule template info 
        
        :param id: cep rule template id
        :param data: cep rule template update data
        :param kwargs: other attrs
        :return: None
        """
        uri = self._console_url + '/api/cep/templates/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            name = kwargs.pop('name', None)
            if name:
                update_data['name'] = name
            desc = kwargs.pop('desc', None)
            if desc:
                update_data['desc'] = name
            temp_type = kwargs.pop('temp_type', None)
            if temp_type:
                temp_type = TemplateType.get(temp_type, None)
            if temp_type is None:
                temp_type = update_data['type']
            pattern_op = kwargs.pop('pattern_op', None)
            if pattern_op:
                pattern_op = PatternOpType.get(pattern_op, None)
            if pattern_op is None:
                pattern_op = update_data['patternOperator']
            has_content = kwargs.pop('has_content', update_data['hasContext'])
            has_select = kwargs.pop('has_select', update_data['hasSelect'])
            has_filter = kwargs.pop('has_filter', update_data['hasFilter'])
            has_window = kwargs.pop('has_window', update_data['hasWindow'])
            has_groupby = kwargs.pop('has_groupby', update_data['hasGroupBy'])
            has_having = kwargs.pop('has_having', update_data['hasHaving'])
            having = kwargs.pop('having', update_data['having'])
            if temp_type == 'normal' and has_window:
                assert has_having
            if temp_type == 'normal' and has_groupby:
                assert has_window and has_having
            if temp_type == 'pattern':
                assert has_window and (not has_groupby) and (not has_having)
            if has_having:
                epl_temp = having.get('epl', None)
                desc_temp = having.get('desc', None)
                assert (epl_temp is not None) and (desc_temp is not None)

            update_data['type'] = temp_type
            update_data['patternOperator'] = pattern_op
            update_data['hasContext'] = has_select
            update_data['hasFilter'] = has_filter
            update_data['hasWindow'] = has_window
            update_data['hasGroupBy'] = has_groupby
            update_data['hasHaving'] = has_having
            update_data['having'] = having

        response = self._session.put(uri, json=update_data)
        #response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        # response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete cep rule template by id
        
        :param id: cep rule template id
        :return: None
        """
        uri = self._console_url + '/api/cep/templates/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 204)

    def delete_all(self):
        """Delete all cep rule templates

        :return: None
        """
        rule_type_list = self.list()
        for rule_type in rule_type_list:
            try:
                self.delete(rule_type['id'])
            except Exception as ex:
                pass

    def import_tpls(self, localfile):
        """Import template
        
        :param localfile: local template file
        :return: None
        """

        uri = self._console_url + '/api/cep/templates-importexport'
        with open(localfile) as pf:
            content = pf.read()
        response = self._session.post(uri, data=content)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        if response_content:
            response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def export_tpls(self, localfile, id_list=[]):
        """Export template
        
        :param localfile: file to store template
        :param id_list: template id need to store
        :return: None
        """
        uri = self._console_url + '/api/cep/templates-importexport'
        if id_list:
            uri = uri + '?ids=' + ','.join(id_list)
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)
        with open(localfile, 'wb') as pf:
            pf.write(response.content)



