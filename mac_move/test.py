#!/usr/bin/env python3.8

from jnpr.junos import Device
import xml.etree.ElementTree as ET
from jnpr.junos.utils.start_shell import StartShell
import getpass

with Device(host='24.199.192.127', user='junospace', password='twc##jun1p') as dev:
    with StartShell(dev) as ss:
        if ss.run('cli','>')[0]:
            if ss.run('request routing-engine login other-routing-engine','>')[0]:
                data = ss.run("show system switchover",'>')
    for i in data:
        print(i)
