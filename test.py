from odooclient import client

print "="*100
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

#Local Test
odoo = client.OdooClient(protocol='xmlrpc', host='localhost', dbname='test', port=8069, debug=True)
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
odoo.Read('res.partner', [1, 2], fields=['name'])
record_id = odoo.Create('res.partner', {'name': "jigar"})
odoo.SearchCount('res.partner')
odoo.Write('res.partner', [record_id], {'name': 'jigar amin'})
odoo.Search('res.partner', [('name', 'like', 'jigar')], order='id desc')
odoo.SearchRead('res.partner', [('name', 'like', 'jigar')], ['name'])
odoo.GetFields('res.partner')
odoo.Copy('res.partner', record_id,{'name': "jigar"})
odoo.NameCreate('res.partner',"jigar")
allids = [o[0] for o in odoo.NameSearch("res.partner", "jigar")]
odoo.Unlink("res.partner", allids)

#Security Test
odoo.Authenticate('demo', 'demo')
odoo.CheckSecurity('res.users', ['create'])
odoo.CheckSecurity('res.partner' )