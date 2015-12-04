# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

import os
import suds

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

from rm_lib import get_my_client

import logging
_logger = logging.getLogger(__name__)

class lotho_sale_order(models.Model):
	_name = 'sale.order'
	#inherit ='sale.order' 
	_inherit = ['sale.order', 'shipments']
