

	@api.one
	def calc_commision(self):
		for cc in self.lines:
			res = cc.onchange_qty(cc.product_id.id, self.discount, cc.qty, cc.price_unit)

			if self.discount and self.discount > 0:
				cc.discount = self.discount
				cc.price_subtotal = res['value']['price_subtotal']
				cc.price_subtotal_incl = res['value']['price_subtotal_incl']

			base_total = res['value']['price_subtotal_incl']

			_logger.warn('base_total %s' % str(base_total))

			if cc.product_id.pos_categ_id:
				_logger.warn('pos_categ_id %s' % str(cc.product_id.pos_categ_id))

				commis_obj = None

				if self.ref_company_id:
					commis_objs = self.env['pos.category.commission'].sudo().search(([('commissioner_id', '=',
					                                                                   self.ref_company_id.id), (
						                                                                  'category_id', '=',
						                                                                  cc.product_id.pos_categ_id.id)]))

					if commis_objs:
						cc.company_commision = round(base_total / 100 * commis_objs[0].commission_company, 2)
					else:
						_logger.warn(
							'dont find pos.category.commission for ref_company_id.id%s' % str(self.ref_company_id.id))

					cc.leader_commision = round(base_total / 100 * self.ref_company_id.commission_leader, 2)
				else:
					_logger.warn('dont set comapy id for order %s' % str(self))

				cc.guide_sale_commission = round(base_total / 100 * cc.product_id.pos_categ_id.guide_sale_commission, 2)

			cc.net_total = base_total - cc.company_commision - cc.leader_commision - cc.guide_sale_commission

	@api.model
	def thai_procc_ordero(self, id):
		order_obj = self.env['pos.order'].sudo().browse(id)

		if order_obj.partner_id:
			sessions_objs = self.env['pos.order.session'].sudo().search(([('leader_id', '=', order_obj.partner_id.id)]))
			_logger.warn('hai_procc_order sessions_objs %s' % str(sessions_objs))
			_logger.warn(' order_obj.partner_id.id %s' % str(order_obj.partner_id.id))

			if len(sessions_objs) > 0:
				session = sessions_objs[-1]
				order_obj.bus_session_id = session.id
				order_obj.calc_commision()

__author__ = 'vovan'

		journal= self.env['account.journal'].sudo().search([('type', '=', 'cash')])[0]
		account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

		create_vals = {

			'journal_id':journal.id,
			'account_id':account_id,

			# 'period_id':
			# 'company_id':
			# 'payment_rate'
			# 'comment':
			# 'payment_option':'without_writeoff',

			'type':'payment',

		}

		if self.guide_commission > 0:
			vals=create_vals.copy()

			vals['amount']=self.guide_commission
			vals['partner_id']=self.leader_id.id

			self.env['account.voucher'].create(vals)

		if self.driver_commission > 0:
			vals=create_vals.copy()

			vals['amount']=self.driver_commission
			vals['partner_id']=self.driver_id.id


			self.env['account.voucher'].create(vals)

	@api.one
	def del____get_report_by_date(self, date):
		ret_arr = []

		date_start_str = fields.Datetime.to_string(date)
		date_end_str = fields.Datetime.to_string(date + datetime.timedelta(days=1))

		_logger.warn('date_start_str %s' % str(date_start_str))
		_logger.warn('date_end_str %s' % str(date_end_str))

		domain = [('date_order', '>=', date_start_str), ('date_order', '<', date_end_str),
				  ('ref_company_id', '=', self.partner_id.id)]

		orders_objs = self.env['pos.order'].sudo().search(domain)

		_logger.warn('orders_objs %s' % str(orders_objs))

		guide_arr = []
		session_ids_arr = []

		for curr in orders_objs:
			if curr.leader_id not in guide_arr:
				guide_arr.append(curr.leader_id)

			if curr.order_pack_id:
				sess_id = curr.order_pack_id.bus_session_id.id
				if sess_id not in session_ids_arr:
					session_ids_arr.append(sess_id)

		for curr in guide_arr:
			session_objs = self.env['pos.order.session'].sudo().search(
				[('id', 'in', session_ids_arr), ('leader_id', '=', curr.id)])
			_logger.warn('orders_objs %s' % str(orders_objs))

			dd = list(domain)
			dd.append(('leader_id', '=', curr.id))
			_logger.warn('guide_orders_objs domain %s' % str(dd))

			guide_orders_objs = self.env['pos.order'].sudo().search(dd)
			_logger.warn('guide_orders_objs res %s' % str(guide_orders_objs))

			n_pax_count = 0

			for cc in session_objs:
				n_pax_count += cc.n_max

			amount_total = 0.00
			leader_commision = 0.00
			company_commision = 0.00

			for cc in guide_orders_objs:
				amount_total += cc.amount_total
				leader_commision += cc.leader_commision
				company_commision += cc.company_commision

			if n_pax_count > 0:
				total_avg = round(amount_total / n_pax_count, 2)
			else:
				total_avg = 0.00

			vals = {

				'guide': curr.name,
				'n_pax': n_pax_count,

				'amount_total': amount_total,
				'total_avg': total_avg,

				'leader_commision': leader_commision,
				'leader_commision_per': leader_commision,
				'company_commision': company_commision,

			}
			ret_arr.append(vals)
		return ret_arr

	@api.one
	def get_dates_arr(self):

		date_start = fields.Date.from_string(self.date_start)
		date_end = fields.Date.from_string(self.date_end)

		diff = (date_end - date_start).days
		diff += 1

		_logger.warn('diff %s' % str(diff))

		if diff < 0:
			return False

		dateList = []
		for x in range(diff):
			ddt = date_start + datetime.timedelta(days=x)

			dateList.append(ddt)

		return dateList
class partner_pack(models.Model):
	_name = 'partner.pack'

	_rec_name = 'id'

	qty= fields.Integer(string="Users Qty", default=25, required=True, states={'done':[('readonly',True)]})
	partner_ids = fields.One2many('res.partner', 'pack_id', string="Pack users", readonly=True)
	session_ids = fields.One2many('pos.order.session', 'client_pack_id', string="Sessions", readonly=True)

	state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string="Status", default='draft', readonly=True, copy=False)

	@api.one
	def get_report_list(self):
		first_flag=True

		ret_arr=[]
		procc_arr=[1,1]

		for curr in self.partner_ids:

			if first_flag:
				procc_arr[0]=curr
				first_flag=False

			else:
				procc_arr[1]=curr
				first_flag=True

				ret_arr.append(procc_arr)
				procc_arr=[1,1]

		return ret_arr

	@api.one
	def action_generate_clients(self):

		if self.state!='draft':
			return False

		self.start_time=fields.Date.today()

		user_code_prefix='042%05d' % self.id
		_logger.warn('user_code_prefix %s' % str(user_code_prefix))

		for curr in range(self.qty):
			partner_code=user_code_prefix+'%04d' % curr

			partner_code=partner_code+str(ean_checksum(partner_code+'z'))

			partner_vals={
				'name':partner_code,
				'ean13':partner_code,
				'pack_id': self.id,
			}

			_logger.warn('partner_vals %s' % str(partner_vals))
			self.env['res.partner'].sudo().create(partner_vals)

		_logger.warn('get_report_list( %s' % str(self.get_report_list()))

		#self.state='done'

	 	return True




@api.model
	def createzzzz(self, vals):

		session = super(partner_session, self).create(vals)
		order_pool=self.env['pos.order'].sudo()

		for curr in session.client_pack_id.partner_ids:
			if curr.partner_balance>0:
				pack_sess_objs=session.client_pack_id.session_ids

				product=self.env.ref('pos_thai.product_fake_pos_sale')

				session_ids = self.env['pos.session'].sudo().search([('state','=', 'opened')])
				ss=session_ids[0]

				if len(pack_sess_objs)>1:
					sess_name='%05d' % (pack_sess_objs[-2].id)
				else:
					sess_name='00000'

				name='FRS %s-%04d' % (sess_name, curr.id)

				lines=[]
				lines.append([0, 0, {'discount': 0, 'price_unit': curr.partner_balance, 'product_id': product.id, 'qty': 1}])

				order= {'user_id': SUPERUSER_ID,
						'name': name,
						'partner_id': curr.id,
						'amount_paid': 0,
						'pos_session_id': ss.id, #
						'lines': lines,
						'statement_ids': [],
						'amount_tax': 0,
						'uid': '', #
						'amount_return': 0-curr.partner_balance, #-100
						'sequence_number': 22,
						'amount_total': curr.partner_balance}

				order_id = order_pool._process_order(order)
				order_pool.browse(order_id).signal_workflow('paid')

		return session


class thai_pos_order_pack(models.Model):
	_name = 'pos.order.pack'

	state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], string="Status", default='draft', readonly=True, copy=False)

	name = fields.Many2one('res.partner', string="Client",  required=True, readonly=True)

	bus_session_id=fields.Many2one('pos.order.session', string="Bus session")

	leader_id = fields.Many2one('res.partner', string="Leader", store=True, readonly=True, related='bus_session_id.leader_id')
	driver_id = fields.Many2one('res.partner', string="Driver", store=True, readonly=True, related='bus_session_id.driver_id')
	ref_company_id = fields.Many2one('res.partner', string="Referal company", store=True, readonly=True, related='bus_session_id.ref_company_id')
	n_max= fields.Integer(string="N max", store=True, readonly=True, related='bus_session_id.n_max')

	order_ids = fields.One2many('pos.order', 'order_pack_id', string="Pack orders", readonly=True)
	order_lines_ids = fields.Many2many('pos.order.line', string="Order items", readonly=True, compute='compute_vals')

	discount = fields.Integer( string='Discount %', states={'paid': [('readonly', True)]})

	cash = fields.Float(digits=(7, 2), string='Cash', states={'paid': [('readonly', True)]})
	change = fields.Float(digits=(7, 2), string='Change', readonly=True)
	amount_total = fields.Float(digits=(7, 2), string='Total', readonly=True, compute='compute_vals')

	@api.onchange('cash')
	def change_cash(self):
		if not self.cash or self.cash<0:
			self.change=None
			return False

		diff=self.cash-self.amount_total

		if diff>=0:
			self.change=diff
		else:
			self.change=''


	@api.onchange('discount')
	def change_discount(self):
		self.compute_vals()

	@api.one
	def action_paid(self):

		disc=0.00
		if self.discount and self.discount>0 and self.discount<100:
			disc=self.discount

		for curr in self.order_ids:

			order_to_pay=0.00

			for cc in curr.lines:
				res=cc.onchange_qty(cc.product_id.id, disc, cc.qty, cc.price_unit)

				if self.discount and self.discount>0:
					cc.discount=disc
					cc.price_subtotal=res['value']['price_subtotal']
					cc.price_subtotal_incl=res['value']['price_subtotal_incl']

				base_total=res['value']['price_subtotal_incl']

				order_to_pay+=base_total

				_logger.warn('base_total %s' % str(base_total))

				if cc.product_id.pos_categ_id:
					_logger.warn('pos_categ_id %s' % str(cc.product_id.pos_categ_id))

					commis_obj=None

					if curr.ref_company_id:
						commis_objs=self.env['pos.category.commission'].sudo().search(([('commissioner_id','=', curr.ref_company_id.id),('category_id','=', cc.product_id.pos_categ_id.id)]))

						if commis_objs:
							commis_obj=commis_objs[0]
						else:
							_logger.warn('dont find pos.category.commission for ref_company_id.id%s' % str(curr.ref_company_id.id))

					else:
						_logger.warn('dont set comapy id for order %s' % str(curr))

					if commis_obj:

							per=commis_obj.commission_leader
							if per>0:
								cc.leader_commision=  round(base_total/100*per,2)

							per=commis_obj.commission_company
							if per>0:
								cc.company_commision= round(base_total/100*per,2)

				cc.net_total=base_total-cc.company_commision-cc.leader_commision

			curr.statement_ids[0].amount=order_to_pay

			curr.action_paid()

		self.state='paid'

	@api.one
	def compute_vals(self):
		disc=0.00

		if self.discount and self.discount>0 and self.discount<100:
			disc=self.discount

		lines_arr=[]
		amount_total=0.00

		for curr in self.order_ids:

			for cc in curr.lines:
				lines_arr.append(cc.id)
				res=cc.onchange_qty(cc.product_id.id, disc, cc.qty, cc.price_unit)

				amount_total+=res['value']['price_subtotal_incl']

		self.amount_total=amount_total
		self.order_lines_ids=lines_arr



			@api.model
	def pack_order_old(self, id):

		order_obj=self.env['pos.order'].sudo().browse(id)

		if not order_obj.partner_id:
			return False

		pack_pool=self.env['pos.order.pack']
		pack_objs=pack_pool.sudo().search([('name','=', order_obj.partner_id.id),('state','=', 'draft')])

		_logger.warn('pack_order pack_obj %s' % str(pack_objs))

		if len(pack_objs)==0:
			pack_obj=pack_pool.sudo().create({'name':order_obj.partner_id.id})
		else:
			pack_obj=pack_objs[0]

		order_obj.order_pack_id=pack_obj.id

		#Search session
		if not order_obj.partner_id.pack_id:
			_logger.warn('dont found client pack for partner %s' % str(order_obj.partner_id))
			return False

		if not order_obj.partner_id.pack_id.session_ids:
			_logger.warn('dont found session in client pack for partner %s' % str(order_obj.partner_id))
			return False

		#Get last session
		session=order_obj.partner_id.pack_id.session_ids[-1]

		pack_obj.bus_session_id=session.id
		pack_obj.discount=session.ref_company_id.pos_disc

	def create_from_ui_old(self, cr, uid, orders, context=None):
		_logger.warn('create_from_ui %s' % str(orders))

		# Keep only new orders
		submitted_references = [o['data']['name'] for o in orders]
		existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
		existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
		existing_references = set([o['pos_reference'] for o in existing_orders])
		orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]

		order_ids = []

		for tmp_order in orders_to_save:
			to_invoice = tmp_order['to_invoice']
			order = tmp_order['data']
			order_id = self._process_order(cr, uid, order, context=context)
			####
			self.pack_order(cr, uid, order_id)
			####
			order_ids.append(order_id)

		return order_ids

