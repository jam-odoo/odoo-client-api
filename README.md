Odoo Client Library
--
Yet Another SLibrary Nothing Fancy here This is very SIMPLE and STUPID, Pything based Odoo Client Library make use of Odoo WebServices. It is designed to wrap all XML RPC Technicality into more object-orientated meaning of programming using class and dedicated Methods.

Usage Example.

Add api directory `odooclient` in our project and import and it ready to user, below is simple example of usage.


from odooclient import client

print "="*100
#Saas Test
odoo = client.OdooClient( host='demo.odoo.com', dbname='firebug', saas=True, debug=True)
print odoo
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
odoo.Read('res.partner', [1, 2], fields=['name'])
odoo.Search('res.partner')
odoo.SearchCount('res.partner')
odoo.SearchRead('res.partner', [], ['name'])
odoo.GetFields('res.partner')

#Lcoal Security Test
odoo.Authenticate('a@b.com', 'a')
odoo.CheckSecurity('res.users', ['create'])
odoo.CheckSecurity('res.partner')

#Local Test
odoo = client.OdooClient(protocol='xmlrpc', host='localhost', dbname='test', port=8069, debug=True)
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
odoo.Read('res.partner', [1, 2], fields=['name'])
rid = odoo.Create('res.partner', {'name': "Odoo"})
odoo.SearchCount('res.partner')
odoo.Write('res.partner', [rid], {'name': 'Odoo'})
odoo.Search('res.partner', [('name', 'like', 'Odoo')], order='id desc')
odoo.SearchRead('res.partner', [('name', 'like', 'Odoo')], ['name'])
#Local Security Test
odoo.Authenticate('demo', 'demo')
odoo.CheckSecurity('res.users', ['create'])
odoo.CheckSecurity('res.partner' )


Note: This is Still development copy not finalized.