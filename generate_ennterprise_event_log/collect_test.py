# -*- coding: utf-8 -*-

import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import socket
from PyEnt import PyEnt
from PyEnt.sender import Sender
from pprint import pprint
#local_host = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
local_host = '172.16.106.150'


host = "172.16.106.150" #"ent.qa.hansight.work"
username = 'admin'
password = 'S3cur!ty'

#Generated Variables
console_url = "https://{host}".format(host=host)

ent = PyEnt(console_url, username=username, password=password)

types = {
            'event': ['Event'],
            'parser': ['Event', 'ParseRule'],
            'intelligence': ['Intelligence'],
            'knowledge': ['Knowledge_AttackData'],
            'cep': ['Event', 'Intelligence', 'CEP_Analysis'],
            'component': ['Component'],
            'dashboard': ['Component', 'Dashboard'],
        }
#cfg = ent.get_resource("AssetView")
#cfg.export_module('a.zip', 'parser')
#cfg.import_module('a.zip')
#print cfg.get_score('org')


def _get_event():
    # event.py
    from datetime import date
    Event = ent.get_resource('Event')
    event_list = Event.list(date(2017, 5, 22))
    print len(event_list)
    for e in event_list:
        if len(e['attrValueList'][3]['showVal']) == 0:
            print e


def _send_msg():
    # eventparser.py
    EventParser = ent.get_resource('EventParser')
    event_parsers = EventParser.list()

    sender = Sender(host=host, port=514)
    cnt = 0
    for item in event_parsers:
        cnt = cnt + 1
        sender.send_string(item['orgEventContent'].decode("utf-8"))
        print cnt, item['id'], item['parserName'], (item['orgEventContent'])

def disable_cep_rule():
    #from random import randrange
    # eventparser.py
    ceprule = ent.get_resource('CepRule')
    ceprules = ceprule.list()
    for item in ceprules:
        ceprule.stop(str(item['id']))


def _create_collector():
    #from random import randrange
    # eventparser.py
    EventParser = ent.get_resource('EventParser')
    event_parsers = EventParser.list()
    Collector = ent.get_resource('Collector')
    Collector.delete_all()
    log_dict = {}
    for item in event_parsers:
        parser_id = item['id']
        collector_id = Collector.create(name='collector_'+parser_id, type='syslog', host_address=local_host, charset='utf-8', parser_rules=[parser_id])
        print 'create collector', collector_id
        log_dict[collector_id] = item['orgEventContent']

def _create_one_collector():
    #from random import randrange
    # eventparser.py
    EventParser = ent.get_resource('EventParser')
    event_parsers = EventParser.list()
    Collector = ent.get_resource('Collector')
    Collector.delete_all()
    rule_list = []
    for item in event_parsers:
        parser_id = item['id']
        rule_list.append(parser_id)
    print len(rule_list)
    collector_id = Collector.create(name='collector'+local_host, type='syslog', host_address=local_host, charset='utf-8', parser_rules=rule_list)
    print 'create collector', collector_id



def _check_performance():
    # eventparser.py
    ptn = re.compile(ur'解析单条样例日志耗时:(.+),解析(.+)条背景数据耗时:(.+)')
    EventParser = ent.get_resource('EventParser')
    event_parsers = EventParser.list()
    for i in event_parsers:
        #reg parse performance

        try:
            msg = EventParser.parse(i['id'])
            cost_time = ptn.search(msg).group()
            print i['id'], i['parserName'], cost_time
        except:
            print i['id'], i['parserName'], 'error', msg
        # reg parse correction
        pattern = i['regex']
        content = i['orgEventContent']
        b_matched = re.search(pattern, content, re.I)

        if not b_matched:
            print i['id'],  i['parserName'], 'not matched'


def _sub_dst_ip(dst_ip, content):
    return re.sub(r'dst_ip:((?:\d{1,3}\.){3}\d{1,3})', 'dst_ip:' + dst_ip, content)


def _sub_src_ip(src_ip, content):
    return re.sub(r'src_ip:((?:\d{1,3}\.){3}\d{1,3})', 'src_ip:'+ src_ip, content)


def _sub_stat_time(time, content):
    return re.sub(r'stat_time:(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{1,2}:\d{1,2})','stat_time:'+ time, content)


def internet_ip():
    from random import randrange
    intraip = [10, 127, 169, 172, 192]
    first = randrange(1, 256)
    while first in intraip:
        first = randrange(1, 256)
    ip = ".".join([str(first), str(randrange(1, 256)), str(randrange(1, 256)), str(randrange(1, 256))])
    return ip

def intranet_ip():
    from random import randrange
    intraip = ["172.16", "192.168"]
    prefixIp = intraip[randrange(0, 2)]
    
    ip = ".".join([str(prefixIp), str(randrange(1, 256)), str(randrange(1, 256))])
    return ip

def _send_event_log(send_days = 30, log_perday = 100, srcip_type = 'external', dstip_type = 'external'):
    import time
    import datetime
    content = r'<11>Feb 18 11:12:23 localhost waf: tag:waf_log_websec site_id:1428395845  protect_id:2442566278  dst_ip:172.17.100.105  dst_port:80  src_ip:211.22.90.249  src_port:28684  method:UNKNOWN  domain:None  uri:None  alertlevel:MEDIUM  event_type:HTTP_Protocol_Validation  stat_time:2017-02-18 11:12:19  policy_id:1  rule_id:0  action:Block  block:No  block_info:None  http:  alertinfo:request method begin with non-capital letters or over load content-lenth  proxy_info:None  characters:None  count_num:1  protocol_type:HTTP  wci:None  wsi:None'
    for n in range(send_days):
        for i in range(log_perday):
            if i%5 == 0:
                if srcip_type == 'internal':
                    src_ip = intranet_ip()
                else:
                    src_ip = internet_ip()
            if i%2 == 0:
                if dstip_type == 'internal':
                    dst_ip = intranet_ip()
                else:
                    dst_ip = internet_ip()

            dt = (datetime.datetime.now()+datetime.timedelta(days=-n)).strftime("%Y-%m-%d %H:%M:%S")
            #dt = time.strftime("%Y-%m-%d %X", time.localtime())
            send_cont = _sub_stat_time(dt, _sub_dst_ip(dst_ip, _sub_src_ip(src_ip, content)))
            print send_cont
            # dt = time.strftime("%Y-%m-%d %X", time.gmtime(time.mktime((2016, 2, 17, 1, 1, 1, 1, 1, 0))))
            # send_cont = _sub_stat_time(dt, content)
            sender = Sender(host=host, port=514)
            sender.send_string(send_cont)
            #time.sleep(3)

def _generate_data():
    import time
    content = r'<11>Feb 18 11:12:23 localhost waf: tag:waf_log_websec site_id:1428395845  protect_id:2442566278  dst_ip:172.17.100.105  dst_port:80  src_ip:211.22.90.249  src_port:28684  method:UNKNOWN  domain:None  uri:None  alertlevel:MEDIUM  event_type:HTTP_Protocol_Validation  stat_time:2017-02-18 11:12:19  policy_id:1  rule_id:0  action:Block  block:No  block_info:None  http:  alertinfo:request method begin with non-capital letters or over load content-lenth  proxy_info:None  characters:None  count_num:1  protocol_type:HTTP  wci:None  wsi:None'
    with open('data.txt', 'w') as pf:
        for i in range(10):
            src_ip = internet_ip()
            dst_ip = internet_ip()
            dt = time.strftime("%Y-%m-%d %X", time.localtime())
            send_cont = _sub_stat_time(dt, _sub_dst_ip(dst_ip, _sub_src_ip(src_ip, content)))
            pf.write(send_cont)
            pf.write('\n')
            # dt = time.strftime("%Y-%m-%d %X", time.gmtime(time.mktime((2016, 2, 17, 1, 1, 1, 1, 1, 0))))
            # send_cont = _sub_stat_time(dt, content)

        #time.sleep(3)



#_create_one_collector()

_send_event_log(30, 100, 'external', 'external')
_send_event_log(30, 100, 'external', 'internal')
_send_event_log(30, 100, 'internal', 'internal')

# _create_collector()
#_send_msg()
#_get_event()
#_send_lm_alarm()
#_check_performance()
#_generate_data()
