# -*- coding: utf-8 -*-

import pprint

from odooclient import client
from odooclient import tools

pp = pprint.PrettyPrinter(indent=4)

#Saas Test
odoo = client.OdooClient( host='test.odoo.com', dbname='firebug', saas=True, debug=True)
print odoo
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
odoo.Read('res.partner', [1, 2], fields=['name'])
odoo.Search('res.partner')
odoo.SearchCount('res.partner')
odoo.SearchRead('res.partner', [], ['name'])
odoo.GetFields('res.partner')

#Security Test
odoo.Authenticate('a@b.com', 'a')
odoo.CheckSecurity('res.users', ['create'])
odoo.CheckSecurity('res.partner')


#Local Ruuning Odoo Connection
odoo = client.OdooClient(protocol='xmlrpc', host='localhost', dbname='test', port=8069, debug=True)
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
odoo.Read('res.partner', [1, 2], fields=['name'])
record_id = odoo.Create('res.partner', {'name': 'Dummy'})
odoo.SearchCount('res.partner')
odoo.Write('res.partner', [record_id], {'name': 'Dummy Persion'})
odoo.Search('res.partner', [('name', 'like', 'Dummy')], order='id desc')
odoo.SearchRead('res.partner', [('name', 'like', 'Dummy')], ['name'])
odoo.GetFields('res.partner')
odoo.Copy('res.partner', record_id,{'name': 'Dummy'})
odoo.NameCreate('res.partner','Dummy')
allids = [o[0] for o in odoo.NameSearch('res.partner', 'Dummy')]
odoo.Unlink('res.partner', allids)


#Workflow methods works for v9 or earlier vrsion only
odoo.UnlinkWorkflow('account.invoice', 1)
odoo.CreateWorkflow('account.invoice', 1)
odoo.StepWorkflow('account.invoice', 1)
odoo.SignalWorkflow('account.invoice', 1, 'invoice_open')
odoo.RedirectWorkflow('account.invoice', [(1,2)])

#Reading a CSV files:
data_lines = tools.read_csv_data('./tests/csv/partners.csv')
pp.pprint(data_lines)