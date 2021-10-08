#!/usr/bin/env python3.8
# -*- coding: utf-8 -*
from jnpr.junos import Device
from jnpr.junos.exception import *
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import getpass

with Device(host='24.199.192.3', user='junospace', password='twc##jun1p', auto_probe=10) as dev:
    filter = '''<configuration><protocols><bgp/></protocols></configuration>'''
    rsp = dev.rpc.get_config(filter_xml=filter, options={'format':'set'})
    print(rsp.text)