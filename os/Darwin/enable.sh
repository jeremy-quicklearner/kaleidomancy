#!/bin/bash
set -e

DARWINDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"
KMDIR=$(dirname $(dirname $DARWINDIR))
RUNTIMEDIR=$KMDIR/runtime

TEMPLATEPATH=$DARWINDIR/com.github.jeremy-quicklearner.kaleidomancy-agent.plist.template
EXPANDPATH=$RUNTIMEDIR/com.github.jeremy-quicklearner.kaleidomancy-agent.plist
INSTALLPATH=~/Library/LaunchAgents/com.github.jeremy-quicklearner.kaleidomancy-agent.plist

# If the plist exists, the Kaleidomancy Agent is already installed
if [ -f $INSTALLPATH ]; then
    echo "[enable][darwin] plist exists. Kaleidomancy Agent is already installed"
    exit 1
fi

# Expand template
cat $TEMPLATEPATH | sed s?%ROOTDIR%?"$KMDIR"?g > $EXPANDPATH

# Install service so launchd will run it on login and stop it on logout
echo "[enable][darwin] Installing plist to ~/Library/LaunchAgents..."
cp $EXPANDPATH $INSTALLPATH

# Start the service now as well
echo "[enable][darwin] Bootstrapping agent..."
launchctl bootstrap gui/$(id -u) $INSTALLPATH
