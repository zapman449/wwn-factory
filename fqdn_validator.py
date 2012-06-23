#!/usr/bin/python

import re

def validate_FQDN(FQDN) :
    """This needs to be externalized to a configfile, and removed for
       other peoples use
    """
    domain = re.search('\.(atl|be|fe|twc|dmz)\.weather\.com$', 
                       FQDN, re.IGNORECASE)
    if domain == None :
        return False
    node = get_node_from_FQDN(FQDN)
    if node == None :
        return False
    return True

def get_node_from_FQDN(FQDN) :
    """Take a given FQDN, and determine which node it lives in"""
    if FQDN.startswith('pr') or FQDN.startswith('dv') or \
            FQDN.startswith('qa') or FQDN.startswith('de') :
        if FQDN[2] == 't' :
            return '0'
        if FQDN[2] == 'e' :
            return '2'
        if FQDN[2] == 'c' :
            return '1'
        return None
    re0 = re.search('0[bx][0-9][0-9]', FQDN)
    re1 = re.search('1[bx][0-9][0-9]', FQDN)
    re2 = re.search('2[bx][0-9][0-9]', FQDN)
    re3 = re.search('3[bx][0-9][0-9]', FQDN)
    if re0 :
        return '0'
    if re1 :
        return '1'
    if re2 :
        return '2'
    if re3 :
        return '3'
    return None

def simple_validate(FQDN) :
    if FQDN.endswith('.com') :
        return True
    return False
