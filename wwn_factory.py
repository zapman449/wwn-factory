#!/usr/bin/python

"""a program to generate (or return) 1 WWNN and 2 WWPN's for a given vhost."""

import collections
import logging
import random
import sqlite3
import sys

SQLDB_FILE = 'san.db'

FIRSTOCTETS = "5f:0a:22:50"
# 5 + f:0a:22:5 + 0
# see http://howto.techworld.com/storage/156/how-to-interpret-worldwide-names/
# for details.  f0a225 is a private OUI according to:
# http://standards.ieee.org/develop/regauth/oui/oui.txt
# 5 indicates type 5, the trailing 0 is for padding.

hostdef = collections.namedtuple('hostdef', 'FQDN wwnn wwpn_a wwpn_b')

class SanData(object) :
    def __init__(self) :
        self.connection = None
        self.cursor = None
        self.init_db()

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
        print 'create DbVersion'
        self.cursor.execute("CREATE TABLE DbVersion(Version INT)")
        self.cursor.execute("INSERT INTO DbVersion(Version) VALUES (1);")
        print 'create Fabrics'
        self.cursor.execute("CREATE TABLE Fabrics(SwitchWWN CHAR(23) UNIQUE NOT NULL ON CONFLICT ROLLBACK, Description CHAR(25), Fabric CHAR(1))")
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
        print 'create HostInfo'
        self.cursor.execute("CREATE TABLE HostInfo(FQDN CHAR(100) UNIQUE NOT NULL ON CONFLICT ROLLBACK, WWNN CHAR(23) UNIQUE NOT NULL ON CONFLICT ROLLBACK, WWPNA CHAR(23) UNIQUE NOT NULL ON CONFLICT ROLLBACK, WWPNB CHAR(23) UNIQUE NOT NULL ON CONFLICT ROLLBACK)")
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

    def get_fabric_from_switchwwn(self, switchwwn) :
        logging.info(repr(switchwwn))
        if switchwwn.startswith('0x') :
            switchwwn = switchwwn[2:]
        if not self.has_colons(switchwwn) :
            switchwwn = self.add_colons(switchwwn)
        self.cursor.execute('SELECT Fabric FROM Fabrics WHERE SwitchWWN = ?',
                                (switchwwn,) )
        row = self.cursor.fetchone()
        if row == None :
            logging.error("SwitchWWN %s not found in DB.  New switch?" % switchwwn)
            return None
        else :
            return row[0]

    def get_wwns_from_fabric(self, switchwwn, FQDN) :
        fabric = self.get_fabric_from_switchwwn(switchwwn)
        if fabric == None :
            return None, None
        ahost = self.get_host(FQDN)
        if ahost.wwnn == '' :
            logging.error("FQDN %s not found in DB." % FQDN)
            return None, None
        if fabric == 'a' :
            return ahost.wwpn_a, ahost.wwnn
        elif fabric == 'b' :
            return ahost.wwpn_b, ahost.wwnn
        else :
            logging.error("Really should not happen (in get_wwns_from_fabric)")
            return None, None

    def get_id_from_wwn(self, wwn) :
        """Take a wwn, and split out the unique id from it.  The unique ID
           will not have colons in it when done
        """
        wwn2 = self.remove_colons(wwn)
        return wwn2[1:7]

    def ensure_unique(self, random_id) :
        """Take a random_ID and ensure that it is unique in our system.  The 
           odds of a collision are pretty small, but it exists"""
        self.cursor.execute('select WWNN from HostInfo')
        idlist = map(self.get_id_from_wwn(self.cursor.fetchall()))
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

    def has_colons(self, charstring, checkchar=':') :
        """Sees if there are colons in the right spots"""
        for i in range(2,23,3) :
            if charstring[i] != checkchar :
                return False
        return True

    def save_new_hostinfo(self, ahost) :
        """Write out the new wwn data to the state file"""
        self.cursor.execute("INSERT INTO HostInfo VALUES (?, ?, ?, ?);",
                              (ahost.FQDN, ahost.wwnn, 
                               ahost.wwpn_a, ahost.wwpn_b) )
        self.connection.commit()

    def create_wwns(self, node, unique_id) :
        """Generate the three wwns from FIRSTOCTETS, node, and unique_id"""
        wwnn = ':'.join([FIRSTOCTETS, node + 'f', unique_id])
        wwpna = ':'.join([FIRSTOCTETS, node + 'a', unique_id])
        wwpnb = ':'.join([FIRSTOCTETS, node + 'b', unique_id])
        return (wwnn, wwpna, wwpnb)

    def get_host(self, FQDN) :
        self.cursor.execute("SELECT wwnn, wwpna, wwpnb FROM HostInfo where FQDN = ?", (FQDN,))
        row = self.cursor.fetchone()
        if row == None :
            return hostdef('', '', '', '')
        else :
            return hostdef(FQDN, row[0], row[1], row[2])

    def get_all_hosts(self) :
        """returns all hosts"""
        self.cursor.execute('select * from HostInfo ORDER BY FQDN')
        results = []
        for row in self.cursor.fetchall() :
            results.append(hostdef(*row))
        return results

    def create(self, FQDN) :
        """if FQDN does not exist, make one.  Returns a tuple of True/False (for
        if it was created or if it already existed) and a hostdef"""
        self.cursor.execute('select * from HostInfo where FQDN = ?', (FQDN,))
        row = self.cursor.fetchone()
        if FQDN == row[0] :
            # already exists
            ahost = hostdef(*row)
            return (False, ahost)
        node = self.get_node_from_FQDN(FQDN)
        if node == None :
            logging.warning('Cannot determine node from name %s. Exiting.' % FQDN)
            ahost = hostdef('', '', '', '')
            return (False, ahost)
        unique_id = self.gen_random_id()
        wwnn, wwpn_a, wwpn_b = self.create_wwns(node, unique_id)
        ahost = hostdef(FQDN, wwnn, wwpn_a, wwpn_b)
        self.save_new_hostinfo(ahost)
        return (True, ahost)

    def delete(self, FQDN) :
        """If FQDN exists, delete it."""
        self.cursor.execute('select * from HostInfo where FQDN = ?', (FQDN,))
        row = self.cursor.fetchone()
        if FQDN == row[0] :
            # already exists
            self.cursor.execute('delete from HostInfo where FQDN = ?', (FQDN,))
            self.connection.commit()
            return True
        return False

if __name__ == '__main__' :
    pass
