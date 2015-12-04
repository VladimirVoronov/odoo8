# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class product_template_tour(models.Model):													
	_inherit = 'product.template'

	bookeo_code = fields.Char()
	route_id = fields.Many2one('fleet.route', string="Route")





