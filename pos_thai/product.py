# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class product_template_pos(models.Model):
	_inherit = 'res.partner'