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
from openerp import tools
from openerp import SUPERUSER_ID


class thai_pos_category_commision(models.Model):
	_name = 'pos.category.commission'

	category_id = fields.Many2one('pos.category', required=True)

	commissioner_id = fields.Many2one('res.partner', string="Commisioner", required=True,
	                                  domain="[ ('is_company','=', True)]")

	commission_company = fields.Integer(string='Commission company %', required=True)


class thai_pos_category(models.Model):
	_inherit = 'pos.category'

	commission_ids = fields.One2many('pos.category.commission', 'category_id', string="Commission")
	guide_sale_commission = fields.Integer(string='Commission Sales Guide %', required=True)

class thai_pos_lines(models.Model):
	_inherit = 'pos.order.line'

	# discount = fields.Integer( string='Discount %', store=True, readonly=True, related='order_id.discount')

	leader_commision = fields.Float(digits=(7, 2), string='Leader commision', readonly=True)
	company_commision = fields.Float(digits=(7, 2), string='Company commision', readonly=True)
	net_total = fields.Float(digits=(7, 2), string='Net total', readonly=True)
	guide_sale_commission = fields.Float(digits=(7, 2), string='guide_sale_commission', readonly=True)
	#bus_session_id = fields.Many2one('pos.order.session', string="Bus session", store=True, readonly=True,
	 #                                related='order_id.bus_session_id')

	n_max = fields.Integer(string="N pax", related='order_id.bus_session_id.n_max', store=True)

class thai_pos(models.Model):
	_inherit = 'pos.order'

	bus_session_id = fields.Many2one('pos.order.session', string="Bus session")

	discount = fields.Integer(string='Discount %', states={'paid': [('readonly', True)]})

	#leader_id = fields.Many2one('res.partner', string="Leader", store=True, readonly=True,)
	                            #related='bus_session_id.leader_id')
	#driver_id = fields.Many2one('res.partner', string="Driver", store=True, readonly=True,)
	                            #related='bus_session_id.driver_id')
	guide_sale_id = fields.Many2one('res.partner', string="Sales Guide", store=True, readonly=True,)
	                             #   related='bus_session_id.guide_sale_id')
	ref_company_id = fields.Many2one('res.partner', string="Referal company", store=True, readonly=True,  related='partner_id.parent_id')
	#n_max = fields.Integer(string="N pax", store=True, readonly=True, related='bus_session_id.n_max')

	leader_commision = fields.Float(digits=(7, 2), string='Leader commision', readonly=True, compute='compute_vals2')
	company_commision = fields.Float(digits=(7, 2), string='Company commision', readonly=True, compute='compute_vals2')
	net_total = fields.Float(digits=(7, 2), string='Net total', readonly=True, compute='compute_vals2')
	guide_sale_commission = fields.Float(digits=(7, 2), string='Guide sale comm', readonly=True,
	                                     compute='compute_vals2')

	@api.one
	def compute_vals2(self):

		leader_commision = 0.00
		company_commision = 0.00
		net_total = 0.00
		guide_sale_commission = 0.00

		for curr in self.lines:
			leader_commision += curr.leader_commision
			company_commision += curr.company_commision
			net_total += curr.net_total
			guide_sale_commission += curr.guide_sale_commission

		self.leader_commision = leader_commision
		self.company_commision = company_commision
		self.net_total = net_total
		self.guide_sale_commission = guide_sale_commission

	@api.one
	def button_calc_comm(self):
		self.calc_commision(self.id)

	@api.one
	def calc_commision(self, id):
		order_obj = self.env['pos.order'].sudo().browse(id)
		rounding=2

		#Set session
		if not order_obj.bus_session_id:
			order_obj.bus_session_id= self.env['pos.order.session'].get_buss_ssesion(self.partner_id)

		if self.partner_id and self.partner_id.parent_id:
			self.ref_company_id=self.partner_id.parent_id.id

		for cc in order_obj.lines:

			base_total =cc.price_subtotal_incl
			_logger.warn('base_total %s' % str(base_total))

			## Calc saleman commision
			if cc.product_id.pos_categ_id:
				cc.guide_sale_commission = round(base_total / 100 * cc.product_id.pos_categ_id.guide_sale_commission, rounding)

			#Calc leader commision
			if self.ref_company_id:
				if cc.product_id.pos_categ_id:
					cc.leader_commision = round(base_total / 100 * self.ref_company_id.commission_leader, rounding)
					_logger.warn('pos_categ_id %s' % str(cc.product_id.pos_categ_id))

			if self.ref_company_id and cc.product_id.pos_categ_id:
				#Calc company commision
				domain=[('commissioner_id', '=',self.ref_company_id.id), ('category_id', '=', cc.product_id.pos_categ_id.id)]
				commis_objs = self.env['pos.category.commission'].sudo().search(domain)

				if commis_objs:
					cc.company_commision = round(base_total / 100 * commis_objs[0].commission_company, rounding)
				else:
					_logger.warn('dont find pos.category.commission for ref_company_id.id %s' % str(self.ref_company_id.id))

			cc.net_total = base_total - cc.company_commision - cc.leader_commision - cc.guide_sale_commission

	def create_from_ui(self, cr, uid, orders, context=None):
		# Keep only new orders
		submitted_references = [o['data']['name'] for o in orders]
		existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
		existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
		existing_references = set([o['pos_reference'] for o in existing_orders])
		orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]

		order_ids = []

		for tmp_order in orders_to_save:
			to_invoice = tmp_order['to_invoice']
			order = tmp_order['data']

			_logger.warn('create_from_ui order vals %s' % str(order))

			order_id = self._process_order(cr, uid, order, context=context)
			####
			self.calc_commision(cr, uid, order_id, order_id)
			####
			order_ids.append(order_id)

			try:
				self.signal_workflow(cr, uid, [order_id], 'paid')

			except Exception as e:
				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

			if to_invoice:
				self.action_invoice(cr, uid, [order_id], context)
				order_obj = self.browse(cr, uid, order_id, context)
				self.pool['account.invoice'].signal_workflow(cr, uid, [order_obj.invoice_id.id], 'invoice_open')

		return order_ids
