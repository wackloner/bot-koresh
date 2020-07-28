#!/bin/bash

tor_instances=$(ps -e | grep " tor" -c)
if (( tor_instances == 0 ))
then
  echo "TOR isn't running, trying to launch..."
  tor &
  disown
fi

tor_instances=$(ps -e | grep " tor" -c)
echo "Now $tor_instances TOR instances are running."
