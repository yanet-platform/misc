#!/bin/bash

sudo ip link delete br_host_a
sudo ip link delete tap_host_a
sudo ip link delete tap_yanet_ki0

sudo ip link delete br_host_b
sudo ip link delete tap_host_b
sudo ip link delete tap_yanet_kib

sudo ip link delete br_man
sudo ip link delete man_host_a
sudo ip link delete man_host_b
sudo ip link delete man_yanet
