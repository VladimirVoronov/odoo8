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

class stock_location2(models.Model):
	#TODO
	#_name = 'purchase.order.line'
	_inherit = 'purchase.order.line'
		
	qty_available = fields.Float(string="Quantity On Hand", related='product_id.qty_available')
	virtual_available = fields.Float(string="Forecasted Quantity", related='product_id.virtual_available')
	incoming_qty = fields.Float(string="Incoming", related='product_id.incoming_qty')
	outgoing_qty = fields.Float(string="Outgoing", related='product_id.outgoing_qty')
	
	inventory_by_locations=fields.Many2many('stock.quant', compute='compute_total')
	mo_line_by_product1=fields.Many2many('mrp.production.product.line', compute='compute_total')
	
	def compute_stock(self):
		cr, uid=self.env.cr, self.env.user
		
	def compute_total(self):
		mbl_arr=[]
		
		ibl=self.env['stock.quant'].sudo().search(([('product_id', '=', self.product_id.id)]))
		mol=self.env['mrp.production.product.line'].sudo().search([('product_id', '=', self.product_id.id)])
		
		_logger.info('mol %s' % str(mol))
		_logger.warn('procc path %s' % str(mol))
		for curr in mol:
			mo_state=curr.production_id.state
			_logger.info('mo_state %s' % str(mo_state))
			if mo_state!='cancel' and mo_state!='done' and mo_state is not None:
				mbl_arr.append(curr)
																	
		self.inventory_by_locations=ibl
		self.mo_line_by_product1=mbl_arr