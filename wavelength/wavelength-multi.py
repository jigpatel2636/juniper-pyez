#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import csv
import os.path
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
    device = str(dev)
    device_name = device.split('(')[1]
    filename = device_name.rstrip(device_name[-1]) + '.csv'
    file_exists = os.path.isfile(filename)
    header = ['interface', 'Wavelength']
    with open(filename, 'a+') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        for fpc in rpc_xml.findall('fpc'):
            for pic in fpc.findall('pic-detail'):
                for port_info in pic.findall('port-information'):
                    for port in port_info.findall('port'):
                        port_num = port.find('port-number').text
                        wavlength_info = port.find('wavelength').text
                        if_speed = port.find('cable-type').text
                        part_num = port.find('sfp-vendor-pno').text
                        if '10GBASE' in if_speed.split():
                            if_name = f'xe-{fpc_slot}/{pic_slot}/{port_num}'
                            Ten_gig = {'interface': if_name, 'Wavelength': wavlength_info}
                            # print(f'xe-{fpc_slot}/{pic_slot}/{port_num} Wavelength - {wavlength_info}')
                            writer.writerow(Ten_gig)
                        elif 'GIGE' in if_speed.split():
                            if_name = f'ge-{fpc_slot}/{pic_slot}/{port_num}'
                            one_gig = {'interface': if_name , 'Wavelength': wavlength_info}
                            # print(f'ge-{fpc_slot}/{pic_slot}/{port_num} Wavelength - {wavlength_info}')
                            writer.writerow(one_gig)
                        elif '40GBASE' in if_speed.split():
                            if_name = f'et-{fpc_slot}/{pic_slot}/{port_num} - 40G'
                            forty_gig = {'interface': if_name, 'Wavelength': wavlength_info}
                            # print(f'et-{fpc_slot}/{pic_slot}/{port_num} Wavelength - {wavlength_info}')
                            writer.writerow(forty_gig)
                        elif '100GBASE' in if_speed.split():
                            if_name = f'et-{fpc_slot}/{pic_slot}/{port_num} - 100G'
                            hundred_gig = {'interface': if_name, 'Wavelength': wavlength_info}
                            # print(f'et-{fpc_slot}/{pic_slot}/{port_num} Wavelength - {wavlength_info}')
                            writer.writerow(hundred_gig)
                        elif if_speed == 'unknown cable':
                            if 'XFP' in part_num.split('-'):
                                if_name = f'xe-{fpc_slot}/{pic_slot}/{port_num}'
                                unknown_tengig = {'interface': if_name, 'Wavelength': wavlength_info}
                                writer.writerow(unknown_tengig)
                            elif 'SFP' in part_num.split('-'):
                                if_name = f'ge-{fpc_slot}/{pic_slot}/{port_num}'
                                unknown_onegig = {'interface': if_name, 'Wavelength': wavlength_info}
                                writer.writerow(unknown_onegig)

def collector(device):
    try:
        with Device(host=device, user=username, password=password, auto_probe=10) as dev:
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

ipfile = input('Enter ip filename: ')
with open(ipfile) as f:
    ips = f.readlines()
devices = []
for ip in ips:
    ip = ip.strip()
    if ip != '':
        devices.append(ip)
NUM_PROCESSES = 20

username = input("Enter your Username: ").strip()
password = getpass.getpass("Enter your Password: ")

def main():
    pool = Pool(processes=NUM_PROCESSES)
    pool.map(collector, devices)
    pool.close()
    pool.join()       

if __name__ == "__main__":
    main()