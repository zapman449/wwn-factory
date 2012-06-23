#!/bin/bash

URL='http://localhost:8080/wwn_fabric'

FQDN='repdb3b00.be.weather.com'

SYSPATH='/tmp/sys/class/fc_host/'
#SYSPATH='/sys/class/fc_host/'

for fchost in ${SYSPATH}/host* ; do
    if [ -f ${fchost}/vport_create ]; then
        fabric=`cat ${fchost}/fabric_name | sed "s/^0x//"`
        #echo "getting ${URL}/${FQDN}/${fabric}"
        result=`curl --silent ${URL}/${FQDN}/${fabric}`
        #echo " -- FQDN: $FQDN -- Fabric ${fabric} -- Result ${result} -- "
        #echo "-- $fabric --"
        echo "echo \"$result\" > ${fchost}/vport_create"
    fi
done
