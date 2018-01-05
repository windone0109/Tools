# -*- coding: utf-8 -*-
from ._internal_utils import IPConfigType

def build_filter_base(left, mid, right):
    return {
    "func": {"left": left, "@class": mid, "right": [right]},
    "operator": "BASE"
    }


def build_filter(op, filter_list=[]):
    assert filter_list
    return {
    "children": [dict(FilterExpression=filter_list)],
    "operator": op
    }


def generate_ip_config_dict(ip_type, content):
    """Generate IP content dict, for intranet use purpose

    :param ip_type: type
    :param content: content
    :return: IP content dict
    """
    content_type = IPConfigType.get(ip_type, None)
    assert content_type
    return {
        'contentType': content_type,
        'content': content
    }


def generate_attr_mapping_subdict(map_type, map_value, map_orgvalue=''):
    """Generate attribute mapping dict, for eventparser attribute mappingList use

    :param map_type: refer to mappingType, current 4 type supported, required
    :param map_value: refer to mappingValue, required
    :param map_orgvalue: refer to orgValue, optional
    :return: mapping dict
    """
    return {
        'mapping_type': map_type,
        'mapping_value': map_value,
        'mapping_key': map_orgvalue
    }


def generate_attr_mapping_dict(attr_name, map_index='', default_value='', mappings=[]):
    """Generate attribute mapping dict, for eventparser attribute mapping use

    :param attr_name: attribute name, required
    :param map_index: mapping index, string format, seperate by ',', refer to mappingIdx, optional
    :param default_value: default value, string format, refer to defaultVal, optional
    :param mappings: list, element is dict created by generate_attr_mapping_subdict
    :return: mapping dict
    """
    return_dict = {
        'attribute_name': attr_name
    }
    if map_index:
        return_dict['parser_item'] = map_index
    if default_value:
        return_dict['default_value'] = default_value
    if mappings:
        return_dict['mappings'] = mappings
    return return_dict

def generate_menu_item_dict(id, allow_type):
    return {
        'id': id,
        'allow_type': allow_type
    }
