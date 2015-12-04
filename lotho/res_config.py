# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class rm_base_config_settings(models.Model):
	
	_inherit = 'base.config.settings'
	
	rm_app_id = fields.Char(string="RM App ID")

	rm_key = fields.Binary(string="RM key")
	rm_cert= fields.Binary(string="RM cert")
	
	rm_login = fields.Char(string="RM Login")
	rm_pass = fields.Char(string="RM Passwird")
