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
from openerp.addons.product.product import ean_checksum


class pos_partner(models.Model):

	_inherit = 'purchase.order'

	@api.one
	def my_action_confirm(self):

		self.signal_workflow('purchase_confirm')

		for curr in self.picking_ids:
			wizard=self.env['stock.transfer_details'].create({'picking_id':curr.id})
			wizard.do_detailed_transfer()

	 	return True