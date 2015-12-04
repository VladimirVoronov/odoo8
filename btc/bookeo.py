# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

import logging

_logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from openerp import models, fields, api
from bookeo_api import get_bookeo_vals

import logging

_logger = logging.getLogger(__name__)

from bookeo_api import get_bookeo_vals
from datetime import datetime, timedelta

from openerp import models, fields, api


class tour_area(models.Model):
	_name = "fleet.route.points"

	route_id = fields.Many2one('fleet.route', string="Area")

	name = fields.Char(string='Name')

	area_id = fields.Many2one('bookeo.area', string="Area")
	pickup_start = fields.Float(digits=(2, 2), string='Pickup start')
	pickup_end = fields.Float(digits=(2, 2), string='Pickup end')

	ext_payment =fields.Integer(string='Ext pay')

class tour_area(models.Model):
	_name = "fleet.route"

	pickuptime_ids = fields.One2many('fleet.route.points', 'route_id', string="Pickup times")

	name = fields.Char(string='Name')

	start = fields.Float(digits=(2, 2), string='Time start')
	end = fields.Float(digits=(2, 2), string='Time end')


class tour_session(models.Model):
	_name = "bookeo.session"

	name = fields.Char(string='Session name', compute='_compute_display_name')
	bookeo_code = fields.Char( required=True, default='007')

	route_id = fields.Many2one('fleet.route', string="Route")

	root_product = fields.Many2one('product.template', required=True)
	booking_date = fields.Datetime(string="Booking Date", required=True)

	booking_ids = fields.One2many('sale.order', 'book_session_id', string="Bookings")
	vehicle_ids = fields.One2many('fleet.vehicle', False, string="Vehicle", compute='_compute_display_name')

	#display_name = fields.Char(compute='_compute_display_name', inverse='_inverse_display_name')

	seats_total= fields.Integer(string="Total seats", compute='compute_vals')
	seats_set= fields.Integer(string="Total seats set", compute='compute_vals')
	seats_unset= fields.Integer(string="Total seats unset", compute='compute_vals')

	@api.onchange('root_product', 'booking_ids.vehicle_id')
	def onchange_root_product(self):
		if self.root_product and self.root_product.route_id:
			self.route_id=self.root_product.route_id

	@api.model
	def _default_route(self):
		user_obj=self.env['res.users'].browse(self.env.user)
		if len(user_obj.company_id.bank_ids)>0:
			return user_obj.company_id.bank_ids[0]
		else:
			return False

	@api.one
	def compute_vals(self):
		seats_set= 0
		seats_unset= 0

		for curr in self.booking_ids:
			if curr.vehicle_id:
				seats_set+=curr.adult
				seats_set+=curr.child

			else:
				seats_unset+=curr.adult
				seats_unset+=curr.child

		self.seats_total= seats_set+seats_unset
		self.seats_set= seats_set
		self.seats_unset= seats_unset

		self.vehicle_ids=[1]

	@api.depends('root_product', 'booking_date')
	def _compute_display_name(self):

		for record in self:
			if record.booking_date and record.root_product:
				self_in_tz = self.with_context(tz=('Etc/GMT-7'))

				ddt=fields.Datetime.from_string(record.booking_date)

				record.name = record.root_product.name + ' ' + fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, ddt))

class tour_area(models.Model):
	_name = "bookeo.area"

	name = fields.Char(string='Name')

class bookeo_import(models.TransientModel):
	_name = "bookeo.import"

	@api.one
	def action_update_products(self):
		product_pool = self.env['product.template']

		res = get_bookeo_vals('settings/products')
		for curr in res:
			product_objs = product_pool.sudo().search([('bookeo_code', '=', curr['productId'])])

			if not product_objs.exists():
				create_vals = {

					'bookeo_code': curr['productId'],
					'name': curr['name'],
					'default_code': curr['productCode'],

				}
				new_product = product_pool.sudo().create(create_vals)

				attr_age = self.env.ref('btc.tour_product_attribute1')

				attr_val_price_adult = self.env.ref('btc.tour_product_age_adult')
				attr_val_price_child4 = self.env.ref('btc.tour_product_age_child4')
				attr_val_price_child0 = self.env.ref('btc.tour_product_age_child0')

				ids = [attr_val_price_adult.id, attr_val_price_child4.id, attr_val_price_child0.id]
				# Create product.attribute.line
				attr_vals = {'product_tmpl_id': new_product.id,
							 'attribute_id': attr_age.id,
							 'value_ids': [(6, 0, ids)],
							 }
				att_age_obj = new_product.attribute_line_ids.create(attr_vals)

				new_product.create_variant_ids()

		return True

	def action_get_customer_id(self, code):
		_logger.warn(' action_get_customer_id %s' % str(code))

		partner_pool = self.env['res.partner']

		partner_objs = partner_pool.sudo().search([('bookeo_code', '=', code)])

		if not partner_pool.exists():
			curr = get_bookeo_vals('customers/%s' % code)

			_logger.warn('curr %s' % str(curr))

			create_vals = {

				'bookeo_code': code,
				'name': curr['firstName'],
				'email': curr['emailAddress'],

			}

			if curr.has_key('lastName'):
				create_vals['name'] = create_vals['name'] + ' ' + curr['lastName']

			for cc in curr['phoneNumbers']:

				if cc['type'] == 'mobile':
					create_vals['mobile'] = cc['number']

				if cc['type'] == 'home':
					create_vals['phone'] = cc['number']


			new_partner = partner_pool.sudo().create(create_vals)

			return new_partner.id

		else:
			return partner_objs[0].id

	def get_session_id(self, curr):
		_logger.warn('get_session_id curr[eventId] %s' % str(curr['eventId']))

		ss_pool = self.env['bookeo.session']

		ss_objs = ss_pool.sudo().search([('bookeo_code', '=', curr['eventId'])])

		if not ss_objs.exists():

			product = self.env['product.template'].sudo().search([('bookeo_code', '=', curr['productId'])])[0]

			booking_date = curr['eventId'][-10:]

			self_in_tz = self.with_context(tz=('Etc/GMT+7'))
			ddt=fields.Datetime.from_string(booking_date)

			create_vals = {
				'route_id': product.route_id.id,
				'bookeo_code': curr['eventId'],
				'root_product': product.id,
				'booking_date': fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, ddt)),

			}

			_logger.warn('get_session_id create create_vals %s' % str(create_vals))
			new_sess = ss_pool.create(create_vals)

			return new_sess.id

		else:
			return ss_objs[0].id

	def get_area_id(self, area):

		area_pool = self.env['bookeo.area']

		area_objs = area_pool.sudo().search([('name', '=', area)])

		if not area_objs.exists():

			create_vals = {

				'name': area,

			}
			new_area = area_objs.create(create_vals)
			return new_area.id

		else:
			return area_objs[0].id

	@api.one
	def procc_booking(self, res):
		so_pool = self.env['sale.order']

		for curr in res:
			so_objs = so_pool.sudo().search([('bookeo_code', '=', curr['bookingNumber'])])

			_logger.warn('product search %s' % str(curr['productId']))

			if not so_objs.exists():

				create_vals = {

					'partner_id': self.action_get_customer_id(curr['customerId']),
					'bookeo_code': curr['bookingNumber'],
					'book_session_id': self.get_session_id(curr),

				}

				for opt in curr['options']:
					field_name = opt['name'].lower().replace(' ', '_').replace('*', '').replace("'", '')
					create_vals[field_name] = opt['value']

				area_name=create_vals['hotel_area']
				st=area_name.find('(')
				if st>0:
					area_name=area_name[:st]
					area_name=area_name.strip()

				create_vals['hotel_area_id']=self.get_area_id(area_name)

				for pp in curr['participants']['numbers']:

					if pp['peopleCategoryId']=='Cadults':
						create_vals['adult']= pp['number']

					if pp['peopleCategoryId']=='Cchildren':
						create_vals['child']= pp['number']

					if pp['peopleCategoryId']=='Cinfant':
						create_vals['infant']= pp['number']

				_logger.warn('procc_booking %s' % str(create_vals))

				so_pool.sudo().create(create_vals)

			else:
				pass

			# print
			# print curr['productId']
			# print curr['customerId']

			# print curr

	@api.one
	def action_import(self):
		# self.action_update_products()
		#

		mask = '%Y-%m-%dT%H:%M:%S+00:00'
		days_diff = 27

		now = datetime.now()
		endTime = now.strftime(mask)
		startTime = (now - timedelta(days=days_diff)).strftime(mask)

		vals = {'startTime': startTime, 'endTime': endTime}

		res = get_bookeo_vals('bookings', vals)

		self.procc_booking(res)

		return True
