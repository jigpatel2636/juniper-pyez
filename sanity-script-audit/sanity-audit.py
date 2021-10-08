#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import getpass

def script_audit(dev):
    filt = '<configuration><system><scripts><commit></commit></scripts></system></configuration>'
    rpc = dev.rpc.get_config(filter_xml=filt)
    rpc_string = ET.tostring(rpc)
    rpc_xml = ET.fromstring(rpc_string)
    
    script = []
    for config in rpc_xml:
        for system in config:
            for comm in system:
                for f in comm:
                    for info in f.findall('name'):
                        if info.text == 'Sanity.slax' or info.text == 'Sanity-L3.slax' or info.text == 'Sanity-L-all.slax':
                            script.append(info.text)
    return script

def collection(device):
    try:
        with Device(host=device, user=username, password=password, auto_probe=10) as dev:
            output = script_audit(dev)
            print(f"{device} - {output}")

    except ConnectError as err:
        print(f"Failed to connect to device {device} ")
    except ConnectAuthError as autherr:
        print(f"Authentication Error for device {device}")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device}")

ipfile = input("Enter device filename: ")
username = input("Enter Username: ")
password = getpass.getpass()

with open(ipfile) as f:
    ips = f.readlines()
devices = []
for ip in ips:
    ip = ip.strip()
    if ip != '':
        devices.append(ip)
NUM_PROCESSES = 20

def main():
    pool = Pool(processes=NUM_PROCESSES)
    pool.map(collection, devices)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()