wwn-factory
===========

If you have an NPIV environment, you need to manage your world wide numbers.
This is a tool to help.

Currently split into 3 pieces:

1) wwn_factory.py
This is the backend functionality for these tools.  Basically, it's the API.

2) wwn_cli.py
This is the front end CLI functionality.

3) wwn_web.py
This is a web frontend.  Uses Bottle.  Provides text listing of information, and has the
ability to return a hosts information in json format.


USAGE guide:

This will need to be customized for any environment that wants to use it.  As I
go through, I'll try to keep a close eye on that, and try to minimize those
changes.  Currently, there are two changes you'll need to make:
a) you need to hack all of fqdn_validator.py.  This code tries to ensure that 
clients are asking for 'proper' hosts.  This code is NOT secure against 
internet attacks.  The concept if a 'node' is important for my environment 
but not for yours.  You could think of a 'node' as a group of fabrics, say 
an A and B fabric for one physical location.  The easiest thing to do would be
rename 'simple_validate' to 'falidate_FQDN' and be done with it, though 
that test is a little... naive.
b) You'll need to remove/modify the 'make_tables' function in wwn_factory.  
This bootstraps the DB to have a bit of data in it, and all the right tables.

To actually use this code, you can use either the CLI command:
./wwn_cli.py -h            Print this help messages
./wwn_cli.py FQDN          Print existing WWNN and WWPN or error out
./wwn_cli.py create FQDN   Print existing WWNN and WWPN, or create new and print
./wwn_cli.py destroy FQDN  Destroys a host from the database

or you can use the web front end, which relies on bottle:

Run with 'wwn_web.py'.

http://localhost:8080/

	redirects to listall

http://localhost:8080/listall

	HTML table with all hosts and wwns listed

http://localhost:8080/list/<FQDN>

	HTML table FQDN's information listed

http://localhost:8080/json/<FQDN>

	json data for FQDN's wwns

http://localhost:8080/create/<FQDN>

	Creates and lists wwns for FQDN.

http://localhost:8080/wwn_fabric/{FQDN}/{switchwwn}

	This is different from the above.  This is used by wwn_remote.py.
	This is based on a given host not needing to have a list of all
	possible FQDN/WWNN/WWPN sets.  It can just ask a central web source
	(via a variablized URL at the top) about what FQDN it wants, and what
	switchWWN (seen in /sys/class/fc_host/host*/fabric_name on linux) it
	is connected to, and be done.  Basically, it needs one piece of info:
	the wwn_remote script with the right URL defined in it.

wwn_remote.py <create|delete> FQDN
	This does NOT create or delete from the DB.  This follows the names
	of /sys/class/fc_host/host*/vport_[create|delete].  This script will
	generate the appropriate commands to create or destroy the
	virtualHBA for that given guest FQDN.
	TODO: code some magic to determine fabric_a or fabric_b into this 
	to simplify live_migration.  This isn't a priority, since Linux KVM
	can't do NPIV Live Migration currently anyway.

wwn_factory.py:
	This is the backend API for everything.

----------

This code has no warranty.  If it causes your computer to fall over, and 
break your toe, I can not be held responsible.  Code is provided AS IS in 
the hopes that it could be useful.
