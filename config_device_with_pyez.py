from paramiko.ssh_exception import SSHException, AuthenticationException
from netmiko.ssh_exception import SSHException, AuthenticationException, NetMikoTimeoutException
import json
from time import time
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import threading
import getpass

username = input("Enter your username: ").strip()
password = getpass.getpass("Password: ").strip()

def config_worker(device):
    ip = device.strip()
    try:
        with Device(host=ip, user=username, passwd=password) as dev:
            dev.open()
            with Config(dev, mode='private') as cu:
                cu.load(path='command.txt', format='set')
                cu.diff()
                if cu.commit_check():
                    cu.commit()
        return
    except(AuthenticationException):
        print('Authentication Failure: ' + device)
    except(NetMikoTimeoutException):
        print('Timeout to device: ' + device)
    except(EOFError):
        print(('End of file while attempting to device: '+ device))
    except(SSHException):
        print('SSH issue. Are you sure SSH is enabled? ' + device)
    except Exception as unknown_error:
        print('Some other error: ' + str(unknown_error))



with open('ipfile') as ip:
    ipaddr = ip.readlines()

starting_time = time()

config_thread_list = []

for device in ipaddr:
    print(f"creating thread for {device}")
    config_thread_list.append(threading.Thread(target=config_worker, args=(device,)))

print('\n -----------Begin get config threading ----------')
print(config_thread_list)
for config_thread in config_thread_list:
    config_thread.start()

for config_thread in config_thread_list:
    config_thread.join()

print(f'\n ------end get config threading , elapsed time = {time() - starting_time}')

