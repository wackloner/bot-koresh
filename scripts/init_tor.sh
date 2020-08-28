#!/bin/bash


tor_instances=$(ps -e | grep " tor" -c)
if (( tor_instances == 0 ))
then
  echo "Tor isn't running, launching..." && sudo -u wackloner tor &>/dev/null & disown

  # TODO: make timeout bigger, but chech bootstrap status and exit on done
  echo "Waiting 60 seconds for tor to bootstrap..." && sleep 60
fi

# TODO: wait for tor to bootstrap, wait, exit on timeout

tor_instances=$(ps -e | grep " tor" -c)
if (( tor_instances == 0 ))
then
  echo "Failed to launch Tor, exiting..." && exit 1
fi

echo "Now $tor_instances Tor instances are running."
