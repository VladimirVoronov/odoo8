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
from openerp import tools
import datetime

import logging

_logger = logging.getLogger(__name__)


class event_confirm(models.TransientModel):
	"""Event Confirmation"""
	_name = "pos.commision_report"

	date_start = fields.Date(string="Date Start",  default=fields.Date.today())
	date_end = fields.Date(string="Date End",  default=fields.Date.today())

	session_id = fields.Many2one('pos.order.session')

	partner_id = fields.Many2one('res.partner', string="Partner", domain="[ ('is_company','=', True)]")
	leader_id = fields.Many2one('res.partner', string="Guide", domain="[ ('parent_id','<>',False)]")

	type = fields.Selection([('company', 'Company'), ('guide', 'Guide'), ('seller', 'Seller'), ('shop', 'Shop')],
							default='shop', string="Report type", required=True)

	@api.model
	def get_categ_arr(self, session):
		ret_arr = []

		# domain=[('bus_session_id', '=', session.id)]
		domain = []

		categs = self.env['pos.category'].sudo().search(domain)

		for curr in categs:
			categ = {}

			categ['company_commision'] = 0.00
			categ['guide_sale_commission'] = 0.00
			categ['price_subtotal_incl'] = 0.00

			comm_objs = self.env['pos.category.commission'].sudo().search(
				[('category_id', '=', curr.id), ('commissioner_id', '=', session.ref_company_id.id)])
			if len(comm_objs) > 0:
				categ['commission_company_per'] = comm_objs[0].commission_company
			else:
				categ['commission_company_per'] = 0

			lines = self.env['pos.order.line'].sudo().search(
				[('bus_session_id', '=', session.id), ('product_id.pos_categ_id', '=', curr.id)])

			for cc in lines:
				categ['price_subtotal_incl'] += cc.price_subtotal_incl
				categ['company_commision'] += cc.company_commision
				categ['guide_sale_commission'] += cc.guide_sale_commission

			categ['name'] = curr.name
			categ['guide_sale_commission_per'] = curr.guide_sale_commission

			ret_arr.append(categ)

		_logger.warn('ret_arr.append(categ) %s' % str(ret_arr))

		return ret_arr

	@api.model
	def get_summ_by_field(self, session, field_name):

		sess_arr = []

		# _logger.warn('get_summ_by_field %s' % str(res))


		for curr in self.get_session_arr()[0]:
			sess_arr.append(curr.id)

		orders = self.env['pos.order'].sudo().search([('bus_session_id', '=', session.id)])

		ret_val = 0.00

		for curr in orders:
			ret_val += getattr(curr, field_name)

		return ret_val

	@api.one
	def get_session_arr(self):
		domain = [('id', 'in', []), ('leader_id', '=', 1)]
		domain = [('id', '>', 20)]
		domain = []

		if self.date_start:
			domain.append(('create_date', '>=', self.date_start + ' 00:00:00'))

		if self.date_end:
			domain.append(('create_date', '<', self.date_end+ ' 23:59:59'))

		if self.partner_id:
			domain.append(('ref_company_id', '=', self.partner_id.id))

		if self.leader_id:
			domain.append(('leader_id', '=', self.leader_id.id))


		if self.session_id:
			domain = [('id', '=', self.session_id.id)]

		#_logger.warn(' get_session_arr domain %s' % str(domain))
		#_logger.warn(' get_session_arr %s' % str(session_objs))

		session_objs = self.env['pos.order.session'].sudo().search(domain)

		return session_objs

	@api.one
	def get_category_details(self, session):

		domain = [[('id', 'in', []), ('leader_id', '=', 1)]]
		domain = []

		ret_arr = []

		return ret_arr

	@api.one
	def get_guide_commision(self):
		commision_objs = self.env['pos.category.commission'].sudo().search(
			[('commissioner_id', '=', self.partner_id.id)])

		if len(commision_objs) > 0:
			return commision_objs[0].commission_leader
		else:
			return 0

	@api.multi
	def print_report(self, data=None):

		datas = {
			 'ids': [self.id],
			 'model': 'pos.commision_report',
			 #'form': self.read(),
			}

		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'pos_thai.sales_commision',
			#'report_type': "qweb-pdf",
			#'report_type': 'pdf',
			'datas': datas,
		}

class thai_pos_report(models.Model):
	_inherit = 'report.pos.order'

	#leader_id = fields.Many2one('res.partner', string="Leader", required=True)
	#driver_id = fields.Many2one('res.partner', string="Driver")

	ref_company_id = fields.Many2one('res.partner', string="Referal company", required=True)
	guide_sale_id = fields.Many2one('res.partner', string="Sales Guide")
	pos_categ_id = fields.Many2one('pos.category', string="POS Category")

	leader_commision = fields.Float(digits=(7, 2), string='Leader commision', readonly=True)
	company_commision = fields.Float(digits=(7, 2), string='Company commision', readonly=True)
	net_total = fields.Float(digits=(7, 2), string='Net total', readonly=True)
	guide_sale_commission = fields.Float(digits=(7, 2), string='Guide sale comm')
	bus_session_id = fields.Many2one('pos.order.session', string="Bus session")

	n_max = fields.Integer(string="N pax")

	def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False,
					   lazy=True):
		res = super(thai_pos_report, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, orderby,
													  lazy)
		_logger.warn('read_group groupby %s' % str(groupby))

		n_pax_dic={}

		ss_ids=self.pool.get('pos.order.session').search(cr, uid, [])

		for curr in self.pool.get('pos.order.session').browse(cr, uid, ss_ids):
			n_pax_dic[curr.id]=curr.n_max

		for curr in res:
			_logger.warn('read_group curr %s' % str(curr))

			if curr.has_key('bus_session_id') and curr['bus_session_id']:
				bs=curr['bus_session_id'][0]
				curr['n_max']=n_pax_dic[bs]
			else:
				curr['n_max']=0


		return res

	def init(self, cr):
		tools.drop_view_if_exists(cr, 'report_pos_order')
		cr.execute("""
			create or replace view report_pos_order as (
				select
					min(l.id) as id,
					count(*) as nbr,
					min(l.n_max) as n_max,

					s.date_order as date,

					sum(l.leader_commision) as leader_commision,
					sum(l.company_commision) as company_commision,
					sum(l.net_total) as net_total,
					sum(l.guide_sale_commission) as guide_sale_commission,

					sum(l.qty * u.factor) as product_qty,
					sum(l.qty * l.price_unit) as price_total,
					sum((l.qty * l.price_unit) * (l.discount / 100)) as total_discount,
					(sum(l.qty*l.price_unit)/sum(l.qty * u.factor))::decimal as average_price,
					sum(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') as int)) as delay_validation,
					s.partner_id as partner_id,

					s.ref_company_id as ref_company_id,
					s.guide_sale_id as guide_sale_id,
					s.bus_session_id as bus_session_id,

					pt.pos_categ_id as pos_categ_id,

					s.state as state,
					s.user_id as user_id,
					s.location_id as location_id,
					s.company_id as company_id,
					s.sale_journal as journal_id,
					l.product_id as product_id,
					pt.categ_id as product_categ_id

				from pos_order_line as l
					left join pos_order s on (s.id=l.order_id)
					left join product_product p on (p.id=l.product_id)
					left join product_template pt on (pt.id=p.product_tmpl_id)
					left join product_uom u on (u.id=pt.uom_id)
				group by
					s.date_order, s.partner_id,s.state, pt.categ_id,

					s.bus_session_id, s.ref_company_id, s.guide_sale_id,  pt.pos_categ_id,

					s.user_id, s.location_id, s.company_id,s.sale_journal,l.product_id,s.create_date
				having
					sum(l.qty * u.factor) != 0)""")
