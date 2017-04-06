#!/bin/bash
dstFile=$1
hName=$(hostname)
echo "127.0.0.1		localhost	localhost.localdomain	"$hName > $dstFile

