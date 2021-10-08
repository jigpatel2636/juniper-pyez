#!/usr/bin/env python3.8
from jnpr.junos import Device
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import getpass


def lldp_patch(dev):
    # try:
    #     with Device(host=device, user=username, password=password, auto_probe=10) as dev:
    rpc = dev.rpc.get_software_information()
    data_string = ET.tostring(rpc)
    data_xml = ET.fromstring(data_string)
    
    if data_xml.find('junos-version').text == '19.4R2-S3.2':
        lst = []
        for package in data_xml:
            for data in package.findall('name'):
                lst.append(data.text)
        if 'lldp-patch-for-i40e-upgrade' in lst:
            print(f'{dev} - Pass')
        else:
            print(f'{dev} - Fail')
    else:
        pass
            
                
def RE_type(dev):
    # try:
    #     with Device(host='24.199.192.58', user=username, password=password, auto_probe=10) as dev:
    rpc = dev.rpc.get_chassis_inventory()
    RE_string = ET.tostring(rpc)
    RE_data_xml = ET.fromstring(RE_string)
    # print(RE_data_xml)
    is_REX6 = False
    for data in RE_data_xml.findall('chassis'):
        for module in data.findall('chassis-module'):
            if module.find('description').text == 'RE-S-2X00x6':
                is_REX6 = True
    
    return is_REX6 


def audit(device):
    try:
        with Device(host=device, user=username, password=password, auto_probe=10) as dev:
            RE_Type = RE_type(dev)
            if RE_Type :
                lldp_patch(dev)

    except ConnectError as err:
        print(f"Failed to connect to device {device} with Error {err}  ")
    except ConnectAuthError as autherr:
        print(f"{device} Error {autherr} ")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device} - {toerr}")  


ipfile = input("Enter ipfile name: ")
username = input("Enter username: ")
password = getpass.getpass("Enter password: ")

with open(ipfile) as f:
    ips = f.readlines()

devices = []
for ip in ips:
    devices.append(ip.strip())
NUM_PROCESSES = 20



def main():
    pool = Pool(processes=NUM_PROCESSES)
    pool.map(audit, devices)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()

