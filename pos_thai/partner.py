# -*- encoding: utf-8 -*-

##############################################################################
#
#  Autor Dementiev Sergey
#  sde@arterp.ru
#  www.arterp.ru
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api
from openerp.addons.product.product import ean_checksum


class pos_partner(models.Model):

	_inherit = 'res.partner'

	pos_disc= fields.Integer(string="POS discount %",  attrs="{'invisible': [('is_company', '=', False)]}")
	sys_pos_disc= fields.Integer(compute='compute_vals2', readonly=True)

	commission_leader = fields.Integer(string='Commission guide %', attrs="{'invisible': [('is_company', '=', False)]}")
	#commission_leader2 =fields.Float(digits=(2, 1), string='Commission company %', required=True)


	@api.one
	def compute_vals2(self):
		if self.parent_id:
			self.sys_pos_disc=self.parent_id.pos_disc


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		if name:
			# Be sure name_search is symetric to name_get
			#name = name.split(' / ')[-1]
			args = [('ean13', '=', name)] + args
		customers = self.search(args, limit=limit)
		#0420100200009
		return customers.name_get()