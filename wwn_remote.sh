#!/bin/bash

URL='http://localhost:8080/wwn_fabric'

#FQDN='repdb3b00.be.weather.com'

SYSPATH='/tmp/sys/class/fc_host/'
#SYSPATH='/sys/class/fc_host/'

if [ "$1" = "create" ] || [ "$1" = "CREATE" ] ; then
    VPORT="vport_create"
elif [ "$1" = "destroy" ] || [ "$1" = "DESTROY" ] || [ "$1" = "delete"] || [ "$1" = "DELETE" ] ; then
    VPORT="vport_delete"
else 
    echo "USAGE: $0 <create|delete> FQDN"
    exit
fi

shift

if [ -z "$1" ]; then
    echo "USAGE: $0 <create|delete> FQDN"
    exit
else
    FQDN=$1
fi

for fchost in ${SYSPATH}/host* ; do
    if [ -f ${fchost}/${VPORT} ]; then
        fabric=`cat ${fchost}/fabric_name | sed "s/^0x//"`
        #echo "getting ${URL}/${FQDN}/${fabric}"
        result=`curl --silent ${URL}/${FQDN}/${fabric}`
        #echo " -- FQDN: $FQDN -- Fabric ${fabric} -- Result ${result} -- "
        #echo "-- $fabric --"
        echo "echo \"$result\" > ${fchost}/${VPORT}"
    fi
done
