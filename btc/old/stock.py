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

class stock_inventory_line(models.Model):
	
	_inherit = 'stock.inventory.line'
	
	#Old calc for field np_stock_real
	def _get_real_qnt_in_location():
		#pdb.set_trace()
		res={}
		for id in ids:
			inv_line_obj=self.browse(cr,uid,id)
			inventory_state=inv_line_obj.inventory_id.state
			res[id]='-'
			if inventory_state=='draft' or inventory_state=='confirm':
				obj_product=inv_line_obj.product_id
				amount = self.pool.get('stock.location')._product_get(cr, uid, inv_line_obj.location_id.id, [obj_product.id], {'uom': obj_product.uom_id.id, 'to_date': False,'compute_child': False})[obj_product.id]
				res[id]=amount
		return res
		
	def _compute(self):
		cr, uid=self.env.cr, self.env.user
		self.np_stock_real='-'


	
	np_stock_real =  fields.Char(string="Real in location", compute='_compute')
	# return fixed location stock/office !!!!
	location_id =  fields.Many2one('stock.location', string="Location", compute='_compute', required=True, default=19)
	
class stock_locationz(models.Model):

	_inherit = 'stock.location'
		
	def compute_stock(self):
		cr, uid=self.env.cr, self.env.user
		
		#product_pool=self.pool.get('product.product')
		#prd=product_pool._product_available(cr, uid, product_ids, context=ctx)
		
		
		#ctx['location_id'] = loc_ids
		#prods = registry['product.product']._product_available(cr, uid, product_ids, context=ctx)
		#for prod in prods.keys():
		#	products[prod] = [(now, prods[prod]['qty_available'])]
		#	prods[prod] = 0

		self.stock_real=44.44
		self.stock_virtual=555.33

	#stock_real =  fields.Folat(string="Real Stock", compute='compute_stock')
	#stock_virtual =  fields.Folat(string="Virtual Stock", compute='compute_stock')
	stock_real = fields.Float()
	stock_virtual = fields.Float()
