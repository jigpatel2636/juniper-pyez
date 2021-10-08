#!/usr/bin/env python3.8
from jnpr.junos import Device
from pprint import pprint
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from lxml import etree
from pprint import pprint
import multiprocessing
import getpass

def sorc(dev,ip):
    knob = '<configuration><system></system></configuration>'
    data = dev.rpc.get_config(filter_xml=knob, options={'format': 'xml'})
    rpc_string = etree.tostring(data, encoding='unicode')
    rpc_xml = ET.ElementTree(ET.fromstring(rpc_string))
    # if 'switchover-on-routing-crash' in data['configuration']['system']:
    #     return f'{ip}->switchover-on-routing-crash is enable'
    # return f'{ip} ->switchover-on-routing-crash is NOT configured'
    root = rpc_xml.getroot()

    for sys in root:
        # print(sys.tag)
        for info in sys:
            if info.tag == "switchover-on-routing-crash" :
                return f'{ip} - True'
    return f"{ip} - False"
    
def connect_device(ip):
    try:
        with Device(host=ip, user=user, password=password) as dev:
            
            sorc_exist = sorc(dev,ip)
            print(sorc_exist)

    except ConnectError as err:
        print(f"Failed to connect to device {ip} with Error {err}  ")
    except ConnectAuthError as autherr:
        print(f"{ip} Error {autherr} ")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {ip} - {toerr}") 



NUM_PROCESSES = 20
file = input("filename:").strip()
user = input("UserName: ").strip()
password = getpass.getpass("Password: ").strip()
with open(file) as file:
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

