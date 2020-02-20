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
    def __init__(self, protocol='xmlrpc', host='localhost', port=8069, version=2, dbname=None, saas=False, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        if saas:
            protocol, port = 'xmlrpcs', 443

        self._served_protocols = {'xmlrpc': 'http', 'xmlrpcs': 'https'}

        self._protocol = self.__GetProtocol(protocol)
        self._host = host
        self._port = port
        self._db = dbname
        self._version = version

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
        cn = connection.Connection(self._url, version=self._version)
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
        service = connection.Connection(self._url, version=self._version)
        self._uid = service.Authenticate(self._db, login, pwd, {})
        return self._uid

    def Login(self, login, pwd):
        """
        Code :
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
        """
        self._login, self._password = login, pwd
        service = connection.Connection(self._url, version=self._version)
        self._uid = service.Login(self._db, login, pwd)
        return self._uid



    def CheckSecurity(self, model, operation_modes=['read']):
        """
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        models.execute_kw(db, uid, password,
                                        'res.partner', 'check_access_rights',
                                        ['read'], {'raise_exception': False})
        """
        service = connection.Connection(self._url, version=self._version)
        results = dict.fromkeys(operation_modes, False)
        for mode in operation_modes:
            response = service.Model(self._db, self._uid, self._password, model, \
                        'check_access_rights', mode, raise_exception=False)
            results.update({mode: response})
        return results

    def Method(self, model, method, *args, **kwrags):
        """
        Generic Method Call if you don't find specific implementation.
		
        models.execute_kw(db, uid, password,
            '<any model>', '<any method>', args1, args1, ..., argsN
            {'kwy': ['val1', 'val2', 'valn'], 'key2': val2})
        """
        if not kwrags: kwrags = {}
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                        method, *args, **kwrags)
        return response 

    def Read(self, model, document_ids, fields=False, context=None):
        """
        models.execute_kw(db, uid, password,
                    'res.partner', 'read',
                    [ids], {'fields': ['name', 'country_id', 'comment']})
        """
        if not context:
            context = {}
        if type(document_ids) not in (int, complex, list, tuple):
            msg = "Invalid ids `type` {ids}. Ids should be on type `int`, \
                                    `long`, `list` or 'tuple'.".format(ids=ids)
            return (False, msg)
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 'read', document_ids, fields=fields, context=context)
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
        service = connection.Connection(self._url, version=self._version)
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
        service = connection.Connection(self._url, version=self._version)
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

        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                        'search_read', domain or [],
                                        fields=fields, **kwargs)
        return response

    def NameSearch(self, model, name, domain=False, context=None,**kwargs):
        """
        name_search(name='', domain=None, operator='ilike', limit=100)

        models.execute_kw(db, uid, password,
            'res.partner', 'name_search',<name_to_search>
            [[['is_company', '=', True], ['customer', '=', True]]],
            {'offset': 10, 'limit': 5})

        """
        if not context:
            context = {}
        if not kwargs:
            kwargs ={}
        kwargs.update({'context': context})
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                        'name_search', name, domain or [], **kwargs)
        return response

    def Create(self, model, values, context=None):
        """
        create(self, vals):

        id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
            'name': "New Partner",
        }])

        """
        if not context: context = {}
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                            'create', values, context=context)
        return response

    def NameCreate(self, model, name, context=None):
        """
        name_create(name, context)

        models.execute_kw(db, uid, password,
            'res.partner', 'name_create',<name_to_search>
            [[['is_company', '=', True], ['customer', '=', True]]],
            {'offset': 10, 'limit': 5})

        """
        if not context:
            context = {}
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                        'name_create', name, context=context)
        return response

    def Write(self, model, document_ids, values, context=None):
        """
        write(self, vals):

        models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], {
            'name': "Newer partner"
        }])
        """
        if not context: context = {}
        service = connection.Connection(self._url, version=self._version)
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

        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                        'fields_get', context=context, attributes=attributes)
        return response

    def Unlink(self, model, document_ids, context=None):
        """

        models.execute_kw(db, uid, password, 
                          'res.partner', 'unlink', [[id]])
        """
        if not context: context = {}
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'unlink', document_ids, context=context)
        return response

    def Copy(self, model, document_ids, default=None, context=None):
        """
        copy(default=None)
        models.execute_kw(db, uid, password, 
                          'res.partner', 'copy', [id], {'field1': "default values"})
        """
        if not context: context = {}
        if not default: default = {}
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'copy', document_ids, default=default, context=context)
        return response

    def CreateWorkflow(self, model, document_ids, context=None):
        """
        def create_workflow(self, cr, uid, ids, context=None):
            Create a workflow instance for each given record IDs    
        """
        if not context: context = {}
        if type(document_ids) not in (int, long, list, tuple):
            raise Exception("Document Ids expected to be in int, long list or tuple format.")
        if type(document_ids) in (int, long):
            document_ids = [document_ids]
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'create_workflow', document_ids, context=context)
        return response

    def UnlinkWorkflow(self, model, document_ids, context=None):
        """
        def delete_workflow(self, cr, uid, ids, context=None):
        Delete the workflow instances bound to the given record IDs.
        """
        if not context: context = {}
        if type(document_ids) not in (int, long, list, tuple):
            raise Exception("Document Ids expected to be in int, long list or tuple format.")
        if type(document_ids) in (int, long):
            document_ids = [document_ids]
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'delete_workflow', document_ids, context=context)
        return response

    def StepWorkflow(self, model, document_ids, context=None):
        """
        def step_workflow(self, cr, uid, ids, context=None):
        Reevaluate the workflow instances of the given record IDs.

        """
        if not context: context = {}
        if type(document_ids) not in (int, long, list, tuple):
            raise Exception("Document Ids expected to be in int, long list or tuple format.")
        if type(document_ids) in (int, long):
            document_ids = [document_ids]
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'step_workflow', document_ids, context=context)
        return response

    def SignalWorkflow(self, model, document_ids, signal, context=None):
        """
        def signal_workflow(self, cr, uid, ids, signal, context=None):
        Send given workflow signal and return a dict mapping ids to workflow results
        """
        if not context: context = {}
        if type(document_ids) not in (int, long, list, tuple):
            raise Exception("Document Ids expected to be in int, long list or tuple format.")
        if type(document_ids) in (int, long):
            document_ids = [document_ids]
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'signal_workflow', document_ids, signal,context=context)
        return response

    def RedirectWorkflow(self, model, old_new_ids, context=None):
        """
        def redirect_workflow(self, cr, uid, old_new_ids, context=None):
        Rebind the workflow instance bound to the given 'old' record IDs to
            the given 'new' IDs. (``old_new_ids`` is a list of pairs ``(old, new)``.
        """
        if not context: context = {}
        if type(old_new_ids) not in (list, tuple):
            raise Exception("Document Ids expected to be in  list/tuple of tuples [(1,2)] format.")
        service = connection.Connection(self._url, version=self._version)
        response = service.Model(self._db, self._uid, self._password, model, 
                                'redirect_workflow', old_new_ids, context=context)
        return response

    def PrintReport(self, report_service, record_ids, context=None):
        """
        invoice_ids = models.execute_kw(
            db, uid, password, 'account.invoice', 'search',
            [[('type', '=', 'out_invoice'), ('state', '=', 'open')]])
        report = xmlrpclib.ServerProxy('{}/xmlrpc/2/report'.format(url))
        result = report.render_report(
            db, uid, password, 'account.report_invoice', invoice_ids)
        report_data = result['result'].decode('base64')

        """
        if not context: context = {}
        service = connection.Connection(self._url, version=self._version)
        response = service.Report(self._db, self._uid, self._password, report_service, 
                                            record_ids, context=context)
        return response