# -*- coding: utf-8 -*-

{
	'name': 'food',
	'version': '1',

	'license': 'Other proprietary',

	'summary': 'Custom for food mail',
	'depends': ['stock', 'mrp', 'purchase', 'point_of_sale', 'product_brand', 'mail'],
	'description': """
	- customize
		http://food1.myodoo:9080/report/html/food.thai_invoice/1
	""",
	'author': 'myodoo',

	'qweb': [
		#'qweb.xml',
	],

	'installable': True,
	'data': [
		'product_view.xml',
		'sale_view.xml',
		'res_partner.xml',
		'user_data.xml',
		'smtp_per_user_view.xml',

	],
}
