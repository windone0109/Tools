# -*- coding: utf-8 -*-

import json

from ._internal_utils import status_code_check, response_status_check, convert_date_time

from datetime import datetime, date, timedelta
import logging
log = logging.getLogger(__name__)

class GlobalTrend(object):
    def __init__(self, console_url, session=None):
        self._console_url = console_url
        self._session = session
        self._linkurl_dict = {
            'all_stage_data': self._console_url + '/alarm/monitor/allStageData',
            'all_alarm_data': self._console_url + '/alarm/monitor/allAlarmData',
            'all_type_radar_data': self._console_url + '/alarm/monitor/allTypeRadarData',
            'alarm_level_pie_data': self._console_url + '/alarm/monitor/alarmLevelPieData',
            'latest_alarm_data': self._console_url + '/alarm/monitor/latestAlarmData',
            'focus_alarm_type_data': self._console_url + '/alarm/monitor/foucusAlarmTypeData',
            'focus_asset_data': self._console_url + '/alarm/monitor/foucusAssetsData',
            'alarm_dstaddr_top10_data': self._console_url + '/alarm/monitor/alarmDstAddressTopTenData',
            'alarm_level_trend_data': self._console_url + '/alarm/monitor/AlarmLevelTrendData',
            'alarm_stage_distribution_data': self._console_url + '/alarm/monitor/alarmStageDistributionData',
            'alarm_attack_mapchart_data': self._console_url + '/alarm/monitor/alarmAttackMapChartData',
            'alarm_srcaddr_top10_datalist': self._console_url + '/alarm/monitor/alarmSrcAddressTopTenDataList',
            'alarm_dstaddr_top10_datalist': self._console_url + '/alarm/monitor/alarmDstAddressTopTenDataList',
            'event_intr_data': self._console_url + '/alarm/monitor/eventIntranetChartData',
            'event_srcintr_top10': self._console_url + '/alarm/monitor/eventSrcIpIntranetTopTen',
            'event_dstintr_top10': self._console_url + '/alarm/monitor/eventDstIpIntranetTopTen',
            'alarm_intr_cnt': self._console_url + '/alarm/monitor/alarmCountIntranet',
            'event_intr_cnt': self._console_url + '/alarm/monitor/eventCountIntranet',
            'inner_topo': self._console_url + '/dashboard/inner/topo',
            'inner_srctop': self._console_url + '/dashboard/inner/srcTop',
            'inner_dsttop': self._console_url + '/dashboard/inner/dstTop',
            'inner_bug': self._console_url + '/dashboard/inner/bug',
            'inner_alarm': self._console_url + '/dashboard/inner/alarm',
            'inner_event': self._console_url + '/dashboard/inner/event',
            'asset_type': self._console_url + '/dashboard/inner/assetType'
        }
        self._items = {
            '3d_trend': ['all_stage_data', 'all_alarm_data', 'alarm_level_trend_data', 'alarm_attack_mapchart_data',
                         'alarm_srcaddr_top10_datalist', 'alarm_dstaddr_top10_datalist' ],
            'outside_trend': ['all_stage_data', 'latest_alarm_data', 'alarm_level_trend_data', 'alarm_attack_mapchart_data',
                              'alarm_srcaddr_top10_datalist', 'alarm_dstaddr_top10_datalist'],
            'inside_trend_dev': ['inner_topo', 'inner_srctop', 'inner_dsttop', 'inner_bug', 'inner_alarm', 'inner_event', 'asset_type'],
            'inside_trend': ['inner_bug', 'inner_topo', 'event_intr_data', 'event_srcintr_top10', 'event_dstintr_top10', 'alarm_intr_cnt', 'event_intr_cnt', 'asset_type'],
            'alarm_trend': ['all_stage_data', 'all_alarm_data', 'all_type_radar_data', 'alarm_level_pie_data', 'latest_alarm_data',
                            'focus_alarm_type_data', 'focus_asset_data', 'alarm_dstaddr_top10_data', 'alarm_level_trend_data',
                            'alarm_stage_distribution_data']
        }

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def retrive_url(self, uri, start_time, end_time):
        """retrive url, 
        
        :param uri: uri link
        :param start_time: start time, timestamp format
        :param end_time: end time, timestamp format 
        :return: response
        """
        payload = {
            'startTime': start_time,
            'endTime': end_time,
            'preStartTime': str(int(start_time)-86400),
            'preEndTime': str(int(end_time)-86400)
        }
        response = self._session.post(uri, json=payload)
        status_code_check(response.status_code, 200)
        response_content = json.loads(response.content)

        response_status_check(response_content['statusCode'], 0, response_content['messages'])
        try:
            return response_content['data']
        except:
            return response_content

    def get_item_info(self, item, start_time=date.today(), end_time=date.today() + timedelta(days=+1), arg=None):
        """Get item info, post request for each
        
        :param item: item name, support 5 kinds currently
        :param start_time: start time, date format
        :param end_time: end time, date format
        :param arg: other args, specify one type in item
        :return: dict format
        """
        ret_info = {}
        if arg is not None:
            index = self._items[item].index(arg)
            assert index != -1
            ret_info[arg] = self.retrive_url(self._linkurl_dict[arg], convert_date_time(start_time), convert_date_time(end_time))
        else:

            for req_index in self._items[item]:
                ret_info[req_index] = self.retrive_url(self._linkurl_dict[req_index], convert_date_time(start_time), convert_date_time(end_time))
        return ret_info



