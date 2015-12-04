# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class lotho_res_partner(models.Model):
	_inherit = 'res.partner'
	
	#custom_message_ids=fields.One2many('mail.message', 'res_id', string="Reviews", readonly=True, domain=['&', ('model', '=', 'res.partner'), ('type', '=', 'comment'), ('subtype_id', '<>', False)])
	custom_message_ids=fields.One2many('mail.message', 'res_id', string="Reviews", readonly=True, domain=['&', ('model', '=', 'res.partner')])
	history_count = fields.Integer(compute='compute_vals')
		
	@api.one	
	def compute_vals(self):
		history_obj=self.env['shipments.history'].search([('partner_id', '=', self.id)])
		self.history_count=len(history_obj)
		
	def message_get_suggested_recipients(self, cr, uid, ids, context=None):
		#Grab from mail module
		#recipients = super(res_partner_mail, self).message_get_suggested_recipients(cr, uid, ids, context=context)
		#for partner in self.browse(cr, uid, ids, context=context):
		#	self._message_add_suggested_recipient(cr, uid, recipients, partner, partner=partner, reason=_('Partner Profile'))
		res=super(lotho_res_partner, self).message_get_suggested_recipients(cr, uid, ids, context=context)
		_logger.warn('MY MY message_get_suggested_recipients %s' % str(res))
		#return recipients
		return {} 