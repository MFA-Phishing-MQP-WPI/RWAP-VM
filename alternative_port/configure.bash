echo "[ ] setting up your system ..."
apt install gnome-terminal
sudo apt install -y hostapd
sudo apt install -y dnsmasq
echo "[*] configuring terminals, hostapd dnsmasq"

sudo apt install -y aircrack-ng iptables-persistent net-tools
echo "[*] configuring net tools systems successfully"

pip install mitmproxy --break-system-packages
echo "[*] installing mitmproxy successfully"

chmod +x fakeap.sh
echo "[*] updated security settings successfully"
