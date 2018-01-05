# -*- coding: utf-8 -*-

import requests
import hashlib
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from . import __title__, __version__
from ._internal_utils import status_code_check, response_status_check

import logging
log = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def clean():
    user_agent = '{0}/{1}'.format(__title__, __version__)
    with requests.Session() as session:
        session.headers.update({'user-agent': user_agent})
        session.verify = False
    return session


def login(console_url, username, password):
    user_agent = '{0}/{1}'.format(__title__, __version__)

    # Login from internal bypass
    login_url = console_url + '/system/auth/login'
    with requests.Session() as session:
        session.headers.update({'user-agent': user_agent})
        session.headers.update({'referer': console_url})
        #session.headers.update({'Content-Encoding': 'UTF-8'})
        m = hashlib.md5()
        m.update(password)
        data = {"username": username, "password": m.hexdigest(), "internal_bypass": True}
        response = session.post(login_url, json=data, verify=False)
        response_content = json.loads(response.content)
        status_code_check(response.status_code, 200)
        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        session.headers.update({"TOKEN": response_content['data']['token']})
        session.cookies.set("TOKEN", response_content['data']['token'])
        print response_content['data']['token']
        session.verify = False
        try:
            check_status(console_url, session)
            #session.headers.update({"Cookie": 'csrfToken={csrf}; TOKEN={token}'.format(csrf=session.cookies['csrfToken'], token=response_content['data']['token'])})
            session.headers.update({"x-csrf-token": session.cookies['csrfToken']})
        except:
            pass

    return session


def logout(session):
    # Todo: logout session from server
    session = None
    return session


def check_status(console_url, session):
    uri = console_url + "/api/node/menus"
    response = session.get(uri)
    status_code_check(response.status_code, 200)


