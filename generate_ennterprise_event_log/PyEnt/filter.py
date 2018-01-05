# -*- coding: utf-8 -*-


"""
pyent.filter
~~~~~~~~~~~~~~
This module provides filter functions that are used within pyent
"""

from copy import copy


class EntObject(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


def filter(object_list, **kwargs):
    for object_item in object_list:
        object_valid = False
        for key, value in kwargs.iteritems():
            if not value:
                continue

            item_value = copy(object_item)
            for attribute in key.split('.'):
                item_value = getattr(item_value, attribute, None)

                if item_value is None:
                    break

                object_valid = True

        if object_valid:
            yield object_item
