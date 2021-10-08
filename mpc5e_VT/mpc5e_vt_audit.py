#!/usr/bin/env python3.8
from jnpr.junos import Device
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import getpass
import os
import csv


def mpc5e_vt_op(dev):
    rpc = dev.rpc.get_config(filter_xml='<system><scripts></scripts></system>')
    data_string = ET.tostring(rpc)
    data_xml = ET.fromstring(data_string)
    # print(data_xml)
    is_op = 'No'
    for data in data_xml.iter():
        if data.tag == 'name' and data.text == 'adjbmr-op.slax':
            is_op = 'Yes'

    return is_op

def mpc5e_vt_event(dev):
    rpc = dev.rpc.get_config(filter_xml='<event-options></event-options>')
    data_string = ET.tostring(rpc)
    data_xml = ET.fromstring(data_string)
    # print(data_xml)
    is_event = 'No'
    for data in data_xml.iter():
        if data.tag == 'name' and data.text == 'adjbmr-event.slax':
            is_event = 'Yes'
    return is_event
            
def audit(device):
    try:
        #print(f"Connecting to device {device}")
        with Device(host=device, user=username, password=password, auto_probe=10) as dev:
            print(f"connected to {device}")
            op = mpc5e_vt_op(dev)
            event = mpc5e_vt_event(dev)
            data = {'Device':device, 'adjbmr-op':op, 'adjbmr-event':event}
            file_exists = os.path.isfile(filename)
            header = ['Device', 'adjbmr-op', 'adjbmr-event']
            with open(filename, 'a+') as file:
                writer = csv.DictWriter(file, fieldnames=header)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
            
           
    except ConnectError as err:
        print(f"Failed to connect to device {device} with Error {err}  ")
    except ConnectAuthError as autherr:
        print(f"{device} Error {autherr} ")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device} - {toerr}")
    except ProbeError as prberr:
        print(f"Prob error {device} - {prberr}")

    return



ipfile = input("Enter ipfile name: ")
with open(ipfile) as f:
    ips = f.readlines()

filename = ipfile + '-data.csv'

devices = []
for ip in ips:
    devices.append(ip.strip())
NUM_PROCESSES = 20

username = input("Enter username: ")
password = getpass.getpass("Enter password: ")

def main():
    pool = Pool(processes=NUM_PROCESSES)
    pool.map(audit, devices)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()

