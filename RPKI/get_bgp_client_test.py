#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

from jnpr.junos import Device
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
import getpass


def collect_bgp_client(device):
    try:
        with Device(host=device, user=user, password=pwd) as dev:
            bgp_group = '<configuration><protocols><bgp></bgp></protocols></configuration>'
            bgp_data = dev.rpc.get_config(filter_xml=bgp_group)
            group_string = ET.tostring(bgp_data)
            group_xml = ET.fromstring(group_string)

            # print(group_xml)
            final = []
            for data in group_xml.findall('.//group'):
                if data.find('accept-remote-nexthop') is not None:
                    grp_name = data.find('name').text
                    final.append(grp_name)
            print(f"{device} ~ {final}")
        
    except ConnectError as err:
        print(f"Failed to connect to device {device} ")
    except ConnectAuthError as autherr:
        print(f"Authentication Error for device {device}")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device}")

ipfile = input('Enter ip filename: ')
with open(ipfile) as f:
    ips = f.readlines()
devices = []
for ip in ips:
    ip = ip.strip()
    if ip != '':
        devices.append(ip)

user = input("Enter your username: ").strip()
pwd = getpass.getpass("Enter your password: ").strip()

for device in devices:
    collect_bgp_client(device)