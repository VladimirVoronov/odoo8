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
import pdb
#import np_stock
#import stock
#import mrp

#import stock_location

from openerp import tools
from openerp.osv import osv
from openerp.osv import fields 
import logging



_logger = logging.getLogger(__name__)
# Scheduled Products

class mrp_production_product_line(osv.osv):
	_inherit = 'mrp.production.product.line'
	_name = 'mrp.production.product.line'

	def _get_field_from_production_obj(self, cr, uid, ids, name, arg, context=None):
		#pdb.set_trace()
		res={}
		for id in ids:
			production_obj=self.browse(cr,uid,id).production_id
			res[id]=""
			if production_obj.id:
				if name=='mo_product':
					res[id]= self.browse(cr,uid,id).production_id[arg].name
				else:
					res[id]= self.browse(cr,uid,id).production_id[arg]
		#pdb.set_trace()
		return res

	_columns = {
		'mo_name': fields.function(_get_field_from_production_obj,arg='name',type='char', string='MO name'),
		'mo_product': fields.function(_get_field_from_production_obj,arg='product_id',type='char', string='Product'),
		'mo_status': fields.function(_get_field_from_production_obj,arg='state',type='char', string='State'),
	}

mrp_production_product_line()
