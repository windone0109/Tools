# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check

import logging
log = logging.getLogger(__name__)


class KnowledgeType(object):
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
        """Get all knowledge type

        :return: knowledge type list
        """

        uri = self._console_url + '/security/knowledgeType/query'
        payload = {'paginate': False}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get knowledgetype by id

        :param id: knowledgetype id
        :return: knowledgetype info dict
        """

        uri = self._console_url + '/security/knowledgeType/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get knowledgetype by name

        :param name: knowledgetype name
        :return: knowledgetype info dict
        """

        knowledge_list = self.list()
        return [knowledge for knowledge in knowledge_list if knowledge['name'] == name][0]

    def create_by_data(self, data):
        """Create knowledge type by data

        :param data: create data
        :return: knowledge type id
        """
        uri = self._console_url + '/security/knowledgeType'
        response = self.session.put(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']['id']

    def create(self, name=None, description=None, parent_name=None, data=None, **kwargs):
        """Create knowledge type

        :param name: type name, required
        :param description: description
        :param parent_name: parent type name, required
        :param data: create data
        :param kwargs: other opts
        :return: knowledge type id
        """
        if data:
            create_data = data
        else:
            assert name
            assert parent_name
            parent_info = self.get_by_name(parent_name)
            parent_id = parent_info['id']
            create_data = {
                'name': name,
                'parentId': parent_id
            }
            if description:
                create_data['description'] = description
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update knowledge type id

        :param id: knowledge type id
        :param data: knowledge data
        :param kwargs: knowledge opts
        :return: None
        """
        uri = self._console_url + '/security/knowledgeType/' + id
        if data:
            update_data = data
        else:
            name = kwargs.pop('name', None)
            desc = kwargs.pop('description', None)
            update_data = self.get(id)
            if name:
                update_data['name'] = name
            if desc:
                update_data['description'] = desc
        response = self._session.post(uri, json=update_data)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete knowledge type by id

        :param id: knowledge id need to delete
        :return: None
        """
        uri = self._console_url + '/security/knowledgeType/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)


class Knowledge(object):
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
        """Get all knowledges

        :return: knowledge list
        """

        uri = self._console_url + '/security/knowledge/query'
        payload = {'paginate': False, 'pagination': {}, 'sorts': []}
        response = self._session.post(uri, json=payload)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['list']

    def get(self, id):
        """Get knowledge by id

        :param id: knowledge id
        :return: knowledge info dict
        """

        uri = self._console_url + '/security/knowledge/' + id

        response = self._session.get(uri)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']

    def get_by_name(self, name):
        """Get knowledge by name

        :param name: knowledge name
        :return: knowledge info dict
        """

        knowledge_list = self.list()
        return [knowledge for knowledge in knowledge_list if knowledge['title'] == name][0]

    def create_by_data(self, data):
        """Create knowledge

        :param data: knowledge data
        :return: knowledge id
        """

        uri = self._console_url + '/security/knowledge'
        response = self._session.put(uri, json=data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

        return response_content['data']['id']

    def create(self, title=None, summary=None, type_name=None, data=None, **kwargs):
        if data:
            create_data = data
        else:
            assert title
            assert summary
            assert type_name
            _knowledge_type = KnowledgeType(self._console_url, self._session)
            knowledge_type_id = _knowledge_type.get_by_name(type_name)['id']
            create_data = {
                'title': title,
                'summary': summary,
                'knowledgeName': type_name,
                'typeId': knowledge_type_id
            }
            content = kwargs.pop('content', None)
            attachment = kwargs.pop('attachment', None)
            if content:
                create_data['content'] = content
            if attachment:
                attachment_str = ',' + ','.join(attachment)
                create_data['attachmentss'] = attachment_str
                create_data['addAttachmentss'] = attachment_str
        return self.create_by_data(create_data)

    def update(self, id, data=None, **kwargs):
        """Update knowledge info
        
        :param id: knowledge id
        :param data: update data
        :param kwargs: optional keywords
        :return: None
        """
        uri = self._console_url + '/security/knowledge/' + id
        if data:
            update_data = data
        else:
            update_data = self.get(id)
            title = kwargs.pop('title', None)
            summary = kwargs.pop('summary', None)
            content = kwargs.pop('content', None)
            attachment_add = kwargs.pop('attachment_add', None)
            attachment_del = kwargs.pop('attachment_del', None)
            if title:
                update_data['title'] = title
            if summary:
                update_data['summary'] = summary
            if content:
                update_data['content'] = content
            if attachment_add:
                update_data['addAttachmentss'] = ',' + ','.join(attachment_add)
            if attachment_del:
                update_data['deleteAttachmentss'] = ',' + ','.join(attachment_del)
                # other kwargs handler

        response = self._session.post(uri, json=update_data)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])

    def delete(self, id):
        """Delete knowledge by id

        :param id: knowledge id
        :return: None
        """

        uri = self._console_url + '/security/knowledge/' + id
        response = self._session.delete(uri)
        status_code_check(response.status_code, 200)

    def delete_all(self):
        """Delete all knowledges

        :return: None
        """

        knowledge_list = self.list()
        for knowledge in knowledge_list:
            try:
                self.delete(knowledge['id'])
            except Exception as ex:
                pass

    def upload_file(self, local_file):
        """Upload local file to knowledge database
        
        :param local_file: localfile need to update
        :return: upload info dict
        """
        uri = self._console_url + '/security/knowledge/uploadAttachment'
        import os
        multiple_files = [
            ('attachment', (os.path.basename(local_file), open(local_file, 'rb'), 'multipart/form-data'))]
        response = self._session.post(uri, files=multiple_files)
        response_content = json.loads(response.content)

        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        return response_content['data']

    def download_file(self, file_id, local_file):
        """download file to local

        :param local_file: localfile need to store
        :return: None
        """
        uri = self._console_url + '/security/knowledge/downloadAttachment/' + file_id
        response = self._session.get(uri)
        status_code_check(response.status_code, 200)

        with open(local_file, 'wb') as pf:
            pf.write(response.content)
