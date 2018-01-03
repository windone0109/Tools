# -*- coding:utf-8 -*-

import os
import json
import time
from random import randrange
import socket
import re


#
def set_enterprise_ip():
    while True:
        HOST = raw_input('输入企业版IP地址: ')
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', HOST):
            return HOST
            break

def set_log_number():
    while True:
        a = raw_input('发送log数量 : ')
        if a.isdigit():
            if int(a) > 0:
                return int(a)
                break

log_field = ['@timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port']
raw_log_path = './nta_json_sample/'

def set_timestamp():
    nowTime = lambda: int(round(time.time() * 1000))
    return nowTime()


def set_internetip():
    from random import randrange
    intraip = [10, 127, 169, 172, 192]
    first = randrange(1, 256)
    while first in intraip:
        first = randrange(1, 256)
    ip = ".".join([str(first), str(randrange(1, 256)), str(randrange(1, 256)), str(randrange(1, 256))])
    return ip


def set_intranetip():
    intraip = ["172.16", "192.168"]
    prefixIp = intraip[randrange(0, 2)]
    ip = ".".join([str(prefixIp), str(randrange(1, 256)), str(randrange(1, 256))])
    return ip


def parse_json(raw_log_file):
    with open(raw_log_file,'r') as f:
        json_log = ''
        for line in f.readlines():
            line = line.strip("    ")
            line = line.strip('\r\n')
            json_log = json_log + line

        return json_log


def update_json_log(raw_log_file):

    data = []

    update_json = json.loads(parse_json(raw_log_file), 'utf-8')

    if update_json.has_key('timestamp'):
        update_json['timestamp'] = set_timestamp()
    else:
        update_json['@timestamp'] = set_timestamp()
    update_json['src_ip'] = set_internetip()
    update_json['dst_ip'] = set_internetip()
    update_json['src_port'] = randrange(0, 65536)
    update_json['dst_port'] = randrange(0, 65536)
    data = json.dumps(update_json)

    return data


def send_json(raw_log_file, host, iter_times):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        HOST = host
        PORT = 9293
        s.connect((HOST, PORT))

        count = 0
        # print send_json_log

        for i in range(int(iter_times)):

            send_json_log = update_json_log(raw_log_file)
            s.sendall(send_json_log)

            count = count + 1
            if count % 1000 == 0:
                time.sleep(1)
                
        print "Send '%s' file '%s' times success." % (raw_log_file, count)
    except BaseException as err:
        print "Send '%s' file failed, check it please!" % raw_log_file
    finally:
        s.close()


def start():

    host = set_enterprise_ip()
    iter_times = set_log_number()
    print iter_times

    starttime = time.time()
    print "Start time: " + str(starttime)

    for log_file in os.listdir(raw_log_path):
        print "Start send %s" % log_file
        send_json(raw_log_path + log_file, host, iter_times)

    endtime = time.time()
    print "End time: " + str(endtime)

    costtime = float(endtime) - float(starttime)
    print "Cost time: %s" % costtime


if __name__ == '__main__':

    start()
