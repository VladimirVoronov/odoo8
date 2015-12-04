# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class sale_order_btc(models.Model):
	_inherit = 'sale.order'

	book_session_id = fields.Many2one('bookeo.session', string="Session")
	hotel_area_id = fields.Many2one('bookeo.area', string="Area")
	vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

	root_product = fields.Many2one('product.template', related='book_session_id.root_product', readonly=True, store=True,)
	booking_date = fields.Datetime(string="Booking Date", related='book_session_id.booking_date', readonly=True)

	bookeo_code = fields.Char(string="Bookeo ID")


	room_no = fields.Char(string="Room No")
	hotel_name = fields.Char(string="Hotel Name")
	voucher_no = fields.Char(string="Voucher No")
	remark = fields.Char(string="Remark*")
	tourists_name = fields.Char(string="Tourist's Name")

	adult = fields.Integer(string="Adult")
	child = fields.Integer(string="Child")
	infant = fields.Integer(string="Infant")

	date_start = fields.Datetime(string="Start")
	date_end = fields.Datetime(string="End")

	pickup_time = fields.Float(digits=(2, 2), string='P/U Time')


	pickup_start = fields.Float(digits=(2, 2), string='P/U Time')
	pickup_end = fields.Float(digits=(2, 2), string='P/U Time')

	ext_payment =fields.Integer(string='Ext pay')

	@api.onchange('hotel_area_id')
	def onchange_root_product(self):

		_logger.warn('onchange_root_product book_session_id%s' % str(self.book_session_id))
		_logger.warn('onchange_root_product book_session_id.route_id %s' % str(self.book_session_id.route_id))
		_logger.warn('onchange_root_product self.hotel_area %s' % str(self.hotel_area_id))

		if self.book_session_id and self.book_session_id.route_id and self.hotel_area_id:

			points_objs = self.env['fleet.route.points'].sudo().search([('route_id', '=', self.book_session_id.route_id.id),('area_id', '=',self.hotel_area_id.id)])

			if points_objs.exists():
				point=points_objs[0]

				self.pickup_start=point.pickup_start
				self.pickup_end=point.pickup_end
				self.ext_payment =point.ext_payment