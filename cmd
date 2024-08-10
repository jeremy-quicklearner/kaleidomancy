#!/bin/bash
set -e

# All Kaleidomancy stuff goes in the directory this script is in
KMDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

# If the pipe doesn't exist, the Kaleidomancy Agent already isn't running
RUNTIMEDIR=$KMDIR/runtime
if ! [ -p $RUNTIMEDIR/kaleidomancy-cmds ]; then
    echo "[cmd] pipe not found. Kaleidomancy Agent is already not running"
    exit 1
fi

# This mess with eval and pipes is to buffer everything before obtaining the lock
if [ "$1" = "-" ]; then
    eval 'echo "$(cat -)"' | flock -w 10 $RUNTIMEDIR/lock cat > $RUNTIMEDIR/kaleidomancy-cmds
else
    eval echo $@ | flock -w 10 $RUNTIMEDIR/lock cat > $RUNTIMEDIR/kaleidomancy-cmds
fi
