# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class product_template_tour(models.Model):													
	_inherit = 'product.template'

	max= fields.Integer(string="Max")
	gross_price = fields.Float(string="Gross Price")
	vat_code = fields.Char(string="VAT Code")

	vat_code_purch = fields.Char(string="VAT Code for Purchases")
	ppb= fields.Integer(string="PPB")

	a_c = fields.Float(string="Accumulated Depreciation")

	vat_gency = fields.Char(string="VAT Agency")

	aiv = fields.Boolean(string="Amounts Include VAT", default=False)
	pur_ro_res = fields.Boolean(string="Purchased for Resale", default=False)



