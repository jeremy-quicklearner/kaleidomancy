#!/usr/local/bin/python3

import os
import sys
import time
import signal
import contextlib

import usb

def sigtermHandler(signalNum, stackFrame):
    raise Exception("SIGTERM Caught")

@contextlib.contextmanager
def maintainCmdPipe(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        raise Exception("pipe already exists")

    try:
        print('Creating command pipe...')
        os.mkfifo(path)
        print('Command pipe created. Ready for commands')

        def getCmds():
            while True:
                with open(path, 'r') as cmdPipe:
                    # Each line is one command
                    for cmd in cmdPipe:
                        yield cmd

        yield getCmds()
    finally:
        print('Removing command pipe...')
        os.remove(path)
        print('Command pipe removed')

if __name__ == '__main__':
    print('Start of Kaleidomancy Agent Log')

    print('Installing signal handler...')
    signal.signal(signal.SIGTERM, sigtermHandler)
    print('Signal handler installed')

    if len(sys.argv) != 2:
        raise Exception("no pipe path given")

    with maintainCmdPipe(sys.argv[1]) as getCmds, usb.maintainBus() as sendMsg:
        i = 0
        chars = [
            0x52,
            0x47,
            0x42,
        ]

        for cmd in getCmds:
            print("COMMAND: ", cmd.strip())
            sendMsg('kbd-60-rgbmat', [
                chars[i % 3],
                chars[i % 3],
            ])
            i += 1
