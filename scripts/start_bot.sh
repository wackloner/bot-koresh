#!/bin/bash


echo
KORESH_HOME=~/bot-koresh
echo "KORESH_HOME=$KORESH_HOME"
SCRIPT_LOG="$KORESH_HOME/.logs/total.log"
echo "FULL LOG: $SCRIPT_LOG"

"$KORESH_HOME"/scripts/init_tor.sh
echo

"$KORESH_HOME"/scripts/start_mongodb.sh
echo

while true
do
   # TODO: make the command common for all
   ~/.local/share/virtualenvs/moshnar-bot-vNaJ8oUp/bin/python3.8 "$KORESH_HOME/main.py" | tee -a $SCRIPT_LOG
   sleep 1
done
