# -*- coding: utf-8 -*-


"""
pyent._internal_utils
~~~~~~~~~~~~~~
This module provides utility functions that are used within pyetn
that are also useful for external consumption.
"""

from .exceptions import StatusCodeError, ResponseStatusError

import time


def status_code_check(status_code, *expect_status):
    for i in expect_status:
        if status_code == i:
            return
    else:
        raise StatusCodeError(status_code, expect_status)
    # if not status_code == expect_status:
    #     raise StatusCodeError(status_code, expect_status)


def response_status_check(status, expect_status, messages):
    if not status == expect_status:
        raise ResponseStatusError(status, expect_status, messages)


def convert_date_time(date):
    return int(time.mktime(date.timetuple())*1000)


ParserType = {
    'regex': 'regex',
    'key_value': 'WELF_value'
}

MappingType = {
    'regex': 'REGULAR',
    'text': 'EQUAL',
    'redefine': 'TRANSFORM',
    'time': 'TIME'
}

Charset = {
    'utf-8': 'UTF-8',
    'gbk': 'GBK'
}

CollectorType = {
    'syslog': 'SYSLOG',
    'file': 'FILE',
    'jdbc': 'JDBC',
    'kafka': 'KAFKA'
}

TemplateType = {
    'normal': 'normal',
    'pattern': 'pattern'
}

PatternOpType = {
    'followby': 'followBy',
    'repeat': 'repeatUntil'
}

IPConfigType = {
    'single': 'single',
    'interval': 'couple',
    'mask': 'subnetmask'
}

OperationType = {
    'ip': {
        'e': '=',
        'ne': '!='
    },
    'text': {
        'e': '=',
        'ne': '!='
    },
    'num': {
        'ge': '>=',
        'ne': '!=',
        'le': '<=',
        'in': 'in',
        'e': '=',
        'l': '<',
        'g': '>'
    },
    'date': {
        'g': '>',
        'l': '<'
    },
    'intel': {
        'belong': 'belongs',
        'not_belong': 'nbelong'
    },
}

AlarmInfo = {
    'alarm_focus': ['0', '1'],
    'alarm_level': ['0', '1', '2'],
    'alarm_stage': ['1', '2', '3', '4', '5', '6'],
    'alarm_status': ['0', '1', '2'],
    'alarm_type': ['/hostsec', '/malware', '/networksec', '/accessctrl', '/datasec', '/other']
}

EntityType = {
    'dashboard': 1,
    'component': 2,
    'report_template': 3,
    'report': 4,
}

ShareType = {
    'open': 0,
    'self': 1,
    'specific': 2,
}

ReportFileFormat = ['.pdf', '.html', '.zip']