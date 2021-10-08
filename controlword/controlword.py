#!/usr/bin/env python3.8

from os import write
from jnpr.junos import Device
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import os.path
import csv
import getpass
from pprint import pprint


def control_word(device):
    try:
        with Device(host=device, user=username, password=password, auto_probe=10) as dev:
            print(f"connected to {device}")
            rpc = dev.rpc.get_config(filter_xml='<configuration><groups><name>DEFAULTS</name></groups></configuration>')
            rpc_string = ET.tostring(rpc)
            rpc_xml = ET.fromstring(rpc_string)
            # pprint(rpc_string)
            # # print(rpc_xml)
            header = ['Device','status']
            file_exists = os.path.isfile(filename)
            f = open(filename, 'a+')
            writer = csv.DictWriter(f, fieldnames=header)
            if not file_exists:
                writer.writeheader()
            # for data in rpc_xml.findall('groups'):
            #     # if data.find('name').text == 'DEFAULTS':
            #     for rs in data.findall('routing-instances'):
            #         for inst in rs.findall('instance'):
            #             if inst.find('name').text.split('.')[1][0:4] == 'ELAN':
            #                 for proto in inst.findall('protocols'):
            #                     for vpls in proto.findall('vpls'):
            #                         if vpls.find('control-word'):
            #                             print('cw')
            #                             output = str(vpls.find('control-word'))
            #                             cw = output.split()[1]
            #                             csv_write = {'Device':device, 'status':cw}
            #                         else:
            #                             print('no cW')
            
            if rpc_xml.findall('.//vpls'):
                vpls = rpc_xml.findall('.//vpls')
                
                for data in vpls :
                    if data.find('.//control-word') != 'None':
                        cw_mem = str(data.find('.//control-word'))
                        cw = {'Device':device, 'status':cw_mem}
                writer.writerow(cw)
                
            else:
                cw = {'Device':device, 'status':'None'}
                writer.writerow(cw)
        
        f.close()
    except ConnectError as err:
        print(f"Failed to connect to device {device} ")
    except ConnectAuthError as autherr:
        print(f"Authentication Error for device {device}")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device}")

    return   

device_list = input("Enter device list file name: ")
filename= device_list +'-data.csv'
devices = []
with open(device_list) as f:
    ips = f.readlines()
for hostname in ips:
    devices.append(hostname.strip())

username = input('Enter your username: ').strip()
password = getpass.getpass()
NUM_PROCESSES = 20

def main ():
    pool = Pool(processes=NUM_PROCESSES)
    pool.map(control_word, devices)
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()