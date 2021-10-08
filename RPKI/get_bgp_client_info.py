#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import getpass

def collect_bgp_client(device):
    try:
        with Device(host=device, user=user, password=pwd, auto_probe=10) as dev:
            rpc = dev.rpc.get_config('<configuration><protocols><bgp></bgp></protocols></configuration>')
            rpc_string = ET.tostring(rpc)
            rpc_xml = ET.fromstring(rpc_string)

            grp = []
            for data in rpc_xml.findall('.//group'):
                grp_name = data.find('name').text
                if grp_name == 'IBGP-RR-IPV4' :
                    continue
                if grp_name == 'IBGP-RR-IPV6':
                    continue
                grp.append(grp_name)

            if grp:
                print(f'{device} ~  {grp}')
            else:
                print(f'{device} ~ No')

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
NUM_PROCESSES = 20

user = input("Enter your username: ").strip()
pwd = getpass.getpass("Enter your password: ").strip()

for device in devices:
    collect_bgp_client(device)

# def main():
#     pool = Pool(processes=NUM_PROCESSES)
#     pool.map(collect_bgp_client, devices)
#     pool.close()
#     pool.join()       

# if __name__ == "__main__":
#     main()
