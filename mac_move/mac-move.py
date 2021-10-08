#!/usr/bin/env python3.8

from jnpr.junos import Device
from lxml import etree
import xml.etree.ElementTree as ET
import getpass
username = input("UsernName: ")
password = getpass.getpass("Password: ")

with open('ipfile') as f:
    ips = f.readlines()

for ip in ips :
    with Device(host=ip.strip(), user=username, password=password) as dev:
        rpc = dev.rpc.get_l2_learning_mac_move_buffer_information(detail=True)
        rpc_string = ET.tostring(rpc)
        rpc_xml =  ET.fromstring(rpc_string)
        #print(type(rpc_xml))
        data = {}
        for item in rpc_xml.findall('l2ald-mac-move-entry'):
            if 'CMS' in item.find('l2ald-mac-move-bridge-domain').text:
                if data['mac_address']:
                    data['mac_address'] = [data['mac_address'].append(item.find('l2ald-mac-address').text)]
                if data['time']:
                    data['time'] = [data['time'].append(item.find('l2ald-mac-move-time-rec').text)]
                if item.find('l2ald-mac-move-bridge-domain').text:
                    if data['instance_name']: 
                        data['instance_name'] = [data['instance_name'].append(item.find('l2ald-mac-move-bridge-domain').text)]
    print(ip, '-', data)
