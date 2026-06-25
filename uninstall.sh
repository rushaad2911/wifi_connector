#!/bin/bash

sudo systemctl stop wifi-connector
sudo systemctl disable wifi-connector

sudo rm -f /etc/systemd/system/wifi-connector.service

sudo systemctl daemon-reload

echo "BUX WiFi Connector removed."