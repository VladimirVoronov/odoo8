# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################
from openerp.tools.translate import _
import mandrill
import logging
_logger = logging.getLogger(__name__)

import base64

from openerp.addons.base.ir.ir_mail_server import *
from openerp import models, fields, api

def parse_mail(head_str):
	parse=head_str.split('<')
	name=parse[0]
	email=parse[1].replace('>', '')
	return name, email

def peplace_email(head_str, email):
	start=head_str.find('<')
	stop=head_str.find('>')
	bad_str=head_str[start+1:stop]
	return head_str.replace(bad_str, email)

class mandrill_message_mandrill(models.Model):
	_inherit = 'mail.message'

	mandrill_status = fields.Char(string="Mandrill status", readonly=True, copy=False)
	mandrill_id = fields.Char(string="Mandrill ID", readonly=True, copy=False)
	mandrill_reject_reason = fields.Char(string="Reject reason", readonly=True, copy=False)

	@api.one
	def action_update_track_mandrill(self):
		#Clean Attr.
	 	return True
	 	
class mandrill_mail_server(models.Model):
	_inherit = 'ir.mail_server'
	
	@api.model
	def send_mandrill(self, message):
		_logger.warn('send_mandrill message %s' % str(message.keys()))
		_logger.warn('send_mandrill get_content_maintype %s' % str(message.get_content_maintype()))
		
		mandrill_client = mandrill.Mandrill(tools.config.get('mandrill_key'))

		name, email=parse_mail(message['From'])
		name_to, email_to=parse_mail(message['To'])
		
		mess = {}
		mess['from_email']=email
		mess['from_name']=name
		#mess['headers']= {'Reply-To': message['Reply-To']}
		mess['subject']=message['Subject']
		mess['to']=[{'email':email_to, 'name':name_to, 'type':'to'}]
		
		text=None
		html=None
		
		for curr in  message.walk():
			if curr.get_content_type()=='text/plain':
				text=base64.b64decode(curr.get_payload())
				
			if curr.get_content_type()=='text/html':
				html=base64.b64decode(curr.get_payload())
								
			_logger.warn('walk text get_content_maintype %s' % str(curr.get_content_maintype()))
			_logger.warn('walk text payload %s' % str(curr.get_payload()))	

			
			_logger.warn('walk type  %s' % str(curr.get_content_type() ))
			
		mess['html']=html
		mess['text']=text	
		
		_logger.warn('send_mandrill mess  %s' % str(mess ))
		result = mandrill_client.messages.send(message=mess, async=False)[0]
		
		mess_id=message['Message-Id']
		
		message_obj=self.env['mail.message'].search([('message_id', '=', mess_id)])
		if len(message_obj)>0:
			message_obj=message_obj[0]
		else:
			_logger.warn('dont found message for update with id %s' % mess_id)	
			return mess_id
		
		message_obj.mandrill_status =result['status']
		message_obj.mandrill_id =result['_id']
		message_obj.mandrill_reject_reason = result['reject_reason']
		
		#m_obj=self.env['mail.mail'].search([('mail_message_id', '=', message_obj.id)]) 
		
		_logger.warn('send_mandrill result  %s' % str(result ))
		_logger.warn('send_mandrill Message-Id %s' % str(mess_id))
		
		return mess_id
		
	def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
				   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
				   context=None):
		
		_logger.warn('Mandriil custom was here %s' % str(message))
		
		"""Sends an email directly (no queuing).

		No retries are done, the caller should handle MailDeliveryException in order to ensure that
		the mail is never lost.

		If the mail_server_id is provided, sends using this mail server, ignoring other smtp_* arguments.
		If mail_server_id is None and smtp_server is None, use the default mail server (highest priority).
		If mail_server_id is None and smtp_server is not None, use the provided smtp_* arguments.
		If both mail_server_id and smtp_server are None, look for an 'smtp_server' value in server config,
		and fails if not found.

		:param message: the email.message.Message to send. The envelope sender will be extracted from the
						``Return-Path`` or ``From`` headers. The envelope recipients will be
						extracted from the combined list of ``To``, ``CC`` and ``BCC`` headers.
		:param mail_server_id: optional id of ir.mail_server to use for sending. overrides other smtp_* arguments.
		:param smtp_server: optional hostname of SMTP server to use
		:param smtp_encryption: optional TLS mode, one of 'none', 'starttls' or 'ssl' (see ir.mail_server fields for explanation)
		:param smtp_port: optional SMTP port, if mail_server_id is not passed
		:param smtp_user: optional SMTP user, if mail_server_id is not passed
		:param smtp_password: optional SMTP password to use, if mail_server_id is not passed
		:param smtp_debug: optional SMTP debug flag, if mail_server_id is not passed
		:return: the Message-ID of the message that was just sent, if successfully sent, otherwise raises
				 MailDeliveryException and logs root cause.
		"""
		smtp_from = message['Return-Path'] or message['From']
		assert smtp_from, "The Return-Path or From header is required for any outbound email"

		# The email's "Envelope From" (Return-Path), and all recipient addresses must only contain ASCII characters.
		from_rfc2822 = extract_rfc2822_addresses(smtp_from)
		assert from_rfc2822, ("Malformed 'Return-Path' or 'From' address: %r - "
							  "It should contain one valid plain ASCII email") % smtp_from
		# use last extracted email, to support rarities like 'Support@MyComp <support@mycompany.com>'
		smtp_from = from_rfc2822[-1]
		email_to = message['To']
		email_cc = message['Cc']
		email_bcc = message['Bcc']
		
		smtp_to_list = filter(None, tools.flatten(map(extract_rfc2822_addresses,[email_to, email_cc, email_bcc])))
		assert smtp_to_list, self.NO_VALID_RECIPIENT

		x_forge_to = message['X-Forge-To']
		if x_forge_to:
			# `To:` header forged, e.g. for posting on mail.groups, to avoid confusion
			del message['X-Forge-To']
			del message['To'] # avoid multiple To: headers!
			message['To'] = x_forge_to

		# Do not actually send emails in testing mode!
		if getattr(threading.currentThread(), 'testing', False):
			_test_logger.info("skip sending email in test mode")
			return message['Message-Id']

		# Get SMTP Server Details from Mail Server
		mail_server = None
		if mail_server_id:
			mail_server = self.browse(cr, SUPERUSER_ID, mail_server_id)
		elif not smtp_server:
			mail_server_ids = self.search(cr, SUPERUSER_ID, [], order='sequence', limit=1)
			if mail_server_ids:
				mail_server = self.browse(cr, SUPERUSER_ID, mail_server_ids[0])

		if mail_server:
			smtp_server = mail_server.smtp_host
			smtp_user = mail_server.smtp_user
			smtp_password = mail_server.smtp_pass
			smtp_port = mail_server.smtp_port
			smtp_encryption = mail_server.smtp_encryption
			smtp_debug = smtp_debug or mail_server.smtp_debug
		else:
			# we were passed an explicit smtp_server or nothing at all
			smtp_server = smtp_server or tools.config.get('smtp_server')
			smtp_port = tools.config.get('smtp_port', 25) if smtp_port is None else smtp_port
			smtp_user = smtp_user or tools.config.get('smtp_user')
			smtp_password = smtp_password or tools.config.get('smtp_password')
			if smtp_encryption is None and tools.config.get('smtp_ssl'):
				smtp_encryption = 'starttls' # STARTTLS is the new meaning of the smtp_ssl flag as of v7.0

		if not smtp_server:
			raise osv.except_osv(
						 _("Missing SMTP Server"),
						 _("Please define at least one SMTP server, or provide the SMTP parameters explicitly."))

		message_id = message['Message-Id']
		# Hook 1
		if smtp_server=='mandrill':
			if tools.config.get('mandrill_key', False):
				return self.send_mandrill(cr, SUPERUSER_ID, message)
			else:
				_logger.warn('You set SMTP server as mandrill but not sent mandril API key in Odoo config file. Use standart Odoo core folow. Please set param mandrill_key in config file')
		# Hook 1
		
		# Hook 2
		if smtp_server=='smtp.mandrillapp.com':
			user_obj=self.pool['res.users'].browse(cr, SUPERUSER_ID, uid)
			normal_from=peplace_email(message['From'], user_obj.login)
			
			del message['From']
			del message['Reply-To']
			
			message['From']=normal_from
			message['Reply-To']=normal_from
			
			_logger.warn('smtp.mandrillapp.com message %s' % str(message))
		# Hook 2		
		try:
			
			# Add email in Maildir if smtp_server contains maildir.
			if smtp_server.startswith('maildir:/'):
				from mailbox import Maildir
				maildir_path = smtp_server[8:]
				mdir = Maildir(maildir_path, factory=None, create = True)
				mdir.add(message.as_string(True))
				return message_id

			smtp = None
			try:
				smtp = self.connect(smtp_server, smtp_port, smtp_user, smtp_password, smtp_encryption or False, smtp_debug)
				rez=smtp.sendmail(smtp_from, smtp_to_list, message.as_string())
				_logger.warn('SMTP send Res %s' % str(rez))
			finally:
				if smtp is not None:
					smtp.quit()
		except Exception, e:
			msg = _("Mail delivery failed via SMTP server '%s'.\n%s: %s") % (tools.ustr(smtp_server),
																			 e.__class__.__name__,
																			 tools.ustr(e))
			_logger.error(msg)
			raise MailDeliveryException(_("Mail Delivery Failed"), msg)
		return message_id