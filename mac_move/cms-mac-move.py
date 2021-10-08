#!/usr/bin/env python3

# for cronjob -- /homes/jigpatel/pyez/CMS/mac-move-audit.py --username regress --password MaRtInI --ipfile ipfile
# 

from jnpr.junos import Device
from pprint import pprint
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from lxml import etree
from pprint import pprint
import multiprocessing
import getpass
import argparse
import time

def mac_move_knob(dev,ip):
    knob = '<configuration><routing-instances></routing-instances></configuration>'
    data = dev.rpc.get_config(filter_xml=knob, options={'format': 'xml'})
    rpc_string = etree.tostring(data, encoding='unicode')
    rpc_xml = ET.ElementTree(ET.fromstring(rpc_string))

    root = rpc_xml.getroot()
    rs_name = []
    for instance in root:
        # print(sys.tag)
        for info in instance:
            instance_name = info.find('./name')
            knob_applied = info.find('./apply-groups-except')
            if instance_name != None and 'CMS' in instance_name.text and knob_applied is None :
                rs_name.append(instance_name.text)
    if not rs_name:
        #rs_name = 'None'
        return 'None'
    else:

        return f'{ip}--> {rs_name} - don\'t have apply-group-except knob enabled \n'

def connect_device(ip):
    filename = time.strftime('output-%Y-%m-%d')
    try:
        with Device(host=ip, user=my_dict['username'], password=my_dict['password']) as dev:
            
            opt_out = mac_move_knob(dev,ip)
            if opt_out != 'None':
                with open(filename, 'a') as fn:
                    fn.write(opt_out)

    except ConnectError as err:
        print(f"Failed to connect to device {ip} with Error {err}  ")
    except ConnectAuthError as autherr:
        print(f"{ip} Error {autherr} ")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {ip} - {toerr}")


NUM_PROCESSES = 20
# ipfile = input("Enter ip file name: ")
# user = input("UserName: ").strip()
# password = getpass.getpass("Password: ").strip()
parser = argparse.ArgumentParser()
parser.add_argument('--username')
parser.add_argument('--password')
parser.add_argument('--ipfile')
args = parser.parse_args()

my_dict = {'username': args.username, 'password': args.password, 'ipfile': args.ipfile}
with open(my_dict['ipfile']) as file:
    ip_lst = file.readlines()

devices=[]
for ip in ip_lst:
    devices.append(ip.strip())

def main():
    # time_start = time.time()
    with multiprocessing.Pool(processes=NUM_PROCESSES) as process_pool:
        process_pool.map(connect_device, devices)
        process_pool.close()
        process_pool.join()

if __name__ == "__main__":
    main()

