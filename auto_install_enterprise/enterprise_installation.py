# -*- coding:utf-8 -*-

import ftplib
import os
import sys
import fileinput
import argparse

ftp_server = '172.16.100.119'
port = 21
username = 'dev'
password = 'devnj'
bufsize = 10240

if len(sys.argv) < 2:
    print "Too few arguments, you should assign the file path.\n"
    print "You should run like this: python %s --help\n" % sys.argv[0]
    exit()

path = sys.argv[1]
ftp_path = path.replace('ftp://ftp.nj.hansight.work/','')
file_path = ftp_path.rsplit('/',1)[0]
file_name = ftp_path.rsplit('/')[-1]

# print file_path
# print file_name

def uninstallEnterprise():
    if os.path.exists('/opt/hansight/uninstall.sh'):
        os.system('cd ~ && sed -i "s/alias cp=\'cp -i\'//g" bashrc && cd -')
        os.system('cp -f /opt/hansight/tomcat/webapps/enterprise/WEB-INF/classes/ ./config/hansight-enterprise.lic')
        os.system('cd /opt/hansight && ./uninstall.sh && cd -')


def ftpdownloadfile():
    ftp = ftplib.FTP()
    ftp.set_debuglevel(2)
    ftp.connect(ftp_server, port)
    ftp.login(username, password)
    print ftp.getwelcome()
    ftp.cwd(file_path)
    file_handle = open(file_name, 'wb').write
    ftp.retrbinary('RETR '+file_name, file_handle, bufsize)
    ftp.set_debuglevel(0)
    ftp.close()


def installEnterprise():
    if os.path.exists(file_name):
        if os.path.exists('HansightEnterprise'):
            os.system('rm -fr HansightEnterprise')
        os.system('tar zxf '+file_name)
        with open("HansightEnterprise/conf/all_in_one.ini", 'r') as f_r:
            lines = f_r.readlines()
        with open("HansightEnterprise/conf/all_in_one.ini",'w') as f_w:
            for line in lines:
                # line = line.strip()
                if 'ES_MEM=16g\n' == line:
                    line = line.replace('ES_MEM=16g', 'ES_MEM=8g')
                if 'TOMCAT_MEM=8g\n' == line:
                    line = line.replace('TOMCAT_MEM=8g', 'TOMCAT_MEM=4g')
                if 'TOMCAT_MEM_NEW=5g\n' == line:
                    line = line.replace('TOMCAT_MEM_NEW=5g', 'TOMCAT_MEM_NEW=2g')
                if 'KAFKA_MEM=4g\n' == line:
                    line = line.replace('KAFKA_MEM=4g', 'KAFKA_MEM=2g')
                if 'CEP_MEM=16g\n' == line:
                    line = line.replace('CEP_MEM=16g', 'CEP_MEM=8g')
                if 'CEP_MEM_NEW=10g\n' == line:
                    line = line.replace('CEP_MEM_NEW=10g', 'CEP_MEM_NEW=5g')

                f_w.write(line)
                # if 'TOMCAT_MEM_NEW=5g' == line:
                #     line = line.replace('TOMCAT_MEM_NEW=5g', 'TOMCAT_MEM_NEW=2g')
                # if 'KAFKA_MEM=4g' == line:
                #     line = line.replace('KAFKA_MEM=4g', 'KAFKA_MEM=2g')
        os.system('cd HansightEnterprise/script/ && ./install.sh && cd -')
        os.system('systemctl stop firewalld.service')

def activate_enterprise():
    os.system('cd ~ && sed -i "s/alias cp=\'cp -i\'//g" bashrc && cd -')
    os.system('cp -f ./config/hansight-enterprise.lic /opt/hansight/tomcat/webapps/enterprise/WEB-INF/classes/')
    os.system('supervisorctl restart all')

if __name__ == '__main__':


    uninstallEnterprise()
    ftpdownloadfile()
    installEnterprise()
    activate_enterprise()


