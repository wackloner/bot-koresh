#!/bin/bash

sudo systemctl daemon-reload
sudo systemctl enable bot
sudo systemctl start bot
sudo systemctl status bot

sudo systemctl daemon-reload && sudo systemctl enable bot && sudo systemctl start bot && sudo systemctl status bot