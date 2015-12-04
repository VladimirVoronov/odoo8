# -*- coding: utf-8 -*-

{
    'name': 'Lotho',
    'version': '3',
    'summary': 'Lotho customization',
	'depends': ['base', 'mail', 'sale', 'base_setup'],
	 'external_dependencies': {'python': ['mandrill']},
	'license': 'Other proprietary',
	'sequence': 1000,
    'description': 	"""
     http://zzblalvla.myodoo:9080/
     #http://www.royalmail.com/portal/rm/track?trackNumber=ZW924750388GB
     
     #On future disable Odoo links uncheck  Activate the customer portal  here http://screencloud.net/v/nR67
	- 
	sudo pip install mandrill
	""",
    'author': 'MyOdoo',
    'installable': True,
	'data': [
		'shipment_view.xml',
        'res_partner.xml',
        'mail_view.xml',
        'sale_view.xml',
        'mandrill_view.xml',
        'user_data.xml',
        'res_config.xml'
    ],
}

