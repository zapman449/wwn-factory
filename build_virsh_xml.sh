#!/bin/bash

fabrics=fabric_names

virsh nodedev-list --cap=scsi_host | while read shost ; do
    if [ -f /sys/class/fc_host/${shost#scsi_}/vport_create ] ; then
        # ok: this proves 1) this is a FC host, and 2) that it's a root
        # fc host, rather than a NPIV vHBA
        fname=`cat /sys/class/fc_host/${shost#scsi_}/fabric_name`
	fabricname=`echo $fname | sed 's/^0x//'`
	cat $fabrics | grep -v "^#" | sed 's/://g' | \
		      while read switchwwn name node fabricletter rest ; do
            if [ "$switchwwn" = "$fabricname" ] ; then
                echo $shost $name
            fi
        done
    fi
done
