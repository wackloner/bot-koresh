#!/bin/bash


echo
KORESH_HOME=~/bot-koresh
echo "KORESH_HOME=$KORESH_HOME"
SCRIPT_LOG="$KORESH_HOME/.logs/total.log"
echo

"$KORESH_HOME"/scripts/init_tor.sh
echo

"$KORESH_HOME"/scripts/start_mongodb.sh
echo

while true
do
   ~/.pyenv/versions/3.8.5/bin/pipenv run python3 "$KORESH_HOME/main.py" | tee -a $SCRIPT_LOG
   sleep 1
done
