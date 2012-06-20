#!/usr/bin/python

"""a program to generate (or return) 1 WWNN and 2 WWPN's for a given vhost."""

import random
import re
import sys
import logging
from collections import namedtuple

hostdef = namedtuple('hostdef', 'FQDN wwnn wwpn_a wwpn_b')

hostdata = {}
# central DB to hold host -> (wwnn, wwpn-a, wwpn-b) data.
fabricdata = {}

HOST_DEF_FILE = 'host_data'
FABRIC_DEF_FILE = 'fabric_names'

FIRSTOCTETS = "5f:0a:22:50"
# 5 + f:0a:22:5 + 0
# see http://howto.techworld.com/storage/156/how-to-interpret-worldwide-names/
# for details.  f0a225 is a private OUI according to:
# http://standards.ieee.org/develop/regauth/oui/oui.txt
# 5 indicates type 5, the trailing 0 is for padding.

def hostdefs_as_dict(hostdef_list) :
    """renders a list of hostdefs as a dictionary, keyed to the FQDN"""
    result = {}
    for ahost in hostdef_list :
        result[ahost.FQDN] = {}
        result[ahost.FQDN]['wwnn'] = ahost.wwnn
        result[ahost.FQDN]['wwpn_a'] = ahost.wwpn_a
        result[ahost.FQDN]['wwpn_b'] = ahost.wwpn_b
    return result

def read_fabrics() :
    """Read the FABRIC_DEF_FILE into a data structure"""
    fabfile = open(FABRIC_DEF_FILE, 'r')
    for line in fabfile :
        if line.startswith('#') :
            continue
        switchwwn, desc, node, fabric, ident = line.split()
        fabricdata[switchwwn] = fabric

def get_wwns_from_fabric(switchwwn, FQDN) :
    if switchwwn in fabricdata :
        fabric = fabricdata[switchwwn]
    else :
        return None, None
    ahost = get_host(FQDN)
    if ahost.wwnn == '' :
        return None, None
    if fabric == 'a' :
        return ahost.wwpn_a, ahost.wwnn
    elif fabric == 'b' :
        return ahost.wwpn_b, ahost.wwnn
    else :
        return None, None

def validate_FQDN(FQDN) :
    domain = re.search('\.(atl|be|fe|twc|dmz)\.weather\.com$', 
                       FQDN, re.IGNORECASE)
    if domain == None :
        return False
    node = get_node_from_FQDN(FQDN)
    if node == None :
        return False
    return True

def get_id_from_wwn(wwn) :
    """Take a wwn, and split out the unique id from it.  The unique ID will not
    have colons in it when done"""
    wwn2 = remove_colons(wwn)
    return wwn2[1:7]

def ensure_unique(random_id) :
    """Take a random_ID and ensure that it is unique in our system.  The odds
    of a collision are pretty small, but it exists"""
    idlist = []
    for h in hostdata.keys() :
        idlist.append(get_id_from_wwn(hostdata[h][0]))
    if random_id in idlist :
        return False
    return True

def gen_random_id(with_colons=True) :
    """Generate a random 6 digit hex id. Also runs ensure_unique on it to
    validate its unique"""
    for i in range(3) :
        # try three times to make a random int.  If it fails after that
        # there are bigger problems
        x = random.randint(0,16777215)
        y = "%x" % x
        if ensure_unique(y) :
            if with_colons :
                return add_colons(y)
            return y
    logging.critical("death! 3 random numbers collided with existing numbers")
    sys.exit(-1)

def add_colons(charstring, addchar=':') :
    """add colons to a string such that 00112233 becomes 00:11:22:33.
    Useful to transform World Wide Names back and forth"""
    chararray = list(charstring)
    length = len(chararray)
    if length % 2 == 0 :
        length -= 1
    for i in range(length,1,-1) :
        if i % 2 == 0 :
            chararray[i:i] = [addchar]
    return ''.join(chararray)

def remove_colons(charstring, removechar=':') :
    """remove colons from a string. useful to transform World wide names back
    and forth."""
    return charstring.replace(removechar, '')

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

def get_node_names() :
    """reads the node_data file and fills the hostdata dictionary"""
    db = open(HOST_DEF_FILE, 'r')
    for line in db :
        uline = line.strip()
        words = uline.split()
        if line.startswith('#') :
            continue
        if len(words) == 4 :
            FQDN = words[0]
            wwnn = add_colons(remove_colons(words[1]))
            wwpna = add_colons(remove_colons(words[2]))
            wwpnb = add_colons(remove_colons(words[3]))
            hostdata[FQDN] = (wwnn, wwpna, wwpnb)

def save_new_hostinfo(ahost) :
    """Write out the new wwn data to the state file"""
    db = open(HOST_DEF_FILE, 'a')
    line = "	".join([ahost.FQDN, ahost.wwnn, ahost.wwpn_a, ahost.wwpn_b])
    db.write(line + '\n')
    hostdata[ahost.FQDN] = (ahost.wwnn, ahost.wwpn_a, ahost.wwpn_b)

def create_wwns(node, unique_id) :
    """Generate the three wwns from FIRSTOCTETS, node, and unique_id"""
    wwnn = ':'.join([FIRSTOCTETS, node + 'f', unique_id])
    wwpna = ':'.join([FIRSTOCTETS, node + 'a', unique_id])
    wwpnb = ':'.join([FIRSTOCTETS, node + 'b', unique_id])
    return (wwnn, wwpna, wwpnb)

def get_host(FQDN) :
    if FQDN in hostdata :
        return hostdef(FQDN, *hostdata[FQDN])
    else :
        return hostdef('', '', '', '')

def get_all_hosts() :
    """returns all hosts"""
    results = []
    for FQDN in sorted(hostdata) :
        results.append(hostdef(FQDN, *hostdata[FQDN]))
    return results

def create(FQDN) :
    """if FQDN does not exist, make one.  Returns a tuple of True/False (for
    if it was created or if it already existed) and a hostdef"""
    if FQDN in hostdata.keys() :
        # already exists.
        ahost = hostdef(FQDN, *hostdata[FQDN])
        return (False, ahost)
    node = get_node_from_FQDN(FQDN)
    if node == None :
        logging.critical('Cannot determine node from name %s. Exiting.' % FQDN)
        ahost = hostdef('', '', '', '')
        return (False, ahost)
    unique_id = gen_random_id()
    wwnn, wwpn_a, wwpn_b = create_wwns(node, unique_id)
    ahost = hostdef(FQDN, wwnn, wwpn_a, wwpn_b)
    save_new_hostinfo(ahost)
    return (True, ahost)

def initialize() :
    get_node_names()
    read_fabrics()

if __name__ == '__main__' :
    pass
