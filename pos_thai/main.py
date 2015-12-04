# -*- coding: utf-8 -*-
import base64

import werkzeug
import werkzeug.urls

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.http import Response

import logging
_logger = logging.getLogger(__name__)

class thai_pos(http.Controller):

	def get_draft_pos_order(self, pos_id):
		pos_obj=request.env['pos.config'].sudo().browse(pos_id)
		customer_obj=request.env['pos.session'].sudo().search([('config_id', '=', pos_obj.id), ('state', '=', 'opened')])

		#order_obj=request.env['pos.order'].sudo().search([('user_id', '=', barcode)])


	@http.route(['/thai_pos/'], type='http', auth="public", website=False)
	def thai_pos(self, barcode='', **pos):

		_logger.debug('thai POS barcode=%s' % str(barcode))
		_logger.debug('thai POS kwargs=%s' % str(pos))

		if len(barcode)<3:
			return '-4'

		pos_id=False
		code_prefix='pos_'

		for curr in pos:
			if curr.startswith(code_prefix):
				pos_id=curr.replace(code_prefix,'')
				pos_id=int(pos_id)

		if not pos_id:
			_logger.debug('Thai POS error don\'t found POS with ID' )
			return '-5'

		if barcode[0:3]=='042':
			customer_obj=request.env['res.partner'].sudo().search([('ean13', '=', barcode)])
			if len(customer_obj)==0:
				_logger.debug('Thai POS error don\'t found customer with code=%s' % str(barcode))
				return '-3'
		else:
			product_obj=request.env['product.template'].sudo().search([('ean13', '=', barcode)])
			if len(product_obj)==0:
				_logger.debug('Thai POS error don\'t found product with code=%s' % str(barcode))
				return '-2'
