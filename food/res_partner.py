# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api

class food_res_partner(models.Model):

	_inherit = 'res.partner'

	manual_balance = fields.Float( string="Balance")
	currency_id = fields.Many2one('res.currency', string="Currency")

	mi = fields.Char(string="M.I.")
	customer_type = fields.Char(string="Customer Type")
	rep = fields.Char(string="Rep")
	vat_code = fields.Char(string="VAT Code")

	vat_country_id = fields.Many2one('res.country', string="VAT Country")
	vat_number = fields.Char(string="VAT Registration Number")

	account_no = fields.Char(string="Account No.")
	vat_code = fields.Char(string="VAT Code")

	js = fields.Char(string="Job Status")
	jt = fields.Char(string="Job Type")
	jd = fields.Char(string="Job Description")

	sd=fields.Date(string='Start Date')
	pe=fields.Date(string='Projected End')
	ed=fields.Date(string='End Date')

	thai_name = fields.Char(string="Thai name")
	thai_street =fields.Char(string="Thai Street")
	thai_street2 =fields.Char(string="Thai Street 2")
	thai_city =fields.Char(string="Thai city")
	thai_country =fields.Char(string="Thai country")

	report_colour =fields.Char(string="report_colour")
