# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)


from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class product_template_tour(models.Model):													
	_inherit = 'product.product'

	avg_purchase_price = fields.Float(digits=dp.get_precision('Product Price'), string='Avg purchase',  readonly=True, compute='compute_vals')

	@api.one
	def compute_vals(self):
		product_lines=self.env['purchase.order.line'].sudo().search([('product_id','=', self.id)])

		total=0.00
		items_count=len(product_lines)

		for curr in product_lines:
			total+=curr.price_unit

		if total>0 and items_count>0:
			val=total/items_count
		else:
			val=0.00

		rd=self.env['decimal.precision'].precision_get('Product Price')

		self.avg_purchase_price=round(val, rd)

class product_template_tour(models.Model):
	_inherit = 'product.template'

	avg_purchase_price = fields.Float(digits=dp.get_precision('Product Price'), string='Avg purchase',  readonly=True, compute='compute_vals')

	@api.one
	def compute_vals(self):

		total=0.000

		items_count=len(self.product_variant_ids)

		for curr in self.product_variant_ids:
			total+=curr.avg_purchase_price

		if items_count>0:

			rd=self.env['decimal.precision'].precision_get('Product Price')
			self.avg_purchase_price=round(total/items_count, rd)

		else:
			self.avg_purchase_price=0.000



