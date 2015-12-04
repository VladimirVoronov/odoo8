# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class product_partner_btc(models.Model):
	_inherit = 'res.partner'

	bookeo_code = fields.Char()