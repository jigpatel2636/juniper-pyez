from netmiko.ssh_exception import SSHException, AuthenticationException, NetMikoTimeoutException
import threading
import os.path
from time import time
import csv
from jnpr.junos import Device
import getpass

username = input("Enter your username: ").strip()
password = getpass.getpass("Password: ").strip()

def config_worker(device):
    data = {}
    ip = device.strip()
    try:
        with Device(host=ip, user=username, passwd=password) as dev:
            dev.open()
            response = dev.rpc.get_chassis_inventory()
            data = [{'Model' : response.findtext("chassis/description"),
                     'Serial Number' : response.findtext("chassis/serial-number"),
                     'IP Address': ip
            }]
        update_data(data)
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

def update_data(data_i):
    file_exists = os.path.isfile('chassis-data.csv')
    with open('chassis-data.csv', 'a', newline='') as file:
        csv_writer = csv.DictWriter(file, fieldnames=['IP Address', 'Model', 'Serial Number'])
        if not file_exists:
            csv_writer.writeheader()
        csv_writer.writerows(data_i)

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

