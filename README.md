#**Odoo Client Library**
--

Very SIMPLE and STUPID Pythonic Odoo Client Library to make-use-of Odoo WebServices. It is designed to wrap all XML RPC Technicality into more object-orientated meaning of programming using class and dedicated Methods.

##__Features:__
- Basic-Generic **ORM API** (create, read, write, unlink ...) CRUD.
- Generic **ORM Research API** (search, search_read, search_count, name_search ...).
- Generic superset **Method** to avoid implmentation (symmetric code but need to be attentive).
- Easy **SaaS/HTTPS or Local Instance/Database** Connection styles.


--


##Usage:

- Add api directory `odooclient` to project.
- Import `from odooclient import client`.

##Below are examples of `odoo-client-api` usage : 

-

##Saas Test
```python
from odooclient import client

odoo = client.OdooClient( host='demo.odoo.com', dbname='firebug', saas=True, debug=True)
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
```

-

##SaaS Security Test
```python
from odooclient import client

odoo = client.OdooClient( host='demo.odoo.com', dbname='firebug', saas=True, debug=True)
odoo.Authenticate('a@b.com', 'a')
odoo.CheckSecurity('res.users', ['create'])
odoo.CheckSecurity('res.partner')
```

-

##Local Test
```python
from odooclient import client

odoo = client.OdooClient(protocol='xmlrpc', host='localhost', dbname='test', port=8069, debug=True)
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
odoo.Read('res.partner', [1, 2], fields=['name'])
rid = odoo.Create('res.partner', {'name': "Odoo"})
odoo.SearchCount('res.partner')
odoo.Write('res.partner', [rid], {'name': 'Odoo'})
odoo.Search('res.partner', [('name', 'like', 'Odoo')], order='id desc')
odoo.SearchRead('res.partner', [('name', 'like', 'Odoo')], ['name'])
odoo.GetFields('res.partner')
odoo.Copy('res.partner', record_id,{'name': "jigar"})
odoo.NameCreate('res.partner',"jigar")
allids = [o[0] for o in odoo.NameSearch("res.partner", "jigar")]
odoo.Unlink("res.partner", allids)
```

-

##Local Security Test
```python
from odooclient import client

odoo = client.OdooClient(protocol='xmlrpc', host='localhost', dbname='test', port=8069, debug=True)
odoo.Authenticate('demo', 'demo')
odoo.CheckSecurity('res.users', ['create'])
odoo.CheckSecurity('res.partner' )
```

###Generic method `Method`

-

For More Control Over API , Generic `Method` is also implemented, where you can call any method from API, but you have to care full in passing Params :

Method  `create` with odoo-client-lib API  look like :
```
    odoo.Create('res.partner', {'name': "Odoo"})
```
But this can be also called using Generic method `Method`which look like:
```
   odoo.Method('res.partner', 'create', {'name': "Odoo"})
```
This sounds more Raw and generic but doesn't make difference in this case as create being generic ORM method, but any method implementation specific to Model can be called using `Method`, this enable Extended API feature.


Note: This is Still development copy not finalized.

##P.S. :

Feature to be Added are : 

- Wrokflow methods
- Report Priting API
- Tools lib.
 - CSV reader
 - Server Friendly Text Sanitizer
- A Fork with ODBC Features.
