# -*- coding: utf-8 -*-

{
	'name': 'btc',
	'version': '1',

	'license': 'Other proprietary',

	'summary': 'Custom for Best Travel Club',
	'depends': ['base', 'sale', 'product', 'fleet'],
	#'depends': ['stock', 'mrp', 'purchase', 'point_of_sale', 'product_brand'],tenerikia
	'description': """
	- customize

	""",
	'author': 'myodoo',
	'installable': True,
	'data': [
		'sale_view.xml',
		'bookeo_view.xml',
		'product_view.xml',
		'user_data.xml',

	],
}
