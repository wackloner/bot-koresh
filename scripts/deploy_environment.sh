#!/bin/bash


while read p; do
  heroku config:set "$p"
done < .env
