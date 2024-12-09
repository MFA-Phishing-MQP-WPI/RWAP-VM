echo "[ ] configuring terminals, hostapd dnsmasq"
apt install gnome-terminal
sudo apt install -y hostapd
sudo apt install -y dnsmasq

echo "[ ] configuring net tools systems"
sudo apt install -y aircrack-ng iptables-persistent net-tools

echo "[ ] installing mitmproxy"
pip install mitmproxy --break-system-packages

echo "[ ] updating security settings"
chmod +x fakeap.sh
