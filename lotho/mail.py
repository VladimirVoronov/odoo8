# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

import base64

from openerp.addons.base.ir.ir_mail_server import *
from openerp import models, fields, api

class lotho_mail_notification(models.Model):
	_inherit = 'mail.notification'
	
	@api.model
	def get_signature_footer(self, user_id, res_model=None, res_id=None, context=None, user_signature=True):
		return  ""
	
class lotho_mail_mail(models.Model):
	_inherit = 'mail.message'
	
	@api.one
	def resend_mail(self):
		mail_objs=self.env['mail.mail'].sudo().search([('mail_message_id', '=', self.id)])
		
		if len(mail_objs)==0:
			
			create_vals={}
			create_vals['body_html']=self.body
			create_vals['mail_message_id']=self.id
			create_vals['notification']=True
			create_vals['auto_delete']=True
			create_vals['state']='exception'
			
			mail_obj=self.env['mail.mail'].sudo().create(create_vals)
			
			_logger.warn('create new %s' % str(mail_obj) )
		else:	
			mail_obj=mail_objs[0]
			
		res=mail_obj.send(raise_exception=True)
		_logger.warn('resend_mail %s' % str(res) )
	 	return True