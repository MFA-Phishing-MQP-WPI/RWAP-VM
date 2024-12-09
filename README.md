# RWAP-VM


## configure req
```bash
apt install gnome-terminal
sudo apt install -y hostapd
sudo apt install -y dnsmasq
sudo apt install -y aircrack-ng iptables-persistent net-tools
pip install mitmproxy --break-system-packages
```

## configure network adapter
```bash
sudo apt install -y linux-headers-$(uname -r) build-essential bc dkms git libelf-dev rfkill iw
mkdir -p ~/src
cd ~/src
git clone https://github.com/morrownr/8821au-20210708.git
cd 8821au-20210708
sudo ./install-driver.sh
> n
> y

<< SYSTEM RESTARTS BY ITSELF >>

sudo wifite --kill
```
