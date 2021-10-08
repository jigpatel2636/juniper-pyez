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

def policy_lookup(dev, policy, final):
    rpc = '<configuration><policy-options><policy-statement></policy-statement></policy-options></configuration>'
    rpc_data = dev.rpc.get_config(filter_xml=rpc)
    rpc_string = ET.tostring(rpc_data)
    rpc_xml = ET.fromstring(rpc_string)
    # pprint(rpc_string)
    # print(policy, len(policy))
    final = {}
    for data in rpc_xml.findall('.//policy-statement'):
        found = data.find('name').text
        if found == policy:
            # print('found')
            # breakpoint()
            try:
                ebgp_check = data.find('apply-groups').text
                if ebgp_check == 'EBGP':
                    final[policy] = 'pass'
                    
            except:
                final[policy] = 'fail'
    # print(final)
    return final

def ebgp_group(device):
    try:
        with Device(host=device, user=user, password=pwd, auto_probe=10) as dev:
            bgp_group = '<configuration><protocols><bgp></bgp></protocols></configuration>'
            bgp_data = dev.rpc.get_config(filter_xml=bgp_group)
            group_string = ET.tostring(bgp_data)
            group_xml = ET.fromstring(group_string)
            # print(group_xml)
            final = {}
            for data in group_xml.findall('.//group'):
                if data.find('accept-remote-nexthop') is not None:
                    import_list = data.findall('import')
                    if import_list :
                       for im_policy in import_list:
                           if im_policy.text != 'RPKI-COMMUNITIES' :
                               policy = im_policy.text
                    else:
                        grup_name = data.find('name').text
                        final[grup_name] = f'Import is not configured for bgp group {grup_name}'
                        # print(final)
                    policy_split = policy.split('&&')
                    if len(policy_split) == 2:
                        customer_policy = policy_split[0][2:].strip()
                        # print('calling policy lookup function')
                        lookup = policy_lookup(dev, customer_policy, final)
                        final.update(lookup)

            print(f'{device} ~ {final}')
    except ConnectError as err:
        print(f"Failed to connect to device {device} ")
    except ConnectAuthError as autherr:
        print(f"Authentication Error for device {device}")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device}")    

# for device in devices:
#     ebgp_group(device)

def main():
    pool = Pool(processes=NUM_PROCESSES)
    pool.map(ebgp_group, devices)
    pool.close()
    pool.join()       

if __name__ == "__main__":
    main()
