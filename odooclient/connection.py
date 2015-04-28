#!/usr/bin/python
# -*- coding: utf-8 -*-

import pprint
import logging
import xmlrpclib


_logger = logging.getLogger("OdooClient ")


class ServiceManager(object):
    """
    Class Will service Odoo service proxy:
    @param url      : Database Connection URL
    @param service  : Name of the service called
    @param version  : Odoo WebService Version No default(2)

    """

    def __str__(self):
        return "<Object XMLRPC-ConnectionManger>"

    def __init__(self, url, service, version=2):

        if service not in ('common', 'object', 'report', 'db'):
            raise NotImplementedError("Unknown Service {service}.".format(service=service))
        self._service = service
        self._version = version
        self._url = url
        self._proxy = xmlrpclib.ServerProxy("{url}/xmlrpc/{version}/{service}".format(url=self._url, version=self._version, service=self._service))

    def Trasmit(self, method, *args, **kwargs):
        try:
            response = getattr(self._proxy, method)(*args)
            _logger.debug("RPC Response of Method `%s` -> %s"%(method, response))
            return response
        except xmlrpclib.ProtocolError as err:
            _logger.debug("A protocol error occurred: \n - URL :{url}\n - Error Code : {code}\n - Error message: {msg}".format(url=err.url, code=err.errcode, msg=err.errmsg))
            raise err
        except Exception, er:
            _logger.debug("Unexpected Error : \n{e}".format(e=er))
            raise er

class Connection(object):
    """

    @param url      : Database Connection URL
    @param service  : Name of the service called
    @param version  : Odoo Web Service Version No default(2)

    """
    def __init__(self, url, service='common', version=2):

        if service not in ('common', 'object', 'report', 'db'):
            raise NotImplementedError("Unknown Service {service}.".format(service=service))
        self._service = service
        self._version = version
        self._url = url
        self._serverinfo = {}

    def __str__(self):
        return "<Object Connection-{url}>".format(url=self._url)

    def GetServerInfo(self):
        self._serverinfo = ServiceManager(self._url,'common').Trasmit('version')
        return self._serverinfo

    def Authenticate(self, db, user, password, session={}):
        try:
            response = ServiceManager(self._url,'common').Trasmit('authenticate', db, user, password, session)
            if response:
                _logger.debug("Successful Authentication of `{user}` Using Database `{db}`.".format(user=user, db=db))
            else:
                _logger.debug("Unsuccessful Authentication Attempt of `{user}` Using Database `{db}`.".format(user=user, db=db))
            return response
        except Exception, e:
            print "Authenticate Exception :\n  %s \n"%(e)
            pass

    def Model(self, db, uid, password, model, method, *args, **kwrags):
        try:
            response = ServiceManager(self._url,'object').Trasmit('execute_kw', db, uid, password, model, method, args, kwrags)
            return response
        except Exception, e:
            print "Unknown Exception :\n  %s \n"%(e)
            pass

