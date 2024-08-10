#!/bin/bash
set -e

INSTALLPATH=~/Library/LaunchAgents/com.github.jeremy-quicklearner.kaleidomancy-agent.plist

# If the plist doesn't exist, the Kaleidomancy Agent is already not installed
if ! [ -f $INSTALLPATH ]; then
    echo "[disable][darwin] plist not found. Kaleidomancy Agent is already not installed"
    exit 1
fi

# Stop the service
echo "[disable][darwin] Bootout'ing agent..."
launchctl bootout gui/$(id -u) $INSTALLPATH

# Uninstall the service so launchd won't run it automatically
echo "[disable][darwin] Uninstalling plist from ~/Library/LaunchAgents..."
rm $INSTALLPATH
