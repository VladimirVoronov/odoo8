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

class pos_pcs_deposit_master(models.TransientModel):

	_name = "pos.deposit_master"

	name = fields.Many2one('res.partner', string="Partner", required=True)
	partner_balance = fields.Float(digits=(7, 2), string='Partner balance',  readonly=True, related='name.partner_balance')
	partner_deposit = fields.Float(digits=(7, 2), string='Deposit')
	partner_balance_after = fields.Float(digits=(7, 2), string='Balance after Deposit',  readonly=True)

	@api.onchange('partner_deposit')
	def change_cash(self):

		if self.partner_deposit>0:
			self.partner_balance_after=self.partner_balance+self.partner_deposit
		else:
			self.partner_balance_after=0.00

	@api.one
	def create_from_vals_and_next(self, summ):
		create_vals={
			'name':self.name.id,
			'partner_deposit': summ,

		}
		new_record=self.env['pos.partner_deposits'].create(create_vals)

		return {
			'type': 'ir.actions.act_window',
			'res_model': 'pos.deposit_master',
			'view_mode': 'form',
		}

	@api.multi
	def create_and_next(self):
		cccc=self.create_from_vals_and_next(self.partner_deposit)

		return {
			'type': 'ir.actions.act_window',
			'res_model': 'pos.deposit_master',
			'view_mode': 'form',
		}

	@api.multi
	def create_refund(self):
		return self.create_from_vals_and_next(0.00-self.partner_balance)


class pos_pcs_deposits(models.Model):

	_name = 'pos.partner_deposits'

	name = fields.Many2one('res.partner',  required=True)
	partner_deposit = fields.Float(digits=(7, 2), string='Partner deposite')

class pos_pcs_partner(models.Model):

	_inherit = 'res.partner'

	partner_balance = fields.Float(digits=(7, 2), string='Partner_balance',  readonly=True, compute='compute_vals2')
	deposits_ids = fields.One2many('pos.partner_deposits', 'name', string="Deposits")

	@api.one
	def compute_vals2(self):
		total_payment=0.0
		for curr in self.env['pos.order'].sudo().search([('partner_id','=', self.id)]):
			total_payment+=curr.amount_total

		_logger.warn('total_payment %s' % str(total_payment))

		total_debet=0.00
		for curr in self.env['pos.partner_deposits'].sudo().search([('name','=', self.id)]):
			total_debet+=curr.partner_deposit

		_logger.warn('total_debet %s' % str(total_debet))

		self.partner_balance =total_debet-total_payment

	@api.model
	def get_partner_balance(self, client):
		client=self.sudo().browse(client['id'])

		return client.partner_balance


