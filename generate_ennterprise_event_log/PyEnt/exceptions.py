# -*- coding: utf-8 -*-


class StatusCodeError(Exception):
    def __init__(self, status_code, expect):
        super(StatusCodeError, self).__init__(
            'Invalid status code %s, exepct %s' % (status_code, expect))


class ResponseStatusError(Exception):
    def __init__(self, status, expect, messages):
        super(ResponseStatusError, self).__init__(
            'Invalid status %s, expect %s, error message: %s' % (status, expect, ','.join(messages)))


class InvalidAttribute(ValueError):
    def __init__(self, attribute_name):
        super(StatusCodeError, self).__init__(
            'Invalid attribute value %s' % attribute_name)
