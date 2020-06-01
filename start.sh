#!/bin/bash

pipenv install
source .env

while true
do
   /usr/bin/python3.8 main.py
   sleep 1
done
