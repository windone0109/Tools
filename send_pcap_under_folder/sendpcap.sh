#!/bin/env bash

#find ./ -name "*.pcap" > pcap.log
find ./ -type f -print0 | xargs -0 rename ' ' ''

for file in `find ./ -name "*.pcap"`
do
	ls -l $file
	tcpreplay --mbps=1mbps --intf1=ens35 $file
done
