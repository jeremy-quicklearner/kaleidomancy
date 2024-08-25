import os
import fcntl
import contextlib

@contextlib.contextmanager
def maintain(path):
    pipepath = os.path.join(path, "pipe")
    rlockpath = os.path.join(path, "rlock")

    if not os.path.exists(pipepath):
        raise Exception('Command pipe does not exist')
    if not os.path.exists(rlockpath):
        raise Exception('Reader Lock does not exist')

    print('Acquiring Reader Lock...')
    rlock = open(rlockpath, 'w')
    fcntl.flock(rlock, fcntl.LOCK_EX)

    try:
        print('Command pipe created. Ready for commands')
        def getCmds():
            while True:
                with open(pipepath, 'r') as cmdPipe:
                    # Each line is one command
                    for cmd in cmdPipe:
                        yield cmd

        yield getCmds()
    finally:
        print('Releasing Reader Lock...')
        fcntl.flock(rlock, fcntl.LOCK_UN)
        rlock.close()
        print('Reader Lock released')
