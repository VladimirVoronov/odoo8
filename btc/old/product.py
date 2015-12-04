# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime

from openerp import tools
from openerp.osv import osv, fields

class product_product(osv.osv):
	_inherit = 'product.product'
	_name = "product.product"
	
	#We are replace date_done to date in model stock.inventory
	def get_last_inventory_date(self, cr, uid, ids, name, arg, context=None):
		#pdb.set_trace()
		res={}
		for id in ids:
			inv_line_obj = self.pool.get('stock.inventory.line')
			inv_lines=inv_line_obj.search(cr, uid, [('product_id', '=', id)])
			
			inv_date=datetime(1900,1,1)
			inv_date_str=""
			for inv_line in inv_lines:
				inv_obj=self.pool.get('stock.inventory').browse(cr,uid,inv_line_obj.browse(cr,uid,inv_line).inventory_id.id)
				if inv_obj.date:
					date_done=datetime.strptime(inv_obj.date, '%Y-%m-%d %H:%M:%S')
					if inv_date<date_done:
						inv_date=date_done
						inv_date_str=inv_obj.date
			
			res[id]=inv_date_str
		return res
	
	def _get_inventory_by_locations(self, cr, uid, ids, name, arg, context=None):
#		pdb.set_trace() 
		res={}
		location_obj = self.pool.get('stock.location')
		res[ids[0]] = location_obj.search(cr, uid, [('usage', '=', 'internal')], context=context)
		return res
		
	_columns = {
		'last_inventory_date': fields.function(get_last_inventory_date, type='date', string='Last inventory date'),
		'inventory_by_locations': fields.function(_get_inventory_by_locations, type='one2many',relation='stock.location', string='Inventory by locations'),
	}
 

product_product()
