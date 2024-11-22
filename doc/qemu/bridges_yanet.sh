#!/bin/bash

build_bridge() {
	bridge_name=$1
	bridge_addresses=$2
	hosts=$3

	echo "Create bridge: $bridge_name"
	sudo ip link add $bridge_name type bridge

	echo "    up bridge"
	sudo ip link set dev $bridge_name up

	if [ -n "$bridge_addresses" ]; then
		echo "    set address: $bridge_addresses"
		sudo ip addr add $bridge_addresses dev $bridge_name
	fi
	
	echo $3 | tr "," "\n" | while read host; do
		echo "    add: $host"
		sudo ip link set dev $host master $bridge_name
	done
}

# Bridge A:
build_bridge "bridge_a" "" "host_a_eth0,router_eth0,yanet_a_eth0"

# Bridge B:
build_bridge "bridge_b" "" "host_b_eth0,router_eth1,yanet_b_eth0"

# Management bridge
build_bridge "bridge_man" "10.19.0.1/24" "host_a_eth1,host_b_eth1,router_eth2,yanet_a_eth1,yanet_b_eth1"

# Check bridges:
sudo bridge link show
