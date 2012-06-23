#!/usr/bin/python

import sys

import wwn_factory
import fqdn_validator

CREATE = False

def USAGE() :
    print "%s -h            Print this help messages" % sys.argv[0]
    print "%s FQDN          Print existing WWNN and WWPN or error out" % sys.argv[0]
    print "%s create FQDN   Print existing WWNN and WWPN, or create new and print" % sys.argv[0]

def check_arguments() :
    """Check the command line arguments"""
    global CREATE
    if len(sys.argv) == 1 :
        USAGE()
        sys.exit()
    if sys.argv[1] in ('-h', '--help') :
        USAGE()
        sys.exit()
    if sys.argv[1] == 'listall' or sys.argv[1] == 'ALL' :
        return 'ALL'
    if sys.argv[1] in ('CREATE', 'create', 'Create') :
        CREATE = True
        del sys.argv[1]
    if len(sys.argv) != 2 :
        print 'bad argument count'
        USAGE()
        sys.exit()
    FQDN = sys.argv[1]
    if fqdn_validator.validate_FQDN(FQDN) :
        return FQDN
    else :
        print """invalid FQDN! 
Needs to end with (atl|twc|dmz|be|fe).atl.weather.com.
Or needs to begin with (pr|qa|dv|dr) and have (tce) as third letter.
Or needs to match [0-3][xb][0-9][0-9].
Exiting"""
        sys.exit(1)

def printer(ahost) :
    """Print to a terminal a single host"""
    print """--- %s ---
         wwnn %s
fabric-A wwpn %s
fabric-B wwpn %s""" % ahost

if __name__ == '__main__' :
    FQDN = check_arguments()
    wwn_factory.initialize()
    if FQDN == 'ALL' :
        hosts = wwn_factory.get_all_hosts()
        for host in hosts :
            printer(host)
    elif CREATE :
        success, host = wwn_factory.create(FQDN)
        if success :
            print 'successfully created wwn set for %s' % host.FQDN
        else :
            print 'host %s already exists!' % host.FQDN
        printer(host)
    else :
        printer(wwn_factory.get_host(FQDN))
