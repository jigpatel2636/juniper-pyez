#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

from jnpr.junos import Device
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import getpass


ipfile = input('Enter ip filename: ')
with open(ipfile) as f:
    ips = f.readlines()
devices = []
for ip in ips:
    ip = ip.strip()
    if ip != '':
        devices.append(ip)
NUM_PROCESSES = 20

user = input("Enter your username: ").strip()
pwd = getpass.getpass("Enter your password: ").strip()

# def policy_lookup(dev, policy, final):
#     rpc = '<configuration><policy-options><policy-statement></policy-statement></policy-options></configuration>'
#     rpc_data = dev.rpc.get_config(filter_xml=rpc)
#     rpc_string = ET.tostring(rpc_data)
#     rpc_xml = ET.fromstring(rpc_string)
#     # pprint(rpc_string)
#     # print(policy, len(policy))
#     final = {}
#     for data in rpc_xml.findall('.//policy-statement'):
#         found = data.find('name').text
#         if found == policy:
#             # print('found')
#             # breakpoint()
#             try:
#                 ebgp_check = data.find('apply-groups').text
#                 if ebgp_check == 'EBGP':
#                     final[policy] = 'pass'
                    
#             except:
#                 final[policy] = 'fail'
#     # print(final)
#     return final

def video_vlan(device):
    try:
        with Device(host=device, user='junospace', password='twc##jun1p', auto_probe=10) as dev:
            vlans_filter = '<configuration><vlans><vlan></vlan></vlans></configuration>'
            vlan = dev.rpc.get_config(filter_xml=vlans_filter)
            vlan_string = ET.tostring(vlan)
            vlan_xml = ET.fromstring(vlan_string)
            # print(vlan_string)
            for data in vlan_xml.findall(".//name"):
                val = data.text
                if 'VIDEO' in val:
                    print(device, val)
            
    except ConnectError as err:
        print(f"Failed to connect to device {device} ")
    except ConnectAuthError as autherr:
        print(f"Authentication Error for device {device}")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device}")    




def main():
    pool = Pool(processes=NUM_PROCESSES)
    pool.map(video_vlan, devices)
    pool.close()
    pool.join()       

if __name__ == "__main__":
    main()
