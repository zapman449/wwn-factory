wwn-factory
===========

If you have an NPIV environment, you need to manage your world wide numbers. This is a 
tool to help.

Currently split into 3 pieces:

1) wwn_factory.py
This is the backend functionality for these tools.  Basically, it's the API.

2) wwn_cli.py
This is the front end CLI functionality.

3) wwn_web.py
This is a web frontend.  Uses Bottle.  Provides text listing of information, and has the
ability to return a hosts information in json format.
