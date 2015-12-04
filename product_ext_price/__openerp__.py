# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################


{
	'name': 'product_ext_price',
	'version': '0.1',
	'summary': 'Pricelist based on Avg Purchase price',
	'depends': ['product'],

	'description': """
		Pricelist based on Avg Purchase price
	""",
	'license': 'Other proprietary',
	'price': 1.00,
	'currency': 'EUR',
	 'website': 'https://www.upwork.com/o/profiles/users/_~01a4a3d604f8c454ec/',


	'author': 'Vladimir Voronov',
	'installable': True,
	'data': [
		'product_view.xml',
		'user_data.xml',
	],
}
