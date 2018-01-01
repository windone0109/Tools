# -*- coding:utf-8 -*-

import os
import json
import time
from random import randrange
import socket
import re


#
HOST = '172.16.100.79'
def check_ip_validation():
    while True:
        HOST = raw_input('输入企业版IP地址: ')
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', HOST):
            break

LOG_NUMBER = 1
def check_log_number():
    while True:
        LOG_NUMBER = raw_input('发送log数量 : ')
        if LOG_NUMBER.isdigit():
            if int(LOG_NUMBER) > 0:
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
    # print json.dumps(update_json)
    for i in range(int(LOG_NUMBER)):
        update_json[log_field[0]] = set_timestamp()
        update_json[log_field[1]] = set_internetip()
        update_json[log_field[2]] = set_intranetip()
        update_json[log_field[3]] = randrange(0, 65536)
        update_json[log_field[4]] = randrange(0, 65536)
        data.append(json.dumps(update_json))
    return data


def send_json(raw_log_file):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        send_json_log = update_json_log(raw_log_file)

        PORT = 9293
        s.connect((HOST, PORT))

        count = 0
        # print send_json_log

        for log in send_json_log:
            s.sendall(log)
            count = count + 1
            if count % 1000 == 0:
                time.sleep(1)
        print "Send '%s' file success." % raw_log_file
    except BaseException as err:
        print "Send '%s' file failed, check it please!" % raw_log_file
    finally:
        s.close()


if __name__ == '__main__':

    check_ip_validation()
    check_log_number()
    print "Start time: " + str(time.time())
    for log_file in os.listdir(raw_log_path):
        print "Start send %s" % log_file
        send_json(raw_log_path + log_file)
    print "End time: " + str(time.time())
