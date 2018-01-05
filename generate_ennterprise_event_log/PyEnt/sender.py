# -*- coding: utf-8 -*-

import socket
import time
import logging
log = logging.getLogger(__name__)


class Sender(object):
    def __init__(self, host, port=514):
        """Sender class init function
        
        :param host: host server ip
        :param port: host port, default is 514, SYSLOG port
        """
        self._addr = (host, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def get_local_ip(self):
        """Get local IP
        
        :return: local IP addr
        """
        return [(s.connect(('114.114.114.114', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    def send_string(self, msg, count=1):
        """Send SYSLOG msg to host server
        
        :param msg: msg to send
        :param count: send count
        :return: None
        """
        for i in range(count):
            try:
                self._socket.sendto(msg, self._addr)
            except Exception:
                raise Exception

    def send_file(self, file, count=1):
        """Send file content to host server
        
        :param file: file path
        :param count: send count per line
        :return: None
        """
        with open(file) as pf:
            for line in pf:
                line = line.strip()
                if not line:
                    break
                self.send_string(line, count)

    def __del__(self):
        """Sender class destruct function
        
        :return: None
        """
        try:
            self._socket.close()
        except:
            pass


