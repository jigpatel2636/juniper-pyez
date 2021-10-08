#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from jinja2 import Template
from multiprocessing import Pool
import getpass


def bgp_filter(dev):
    bgp_group = '<configuration><protocols><bgp></bgp></protocols></configuration>'
    bgp_data = dev.rpc.get_config(filter_xml=bgp_group)
    group_string = ET.tostring(bgp_data)
    group_xml = ET.fromstring(group_string)
    var_data = {}
    for data in group_xml.findall('.//group'):
        if data.find('accept-remote-nexthop') is not None:
            group_name = data.find('name').text
            import_list = data.findall('import')
            if import_list :
                for im_policy in import_list:
                    if im_policy.text != 'RPKI-COMMUNITIES' :
                        policy_name = im_policy.text.strip()
                        var_data[group_name] = policy_name
            else:
                var_data[group_name] = ''
# print(var_data)   
    conf_file = Template(open('test.j2').read())
    rpki_data = conf_file.render(dict = var_data)

    print(rpki_data)

with Device(host='24.199.192.3', user='junospace', password='twc##jun1p') as dev:
    bgp_filter(dev)


# def asn_filter(dev):
#     asn = {}
#     asn_filter = '<configuration><routing-options><autonomous-system><as-number></as-number></autonomous-system></routing-options></configuration>'
#     as_data = dev.rpc.get_config(filter_xml=asn_filter, options={'format':'json'})
#     as_num = as_data['configuration']['routing-options']['autonomous-system']['as-number']
    
#     return as_num


# def ip_info(dev):
#     # with Device(host='10.93.22.6', user='CEN_Engineer', password='MaRtInI') as dev:
#     rpc = dev.rpc.get_interface_information(terse=True, interface_name='lo0', normalize='True')
#     lo_ipv6 = rpc.xpath(".//address-family[address-family-name='inet6']/interface-address/ifa-local")[0].text
    
#     return lo_ipv6

# def load_rpki_config(device):
#     try:
#         print(f"Connecting to device {device}")
#         with Device(host=device, user=user, password=pwd, auto_probe=10) as dev:
#             dev.timeout = 60
#             var_data = {}
#             # bgp_data = bgp_filter(dev,device)
#             bgp_data = bgp_filter(dev)
#             asn_data = asn_filter(dev)
#             ipv6 = ip_info(dev)
#             var_data = {'ASN': asn_data, 'ipv6':ipv6}
#             conf_file = Template(open('RPKI-ROV-v6-Template.j2').read())
#             rpki_data = conf_file.render(var_data)
#             print(rpki_data)
#             print(bgp_data)
#             print(ipv6)
#             # with open(os.path.join(path, device), 'r+') as f:
#             #     bgp_contents = f.read()
#             #     f.seek(0,0)
#             #     f.write(rpki_data+'\n'+bgp_contents)
#             try:
#                 with Config(dev, mode='private') as cu:
#                     # with open(device) as final_config:
#                     try:
#                         # conf = os.getcwd()+'/output/'+device
#                         cu.load(rpki_data, merge=True, format='set')
#                         cu.load(bgp_data, merge=True, format='set')
#                         # cu.pdiff()
#                         try:
#                             if cu.diff():
#                                 cu.commit(comment='RPKI Configuration') 
#                                 print(f"{device} Device Configured Successfully ")
#                             else:
#                                 print(f"Device {device} already configured")
#                         except CommitError as err:
#                             print(f"Unable to commit configuration: {device} - {err}") 
                    
#                     except (ConfigLoadError, Exception) as err:
#                         print(f"Unable to load configuration changes:{device} - {err}")
#                         print("Unlocking the configuration")
#                         try:
#                             cu.unlock()
#                         except UnlockError as err:
#                             print(f"Unable to unlock configuration:{device} - {err}")
#             except LockError as err:
#                 print(f"Lock Error {err}. Configuration database modified for {device}")
#             except RpcError as err:
#                 print(f"RPC error {err} for device {device}")

#     except ConnectError as err:
#         print(f"Failed to connect to device {device} ")
#     except ConnectAuthError as autherr:
#         print(f"Authentication Error for device {device}")
#     except ConnectTimeoutError as toerr:
#         print(f"Device timeout {device}")

#     return 


# # if not os.path.exists('output'):
# #     os.makedirs('output')
# #     path = os.getcwd()+'/output'
# # else:
# #     path = os.getcwd()+'/output'
# # conf_file = Template(open('new-config.j2').read())

# ipfile = input('Enter ip filename: ')
# with open(ipfile) as f:
#     ips = f.readlines()
# devices = []
# for ip in ips:
#     ip = ip.strip()
#     if ip != '':
#         devices.append(ip)
# NUM_PROCESSES = 20

# user = input("Enter your username: ").strip()
# pwd = getpass.getpass("Enter your password: ").strip()

# def main():
#     pool = Pool(processes=NUM_PROCESSES)
#     pool.map(load_rpki_config, devices)
#     pool.close()
#     pool.join()       

# if __name__ == "__main__":
#     main()
