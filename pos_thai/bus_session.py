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


class partner_session(models.Model):
	_name = 'pos.order.session'
	_order = 'id desc'


	state = fields.Selection([('draft', 'Open'), ('done', 'Close'), ('paid', 'Paid')], string="Status", default='draft',
							 readonly=True,
							 copy=False)

	name = fields.Char(string="Vehicle number", required=True, default='000', readonly=True)

	session_date = fields.Datetime(string="Date", default=fields.Datetime.now(), readonly=True)

	# client_pack_id = fields.Many2one('partner.pack', string="Client Pack",  required=True)
	pos_id = fields.Many2one('pos.config', string="POS")

	leader_id = fields.Many2one('res.partner', string="Guide", required=True, domain="[ ('parent_id','<>',False)]")
	thai_leader_id = fields.Many2one('res.partner', string="Thai guide name", domain="[ ('parent_id','<>',False)]")
	excursion_name = fields.Char(string="Excursion name")

	driver_id = fields.Many2one('res.partner', string="Driver", required=True, domain="[ ('parent_id','<>',False)]",
								default=4, readonly=True)

	guide_sale_id = fields.Many2one('res.partner', string="Sale Guide", required=True,
									domain="[ ('parent_id','<>',False)]",
									default=lambda self: self.env.user.partner_id.id, readonly=True)

	ref_company_id = fields.Many2one('res.partner', string="Referal company", required=True, readonly=True,
									 related='leader_id.parent_id')

	n_max = fields.Integer(string="N pax", default=0, required=True)

	vehicle_type = fields.Selection([('Bus', 'Bus'), ('Van', 'Van'), ('Taxi', 'Taxi')], string="Vehicle_type",
									required=True, default='Bus')

	# guide_commission = fields.Float(digits=(7, 2), readonly=True, compute='compute_vals2')
	# driver_commission = fields.Float(digits=(7, 2), readonly=True, compute='compute_vals2')

	def get_buss_ssesion(self, partner_id):

		if not partner_id:
			return False

		session_ids=self.search([('state','=', 'draft'), ('leader_id','=', partner_id.id)])

		if session_ids.exists():

			return session_ids[0].id

		else:

			create_vals={
				'leader_id':partner_id.id,
			}

			new_val=self.create(create_vals)
			return new_val.id

	@api.multi
	def name_get(self):
		result = []
		for ss in self:
			result.append((ss.id, "%s %s %s" % (ss.id, ss.session_date, ss.leader_id.name)))
		return result

	@api.multi
	def close_session(self):
		#vals = {
		#	'session_id': self.id,
		#	'type': 'guide',
		#}

		self.state = 'done'

		return True
		#report = self.env['pos.commision_report'].sudo().create(vals)
		#ret_val = report.print_report()
		#_logger.warn('ret_val %s' % str(ret_val))

	@api.one
	def action_payment(self):

		if not self.pos_id:
			raise Exception("Please set POS")
			return False

		sessions = self.env['pos.session'].sudo().search(
			([('state', '=', 'opened'), ('config_id', '=', self.pos_id.id)]))

		if not sessions.exists():
			raise Exception("Please open session for %s " % self.pos_id.name)
			return False

		statement = sessions.statement_ids[0]

		journal = self.env['account.journal'].sudo().search([('type', '=', 'cash')])[0]

		vals = {
			'date': self.create_date,
			'statement_id': statement.id,
			'journal_id': journal.id,
			'amount': -self.guide_commission,
			'account_id': journal.internal_account_id.id,
			'ref': 'gc',
			'name': 'Guide comm Bus Sess ID- %s' % self.id,
		}
		statement.line_ids.create(vals)
		statement.statement_close()
		self.state = 'paid'
		return True

	@api.one
	def compute_vals2(self):
		if self.vehicle_type == 'Bus':
			self.driver_commission = 100.00

		if self.vehicle_type == 'Van':
			self.driver_commission = 50.00

		if self.vehicle_type == 'Taxi':
			self.driver_commission = 50.00

		vals = {
			'type': 'guide',
		}

	# report = self.env['pos.commision_report'].sudo().create(vals)
	# self.guide_commission = report.get_summ_by_field(self, 'leader_commision')



