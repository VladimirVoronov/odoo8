# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class sale_order_line(models.Model):

	_inherit = 'sale.order.line'

	@api.one
	def compute_fields(self):
		first_index=self.order_id.order_line[0].id
		try:
			self.serial_index=self.id-first_index+1
		except:
			pass	

	serial_index=fields.Integer(string="№п.п.", compute='compute_fields')


class sale_order_line(models.Model):

	_inherit = 'sale.order'

	company_id = fields.Many2one('res.company', string="Company", readonly=False)
	last_pay_date = fields.Date(compute='compute_fields')


	@api.one
	def compute_fields(self):
		for curr in self.invoice_ids:
			for cc in curr.payment_ids:
				self.last_pay_date=cc.date


