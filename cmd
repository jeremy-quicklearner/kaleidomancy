#!/bin/bash
set -e

# All Kaleidomancy stuff goes in the directory this script is in
KMDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

# Make sure the runtime dir exists
RUNTIMEDIR=$KMDIR/runtime
if ! [ -d $RUNTIMEDIR ]; then
    echo "[cmd] runtime not found. Please run setup first"
    exit 1
fi

# If the Reader Lock is not held, no Kaleidomancy Agent or forwarder is running
CMDDIR=$RUNTIMEDIR/cmds
RLOCK=$CMDDIR/rlock
if flock -n $RLOCK echo "[cmd] Reader Lock is free"; then
    echo "[cmd] Reader Lock is not held. No Kaleidomancy Agent or Forwarder present to consume commands"
    exit 1
fi

# This mess with eval and pipes is to buffer everything before obtaining the Writer Lock
WLOCK=$CMDDIR/wlock
if [ "$1" = "-" ]; then
    eval 'echo "$(cat -)"' | flock -w 10 $WLOCK cat > $CMDDIR/pipe
else
    eval echo $@ | flock -w 10 $WLOCK cat > $CMDDIR/pipe
fi
