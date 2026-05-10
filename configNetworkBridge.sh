


NIC=ens192

IP=$(ip add sh $NIC|grep -w inet|cut -d' ' -f 6|cut -d'/' -f 1)
MASK=$(ip add sh $NIC|grep -w inet|cut -d' ' -f 6|cut -d'/' -f 2)
GW=$(route -n|grep ^0.0.0.0|awk -F' ' '{print $2}')
DNS=$(cat /etc/resolv.conf|grep ^nameserver|cut -d' ' -f 2)

cat > /etc/sysconfig/network-scripts/ifcfg-br0 <<-EOF
TYPE=Bridge
STP=yes
BOOTPROTO=none
DEVICE=br0
ONBOOT=yes
IPADDR=$IP
PREFIX=$MASK
GATEWAY=$GW
DNS1=$DNS
EOF


cat >/etc/sysconfig/network-scripts/ifcfg-$NIC <<-EOF
TYPE=Ethernet
DEVICE=$NIC
NAME=$NIC
ONBOOT=yes
BRIDGE=br0
EOF
