#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from jinja2 import Template
from multiprocessing import Pool
import getpass

def fpc_pic_info(dev):
    rpc = dev.rpc.get_pic_information()
    rpc_string = ET.tostring(rpc)
    rpc_xml = ET.fromstring(rpc_string)

    # print(rpc_xml)
    fpc_dict = {}
    for fpc in rpc_xml.findall('fpc'):
        if fpc.find('state').text == 'Online':
            fpc_slot = fpc.find('slot').text
            pic_num = []
            for pic in fpc.findall('pic'):
                if pic.find('pic-state').text == 'Online':
                    pic_num.append(pic.find('pic-slot').text)
            
        fpc_dict[fpc_slot] = pic_num
    return fpc_dict

def wavelength(dev, fpc_slot, pic_slot):
    rpc = dev.rpc.get_pic_detail(fpc_slot=fpc_slot, pic_slot=pic_slot)
    rpc_string = ET.tostring(rpc)
    rpc_xml = ET.fromstring(rpc_string)
    # print(rpc_xml)

    for fpc in rpc_xml.findall('fpc'):
        for pic in fpc.findall('pic-detail'):
            for port_info in pic.findall('port-information'):
                for port in port_info.findall('port'):
                    port_num = port.find('port-number').text
                    wavlength_info = port.find('wavelength').text
                    if_speed = port.find('cable-type').text
                    part_num = port.find('sfp-vendor-pno').text
                    if '10GBASE' in if_speed.split():
                        print(f'xe-{fpc_slot}/{pic_slot}/{port_num}, Wavelength - {wavlength_info}')
                    elif 'GIGE' in if_speed.split():
                        print(f'ge-{fpc_slot}/{pic_slot}/{port_num}, Wavelength - {wavlength_info}')
                    elif '40GBASE' in if_speed.split():
                        print(f'et-{fpc_slot}/{pic_slot}/{port_num} - 40G, Wavelength - {wavlength_info}')
                    elif '100GBASE' in if_speed.split():
                            print(f'et-{fpc_slot}/{pic_slot}/{port_num} - 100G, Wavelength - {wavlength_info}')
                    elif if_speed == 'unknown cable':
                        if 'XFP' in part_num.split('-'):
                            print(f'xe-{fpc_slot}/{pic_slot}/{port_num}, Wavelength - {wavlength_info}')
                        elif 'SFP' in part_num.split('-'):
                            print(f'ge-{fpc_slot}/{pic_slot}/{port_num}, Wavelength - {wavlength_info}')
                            
def main():
    try:
        with Device(host=device, user=username, password=password) as dev:
            print(f'Connected to {device}')
            slot_dict = fpc_pic_info(dev)
            for fpc_slot, pic_list in slot_dict.items():
                for pic_slot in pic_list:
                    wavelength(dev, fpc_slot, pic_slot)

    except ConnectError as err:
        print(f"Failed to connect to device {device} ")
    except ConnectAuthError as autherr:
        print(f"Authentication Error for device {device}")
    except ConnectTimeoutError as toerr:
        print(f"Device timeout {device}")

device = input('Enter device IP Address: ')
username = input("Enter Username: ")
password = getpass.getpass()

if __name__ == "__main__":
    main()