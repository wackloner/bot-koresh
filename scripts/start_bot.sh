#!/bin/bash


echo
KORESH_HOME="/home/wackloner/PycharmProjects/moshnar-bot"
echo "KORESH_HOME=$KORESH_HOME"
SCRIPT_LOG="$KORESH_HOME/.logs/total.log"
echo

"$KORESH_HOME"/scripts/init_tor.sh
echo

"$KORESH_HOME"/scripts/start_mongodb.sh
echo

while true
do
   ~/.local/share/virtualenvs/moshnar-bot-vNaJ8oUp/bin/python3.8 "$KORESH_HOME/main.py" | tee -a $SCRIPT_LOG
   sleep 1
done
