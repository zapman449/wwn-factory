#!/usr/bin/python

import logging
import bottle
import wwn_factory
import fqdn_validator

@bottle.route('/')
def slash() :
    # hooray this works now! Curl doesn't follow though... use a real browser
    logging.info('hi there')
    bottle.redirect('/listall', 303)

@bottle.route('/listall')
@bottle.route('/listall/')
def listall() :
    global options
    logging.info('welcome')
    hosts = SanData.get_all_hosts()
    return bottle.template('make_table', rows=hosts)

@bottle.get('/list/:FQDN')
def list_FQDN(FQDN) :
    host = SanData.get_host(FQDN)
    if host.FQDN == '' :
        return "<p> host %s not found." % FQDN
    return bottle.template('make_table', rows=[host])

@bottle.route('/wwn_fabric/<FQDN>/<switchwwn>')
def wwn_fabric(FQDN, switchwwn) :
    logging.info(repr(FQDN))
    logging.info(repr(switchwwn))
    host = SanData.get_host(FQDN)
    fabric = SanData.get_fabric_from_switchwwn(switchwwn)
    if fabric == None :
        return "fabric not found"
    if host.FQDN == '' :
        return "host not found"
    if fabric in ('a', 'b') :
        short_node = SanData.remove_colons(host.wwnn)
        if fabric == 'a' :
            short_port = SanData.remove_colons(host.wwpn_a)
        elif fabric == 'b' :
            short_port = SanData.remove_colons(host.wwpn_b)
        cmd = ':'.join((short_port, short_node))
        return cmd
    logging.info("-- %s -- %s --" % (host.FQDN, fabric))
    return 'fabric out of bounds'

@bottle.get('/json/:FQDN')
def json_FQDN(FQDN) :
    host = SanData.get_host(FQDN)
    if host.FQDN == '' :
        return "host %s not found." % FQDN
    result = {}
    result['FQDN'] = host.FQDN
    result['wwnn'] = host.wwnn
    result['wwpn_a'] = host.wwpn_a
    result['wwpn_b'] = host.wwpn_b
    #return json.dumps(result)
    return result

@bottle.get('/create/:FQDN')
def create_FQDN(FQDN) :
    if fqdn_validator.validate_FQDN(FQDN) :
        success, host = SanData.create(FQDN)
        if success :
            return bottle.template('make_table', rows=[host])
        else :
            if host.FQDN == '' :
                return 'creation failed'
            else :
                result = "<p>Host already existed.<p>"
                result += bottle.template('make_table', rows=[host])
                return result
    else :
        return 'invalid FQDN'

@bottle.error(403)
def mistake403(code):
    return 'There is a mistake in your url!'

@bottle.error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'

if __name__ == '__main__' :
    logging.basicConfig(level=logging.DEBUG)
    logging.info('starting for jason')
    #wwn_factory.initialize()
    SanData = wwn_factory.SanData()
    # TODO: disable for production:
    bottle.debug(True)
    bottle.run(host='127.0.0.1', port=8080)
    logging.info('stopping for jason')
