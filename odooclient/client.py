#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from . import connection

FORMAT = "%(asctime)-15s - %(url)s - %(user)s :: "
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)

_logger = logging.getLogger("OdooClient ")


class OdooClient(object):
    """
    >>> from odooclient import client
    >>> client.OdooClient(protocol='xmlrpc', host='firebug.odoo.com',  port=443, dbname='firebug', saas=True)


    """
    def __init__(self, protocol='xmlrpc', host='localhost', port=8069, dbname=None, saas=False, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        if saas:
            protocol, port = 'xmlrpcs', 443

        self._served_protocols = {'xmlrpc': 'http', 'xmlrpcs': 'https'}

        self._protocol = self.__GetProtocol(protocol)
        self._host = host
        self._port = port
        self._db = dbname

        self._login = False
        self._password = False
        self._uid = False

        self._serverinfo = {}

        self._url = "{protocol}://{host}:{port}".format(protocol=self._protocol,
                                             host=self._host, port=self._port,)
        _logger.debug('Url -> {url}'.format(url=self._url))

    def __str__(self):
        return "<Object ServerProxy-{url}>".format(url=self._url)

    def __GetProtocol(self, protocol):
        if protocol not in self._served_protocols:
            raise NotImplementedError("The protocol '{0}' is not supported by the\
                         OdooClient. Please choose a protocol among these ones: {1}\
                        ".format(protocol, self._served_protocols))
        return self._served_protocols.get(protocol)

    def ServerInfo(self):
        """
        Code :
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            common.version()
        """
        cn = connection.Connection(self._url)
        self._serverinfo = cn.GetServerInfo()
        return self._serverinfo

    def IsAuthenticated(self):
        cn = all([self._uid, self._login, self._password]) and True or False
        return cn

    def Authenticate(self, login, pwd):
        """
        Code :
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
        """
        self._login, self._password = login, pwd
        service = connection.Connection(self._url)
        self._uid = service.Authenticate(self._db, login, pwd, {})
        return self._uid

    def CheckSecurity(self, model, operation_modes=['read']):
        """
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        models.execute_kw(db, uid, password,
                                        'res.partner', 'check_access_rights',
                                        ['read'], {'raise_exception': False})
        """
        service = connection.Connection(self._url)
        results = dict.fromkeys(operation_modes, False)
        for mode in operation_modes:
            response = service.Model(self._db, self._uid, self._password, model, \
                        'check_access_rights', mode, raise_exception=False)
            results.update({mode: response})
        return results

    def Read(self, model, document_ids, fields=False, context=None):
        """
        models.execute_kw(db, uid, password,
                    'res.partner', 'read',
                    [ids], {'fields': ['name', 'country_id', 'comment']})
        """
        if not context:
            context = {}
        if type(document_ids) not in (int, long, list, tuple):
            msg = "Invalid ids `type` {ids}. Ids should be on type `int`, \
                                    `long`, `list` or 'tuple'.".format(ids=ids)
            return (False, msg)
        service = connection.Connection(self._url)
        response = service.Model(self._db, self._uid, self._password, model, 'read', document_ids, {'fields': fields, 'context':context})
        return response

    def Search(self, model, domain=False, context=None,**kwargs):
        """
        search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False)

        models.execute_kw(db, uid, password,
            'res.partner', 'search',
            [[['is_company', '=', True], ['customer', '=', True]]],
            {'offset': 10, 'limit': 5})

        """
        if not context:
            context = {}
        if not kwargs:
            kwargs ={}
        kwargs.update({'context': context})
        service = connection.Connection(self._url)
        response = service.Model(self._db, self._uid, self._password, model, 
                                        'search', domain or [], **kwargs)
        return response

    def SearchCount(self, model, domain=False, context=None):
        """
        search_count(self, cr, user, args, context=None):

        models.execute_kw(db, uid, password,
            'res.partner', 'search_count',
            [[['is_company', '=', True], ['customer', '=', True]]])

        """
        if not context:
            context = {}
        service = connection.Connection(self._url)
        response = service.Model(self._db, self._uid, self._password, model, 
                                        'search_count', domain or [], context=context)
        return response

    def SearchRead(self, model, domain=False, fields=False, context=None, **kwargs):
        """
        search_read(self, cr, uid, domain=None, fields=None, offset=0, 
                        limit=None, order=None, context=None):

        models.execute_kw(db, uid, password,
            'res.partner', 'search_read',
            [[['is_company', '=', True], ['customer', '=', True]]],
            {'fields': ['name', 'country_id', 'comment'], 'limit': 5})

        """
        if not context:
            context = {}
        if not kwargs:
            kwargs ={}
        kwargs.update({'context': context})

        service = connection.Connection(self._url)
        response = service.Model(self._db, self._uid, self._password, model, 
                                        'search_read', domain or [],
                                        fields=fields, **kwargs)
        return response


    def Create(self, model, values, context=None):
        """
        create(self, vals):

        id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
            'name': "New Partner",
        }])

        """
        if not context: context = {}
        service = connection.Connection(self._url)
        response = service.Model(self._db, self._uid, self._password, model, 
                                            'create', values, context=context)
        return response

    def Write(self, model, document_ids, values, context=None):
        """
        write(self, vals):

        models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], {
            'name': "Newer partner"
        }])
        """
        if not context: context = {}
        service = connection.Connection(self._url)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'write', document_ids, values, context=context)
        return response


    def GetFields(self, model, context=None, attributes=None):
        """
        fields_get(self, cr, user, allfields=None, context=None,
                                    write_access=True, attributes=None)
        models.execute_kw(
            db, uid, password, 'res.partner', 'fields_get',
            [], {'attributes': ['string', 'help', 'type']})
        """
        if not context: context = {}
        if not attributes: attributes = []

        service = connection.Connection(self._url)
        response = service.Model(self._db, self._uid, self._password, model, 
                        'fields_get', context=context, attributes=attributes)
        return response
