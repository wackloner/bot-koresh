#!/bin/bash

#pipenv install
#source .env

tor_instances=$(pgrep tor -c)
if (( tor_instances == 0 ))
then
  tor &
fi

while true
do
   ~/.local/share/virtualenvs/moshnar-bot-vNaJ8oUp/bin/python3.8 ~/PycharmProjects/moshnar-bot/main.py
   sleep 1
done
