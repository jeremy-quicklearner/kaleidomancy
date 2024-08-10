#!/usr/local/bin/python3

import os
import sys
import hid
import time
import signal
import contextlib

vendor_id     = 0x4B50
product_id    = 0xEF8D
usage_page    = 0xFF60
usage         = 0x61
report_length = 32

def sigtermHandler(signalNum, stackFrame):
    raise Exception("SIGTERM Caught")

@contextlib.contextmanager
def maintainCmdPipe(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        raise Exception("pipe already exists")

    try:
        os.mkfifo(path)

        def cmdGen():
            while True:
                with open(path, 'r') as cmdPipe:
                    # Each line is one command
                    for cmd in cmdPipe:
                        yield cmd

        yield cmdGen()
    finally:
        os.remove(path)

def get_raw_hid_interface():
    device_interfaces = hid.enumerate(vendor_id, product_id)
    raw_hid_interfaces = [i for i in device_interfaces if i['usage_page'] == usage_page and i['usage'] == usage]

    if len(raw_hid_interfaces) == 0:
        return None

    interface = hid.Device(path=raw_hid_interfaces[0]['path'])

#    print(f"Manufacturer: {interface.manufacturer}")
#    print(f"Product: {interface.product}")

    return interface

def send_raw_report(data):
    interface = get_raw_hid_interface()

    if interface is None:
        #print("No device found")
        return

    request_data = [0x00] * (report_length + 1) # First byte is Report ID
    request_data[1:len(data) + 1] = data
    request_report = bytes(request_data)

#    print("Request:")
#    print(request_report)

    try:
        interface.write(request_report)

#        response_report = interface.read(report_length, timeout=1)
#        print("Response:")
#        print(response_report)
    finally:
        interface.close()

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, sigtermHandler)

    if len(sys.argv) != 2:
        raise Exception("no pipe path given")

    with maintainCmdPipe(sys.argv[1]) as cmdGen:
        i = 0
        chars = [
            0x52,
            0x47,
            0x42,
        ]

        for cmd in cmdGen:
            print("COMMAND: ", cmd.strip())
            send_raw_report([
                chars[i % 3],
                chars[i % 3],
            ])
            i += 1
