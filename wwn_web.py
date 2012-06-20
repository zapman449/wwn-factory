#!/usr/bin/python

import logging
import bottle
import wwn_factory

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
    hosts = wwn_factory.get_all_hosts()
    return bottle.template('make_table', rows=hosts)

@bottle.get('/list/:FQDN')
def list_FQDN(FQDN) :
    host = wwn_factory.get_host(FQDN)
    if host.FQDN == '' :
        return "<p> host %s not found." % FQDN
    return bottle.template('make_table', rows=[host])

@bottle.get('/json/:FQDN')
def json_FQDN(FQDN) :
    host = wwn_factory.get_host(FQDN)
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
    if wwn_factory.validate_FQDN(FQDN) :
        success, host = wwn_factory.create(FQDN)
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
    wwn_factory.initialize()
    # TODO: disable for production:
    bottle.debug(True)
    bottle.run(host='127.0.0.1', port=8080)
    logging.info('stopping for jason')
