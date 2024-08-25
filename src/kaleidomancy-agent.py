import signal
import sys

import usb
import pipe

def sigtermHandler(signalNum, stackFrame):
    raise Exception("SIGTERM Caught")

if __name__ == '__main__':
    print('Start of Kaleidomancy Agent Log')

    print('Installing signal handler...')
    signal.signal(signal.SIGTERM, sigtermHandler)
    print('Signal handler installed')

    if len(sys.argv) != 2:
        raise Exception("no pipe path given")

    with pipe.maintain(sys.argv[1]) as getCmds, usb.maintainBus() as sendMsg:
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
