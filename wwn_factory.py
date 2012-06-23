#!/usr/bin/python

"""a program to generate (or return) 1 WWNN and 2 WWPN's for a given vhost."""

import collections
import logging
import os
import os.path
import random
import re
import sqlite3
import sys

hostdef = collections.namedtuple('hostdef', 'FQDN wwnn wwpn_a wwpn_b')

hostdata = {}
# central DB to hold host -> (wwnn, wwpn-a, wwpn-b) data.
fabricdata = {}

SQLDB_FILE = 'san.db'
HOST_DEF_FILE = 'host_data'
FABRIC_DEF_FILE = 'fabric_names'

FIRSTOCTETS = "5f:0a:22:50"
# 5 + f:0a:22:5 + 0
# see http://howto.techworld.com/storage/156/how-to-interpret-worldwide-names/
# for details.  f0a225 is a private OUI according to:
# http://standards.ieee.org/develop/regauth/oui/oui.txt
# 5 indicates type 5, the trailing 0 is for padding.

class SanData(object) :
    def __init__(self) :
        self.connection = None
        self.cursor = None
        self.init_db()
        self.get_host_data()
        self.read_fabrics()

    def init_db(self) :
        try :
            self.connection = sqlite3.connect(SQLDB_FILE)
            self.cursor = self.connection.cursor()
        except  sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit()
        try :
            self.cursor.execute("SELECT Version FROM DbVersion")
        except sqlite3.Error, e:
            if e.args[0].startswith("no such table: ") :
                # proxy test for an empty DB
                self.make_tables()

    def make_tables(self) :
        """makes blank tables"""
        self.cursor.execute("CREATE TABLE DbVersion(Version INT)")
        self.cursor.execute("INSERT INTO DbVersion(Version) VALUES (1);")
        self.cursor.execute("CREATE TABLE Fabrics(SwitchWWN CHAR(23), Description CHAR(25), Fabric CHAR(1))")
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:1e:04:46:c5", "verizon-fabric-a", 'a') )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:1e:04:4f:28", "verizon-fabric-a", 'a') )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:1e:04:46:c5", "verizon-fabric-a", "a") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:1e:04:4f:28", "verizon-fabric-a", "a") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:73:0f:c9", "earthstation-fab-a", "a") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:72:f6:1a", "earthstation-fab-b", "b") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:1e:dd:3b:e1", "tc3-fabric-a", "a") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:73:64:d1", "tc3-fabric-a", "a") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:ca:6b:0f", "tc3-fabric-a", "a") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:73:68:15", "tc3-fabric-b", "b") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:1e:dd:2f:5d", "tc3-fabric-b", "b") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:cf:99:6b", "tc3-fabric-b", "b") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:c8:54:29", "tc3-broadcast-a", "a") )
        self.cursor.execute("INSERT INTO Fabrics VALUES (?, ?, ?);",
                      ("10:00:00:05:33:ca:6a:0b", "tc3-broadcast-a", "a") )
        #####
        self.cursor.execute("CREATE TABLE HostInfo(FQDN CHAR(100), WWNN CHAR(23), WWPNA CHAR(23), WWPNB CHAR(23))")
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("prtsys01.atl.weather.com", 
                               "5f:0a:22:50:0f:21:db:b4",
                               "5f:0a:22:50:0a:21:db:b4",
                               "5f:0a:22:50:0b:21:db:b4") )
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("jtest.atl.weather.com",
                               "5f:0a:22:50:0f:33:22:11",
                               "5f:0a:22:50:0a:33:22:11",
                               "5f:0a:22:50:0b:33:22:11"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("nas0b00.be.weather.com",
                               "5f:0a:22:50:0f:dd:d3:81",
                               "5f:0a:22:50:0a:dd:d3:81",
                               "5f:0a:22:50:0b:dd:d3:81"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("repdb3b00.be.weather.com",
                               "5f:0a:22:50:3f:f4:33:ab",
                               "5f:0a:22:50:3a:f4:33:ab",
                               "5f:0a:22:50:3b:f4:33:ab"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("zabbixdb3b00.be.weather.com",
                               "5f:0a:22:50:3f:f0:8d:3f",
                               "5f:0a:22:50:3a:f0:8d:3f",
                               "5f:0a:22:50:3b:f0:8d:3f"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("prtsys02.atl.weather.com",
                               "5f:0a:22:50:0f:dd:92:d8",
                               "5f:0a:22:50:0a:dd:92:d8",
                               "5f:0a:22:50:0b:dd:92:d8"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("zabbixdb3b01.be.weather.com",
                               "5f:0a:22:50:3f:8e:c5:2a",
                               "5f:0a:22:50:3a:8e:c5:2a",
                               "5f:0a:22:50:3b:8e:c5:2a"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("clouddb3b00.be.weather.com",
                               "5f:0a:22:50:3f:da:ca:62",
                               "5f:0a:22:50:3a:da:ca:62",
                               "5f:0a:22:50:3b:da:ca:62"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("repdb1b00.be.weather.com",
                               "5f:0a:22:50:1f:6f:3a:d3",
                               "5f:0a:22:50:1a:6f:3a:d3",
                               "5f:0a:22:50:1b:6f:3a:d3"))
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              ("repdb2b00.be.weather.com",
                               "5f:0a:22:50:2f:f3:8a:00",
                               "5f:0a:22:50:2a:f3:8a:00",
                               "5f:0a:22:50:2b:f3:8a:00"))
        self.connection.commit()

    def hostdefs_as_dict(self, hostdef_list) :
        """renders a list of hostdefs as a dictionary, keyed to the FQDN"""
        result = {}
        for ahost in hostdef_list :
            result[ahost.FQDN] = {}
            result[ahost.FQDN]['wwnn'] = ahost.wwnn
            result[ahost.FQDN]['wwpn_a'] = ahost.wwpn_a
            result[ahost.FQDN]['wwpn_b'] = ahost.wwpn_b
        return result

    def read_fabrics(self) :
        """Read the FABRIC_DEF_FILE into a data structure"""
        fabfile = open(FABRIC_DEF_FILE, 'r')
        for line in fabfile :
            if line.startswith('#') :
                continue
            switchwwn, desc, node, fabric, ident = line.split()
            fabricdata[switchwwn] = fabric

    def get_wwns_from_fabric(self, switchwwn, FQDN) :
        if switchwwn in fabricdata :
            fabric = fabricdata[switchwwn]
        else :
            return None, None
        ahost = self.get_host(FQDN)
        if ahost.wwnn == '' :
            return None, None
        if fabric == 'a' :
            return ahost.wwpn_a, ahost.wwnn
        elif fabric == 'b' :
            return ahost.wwpn_b, ahost.wwnn
        else :
            return None, None

    def validate_FQDN(self, FQDN) :
        """This needs to be externalized to a configfile, and removed for
           other peoples use
        """
        domain = re.search('\.(atl|be|fe|twc|dmz)\.weather\.com$', 
                           FQDN, re.IGNORECASE)
        if domain == None :
            return False
        node = self.get_node_from_FQDN(FQDN)
        if node == None :
            return False
        return True

    def get_id_from_wwn(self, wwn) :
        """Take a wwn, and split out the unique id from it.  The unique ID
           will not have colons in it when done
        """
        wwn2 = self.remove_colons(wwn)
        return wwn2[1:7]

    def ensure_unique(self, random_id) :
        """Take a random_ID and ensure that it is unique in our system.  The odds
        of a collision are pretty small, but it exists"""
        idlist = []
        for h in hostdata.keys() :
            idlist.append(self.get_id_from_wwn(hostdata[h][0]))
        if random_id in idlist :
            return False
        return True

    def gen_random_id(self, with_colons=True) :
        """Generate a random 6 digit hex id. Also runs ensure_unique on it to
           validate its unique
        """
        for i in range(3) :
            # try three times to make a random int.  If it fails after that
            # there are bigger problems
            x = random.randint(0,16777215)
            y = "%x" % x
            if self.ensure_unique(y) :
                if with_colons :
                    return self.add_colons(y)
                return y
        logging.critical("death! 3 random numbers collided with existing numbers")
        sys.exit(-1)

    def add_colons(self, charstring, addchar=':') :
        """add colons to a string such that 00112233 becomes 00:11:22:33.
           Useful to transform World Wide Names back and forth
        """
        chararray = list(charstring)
        length = len(chararray)
        if length % 2 == 0 :
            length -= 1
        for i in range(length,1,-1) :
            if i % 2 == 0 :
                chararray[i:i] = [addchar]
        return ''.join(chararray)

    def remove_colons(self, charstring, removechar=':') :
        """remove colons from a string. useful to transform World wide names
           back and forth.
        """
        return charstring.replace(removechar, '')

    def get_node_from_FQDN(self, FQDN) :
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

    def get_host_data_orig(self) :
        """reads the node_data file and fills the hostdata dictionary"""
        db = open(HOST_DEF_FILE, 'r')
        for line in db :
            uline = line.strip()
            words = uline.split()
            if line.startswith('#') :
                continue
            if len(words) == 4 :
                FQDN = words[0]
                wwnn = self.add_colons(self.remove_colons(words[1]))
                wwpna = self.add_colons(self.remove_colons(words[2]))
                wwpnb = self.add_colons(self.remove_colons(words[3]))
                hostdata[FQDN] = (wwnn, wwpna, wwpnb)

    def get_host_data(self) :
        """sees if the sqllite file exists, and is openable. if not, creates
           an empty one with the right tables.
        """
        # TODO:   %%%
        global SQLDB_FILE

    def save_new_hostinfo(self, ahost) :
        """Write out the new wwn data to the state file"""
        db = open(HOST_DEF_FILE, 'a')
        line = "	".join([ahost.FQDN, ahost.wwnn, ahost.wwpn_a, ahost.wwpn_b])
        db.write(line + '\n')
        hostdata[ahost.FQDN] = (ahost.wwnn, ahost.wwpn_a, ahost.wwpn_b)

    def create_wwns(self, node, unique_id) :
        """Generate the three wwns from FIRSTOCTETS, node, and unique_id"""
        wwnn = ':'.join([FIRSTOCTETS, node + 'f', unique_id])
        wwpna = ':'.join([FIRSTOCTETS, node + 'a', unique_id])
        wwpnb = ':'.join([FIRSTOCTETS, node + 'b', unique_id])
        return (wwnn, wwpna, wwpnb)

    def get_host(self, FQDN) :
        if FQDN in hostdata :
            return hostdef(FQDN, *hostdata[FQDN])
        else :
            return hostdef('', '', '', '')

    def get_all_hosts(self) :
        """returns all hosts"""
        results = []
        for FQDN in sorted(hostdata) :
            results.append(hostdef(FQDN, *hostdata[FQDN]))
        return results

    def create(self, FQDN) :
        """if FQDN does not exist, make one.  Returns a tuple of True/False (for
        if it was created or if it already existed) and a hostdef"""
        if FQDN in hostdata.keys() :
            # already exists.
            ahost = hostdef(FQDN, *hostdata[FQDN])
            return (False, ahost)
        node = self.get_node_from_FQDN(FQDN)
        if node == None :
            logging.critical('Cannot determine node from name %s. Exiting.' % FQDN)
            ahost = hostdef('', '', '', '')
            return (False, ahost)
        unique_id = self.gen_random_id()
        wwnn, wwpn_a, wwpn_b = self.create_wwns(node, unique_id)
        ahost = hostdef(FQDN, wwnn, wwpn_a, wwpn_b)
        self.save_new_hostinfo(ahost)
        return (True, ahost)

#    def initialize() :
#        get_host_data()
#        read_fabrics()

if __name__ == '__main__' :
    pass
