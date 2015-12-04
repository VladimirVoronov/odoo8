# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

{
	'name': 'Thai pos',
	'version': '14',
	'category': 'Point Of Sale',
	'sequence': 6,
	'summary': 'Thai Touchscreen Interface for market',
	'license': 'Other proprietary',
	'description': """
    Download and uncompress in /path/to/your/python/site-packages/reportlab/fonts these file

    http://www.reportlab.com/ftp/fonts/pfbfer.zip

    Companies / Your Company ->Change paper format

	disable stock_account
	disble accounts in product
	default product type =stokable


	POS=>Payment Methods=>Cash registers=Cash Control V


    """,
	'author': 'myodoo',
	'depends': ['point_of_sale', 'purchase', 'product_ext_price'],
	'data': [
		'view.xml',
		'pos_template.xml',
		'template.xml',
		'report.xml',
		'res_partner_view.xml',
		'purchase_view.xml',
		'bus_session_view.xml',

		#'security/security.xml',
        'security/ir.model.access.csv',
		'user_data.xml',

	],

	'qweb': [

		'qweb.xml',
	],

	'installable': True,
	'application': True,

	'auto_install': False,
}
