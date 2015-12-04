# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

import os
import suds

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

from rm_lib import get_my_client, get_tracking_client

import logging
_logger = logging.getLogger(__name__)

class rm_shipments_history(models.Model):
	
	_name = 'shipments.history'
	
	track_date = fields.Datetime(string="Track date", readonly=True)
	track_point = fields.Char(string="Track point", readonly=True)
	track_message = fields.Text(string="Message", readonly=True)
	
	model=fields.Char(string='Related Document Model', readonly=True)
	res_id=fields.Char(string='Related Document ID', readonly=True)  
	
	partner_id=fields.Many2one('res.partner', string="Customer")

class rm_service_type(models.Model):
	_name = 'shipments.service_type'
	code = fields.Char(string="Service code")
	name=fields.Char(string="Service")

class rm_service(models.Model):
	_name = 'shipments.service'
	_rec_name = 'service_offering_name'
	
	service_type_id=fields.Many2one('shipments.service_type', string="Service", required=True)
	service_offering_code=fields.Char(string="Service offering code")
	service_offering_name=fields.Char(string="Service offering name")

class rm_service_format(models.Model):
	_name = 'shipments.service_format'
	service_id=fields.Many2one('shipments.service', string="Service", required=True)
	code = fields.Char(string="Format code")
	name=fields.Char(string="Format name")
	
class rm_shipmets(models.Model):
	def procc_res(self, res):
		_logger.warn('RM API procc_res  FULL res %s' % str(res))
		#_logger.warn('RM API FULL res code %s' % str(res[0]))
		#_logger.warn('RM API FULL res code %s' % str(type(res[0])))
		
		reply=res[1]
		
		if res[0]==200:
			if reply.__dict__.has_key('integrationFooter') and  reply.integrationFooter.__dict__.has_key('errors'):
				error_text=''
				for curr in reply.integrationFooter.errors[0]:
					error_text+='Error code %s - %s \r\n' % (curr.errorCode,  curr.errorDescription)

				raise except_orm(_('Royal mail API Error!'),_(error_text))
				return False
		else:
			code=reply['exceptionDetails']['exceptionCode']
			text=reply['exceptionDetails']['exceptionText']
			
			error_text='Error code %s - %s' %(code, text)
			raise except_orm(_('Royal mail Server Answer Error! %s' % res[0]),_(error_text))
			return False
			
		return reply

	@api.one
	def action_get_label(self):
		if not self.track_number:
			return False
		
		if self.debug_mode=='r':
			client, header =get_my_client(sandbox=False)
		else:
			client, header =get_my_client()
			
		res= client.service.printLabel(header, self.track_number)
		res=self.procc_res(res)
		self.label1=res.label
		self.label1_name=self._name.replace('.','-')+'-'+str(self.id)+'.pdf'
		
	 	return True
	 
	@api.one
	def action_cancel_shipment(self):
		if not self.track_number:
			return False
		
		if self.debug_mode=='r':
			client, header =get_my_client(sandbox=False)
		else:
			client, header =get_my_client()
			
		res= client.service.printLabel(header, self.track_number)
		res=self.procc_res(res)
		self.rm_state='canceled'
		
	 	return True	
	 	
	@api.model			
	def cron_check(self, ids=False):
		_logger.warn('Start shiping Cron' )
		
		objs=self.search([('is_delivered','=',False),('track_number','!=',False)])
		for curr in objs:
			_logger.warn('Shiping Cron Procc %s' % str(curr))
			curr.action_get_track_history()
		return True	
	@api.one
	def action_get_track_history(self):
		
		if not self.track_number:
			return False
		
		history_pool=self.env['shipments.history']
		
		client, header =get_tracking_client()
		res= client.service.getSingleItemHistory(header, self.track_number)
		
		
		if res[0]==200:
			reply=res[1]
			
			if reply.integrationFooter.errors:
				error_text=''
				for curr in reply.integrationFooter.errors[0]:
					error_text+='Error code %s - %s \r\n' % (curr.errorCode,  curr.errorDescription)
				
				_logger.warn('Traking API get error %s' % str(error_text))
				return False
			else:
				for curr in reply['trackDetail']:
					dt=curr.trackDate+' '+curr.trackTime
					
					if history_pool.search_count([('track_date', '=', dt), ('model', '=', self._name), ('res_id', '=', self.id)])==0:
					
						create_vals={}
						create_vals['track_date']=dt
						create_vals['track_point']=curr.trackPoint
						create_vals['track_message']=curr.header
						
						create_vals['model']=self._name
						create_vals['res_id']=self.id
						
						if self._name=='sale.order' and self.partner_shipping_id:
							create_vals['partner_id']=self.partner_shipping_id.id
						
						if self.name=='shipments':
							create_vals['partner_id']=self.recipient_id.id
							
						_logger.warn('History create Vals %s' % str(create_vals))
						history_pool.create(create_vals)
					
				return True	
				 	
	 	else:
	 		_logger.warn('Traking API request Error. Server insver code %s' % str(res[0]))
	 		
 	 
	@api.one
	def action_send_to_server(self):
		if self._name=='sale.order':
			self.recipient_id=self.partner_shipping_id
		
		if self.debug_mode=='r':
			client, header =get_my_client(sandbox=False)
		else:
			client, header =get_my_client()
		
		requestedShipment={}
		
		if self.service_type_id.code=='R':
			#requestedShipment['shipmentType']=
			requestedShipment['shipmentType']={'code':'Return'}
		else:
			#requestedShipment['shipmentType']='Delivery'
			requestedShipment['shipmentType']={'code':'Delivery'}
			
		if self.service_occurence:
			requestedShipment['serviceOccurrence']=self.service_occurence
		
		requestedShipment['serviceType']={'code':self.service_type_id.code}
		requestedShipment['serviceOffering']={'serviceOfferingCode':{'code':self.offering_code_id.service_offering_code}}
		
		if self.service_format_id:
			requestedShipment['serviceFormat']={'serviceFormatCode':{'code':self.service_format_id.code}}
			
		if self.shipping_date:	
			requestedShipment['shippingDate']=self.shipping_date
		
		#Contact block
		recipientContact={}
		recipientContact['name']=self.recipient_id.name
		
		if self.recipient_id.phone:
			#TODO
			ph={'countryCode':'0044',
				'telephoneNumber':'07801123456',
			}
			recipientContact['telephoneNumber']=ph
			
		if self.recipient_id.email:
			recipientContact['electronicAddress']={'electronicAddress':self.recipient_id.email}
		
		#End Contact block	
		requestedShipment['recipientContact']=recipientContact
		
		#Address block
		recipientAddress={}
		recipientAddress['addressLine1']=self.recipient_id.street
		
		if self.recipient_id.street2:
			recipientAddress['addressLine2']=self.recipient_id.street2
		
		recipientAddress['postTown']=self.recipient_id.city
		recipientAddress['postcode']=self.recipient_id.zip
		
		if self.recipient_id.country_id:
			recipientAddress['country']={'countryCode':{'code':self.recipient_id.country_id.code}}
		
		requestedShipment['recipientAddress']=recipientAddress
		# END Address block
		
		requestedShipment['senderReference']='odoo'+self._name+ str(self.id)
		
		# Weight block 
		weight={
			'value':self.weight,
			'unitOfMeasure':{'unitOfMeasureCode':{'code':'g'}}
			}
		
		#Inrernational block
		if self.service_type_id.code=='I':
			parcel={}
			parcel['weight']=weight
			requestedShipment['internationalInfo']={'parcels':{'parcel':parcel}}
		else:	
			item={}

			item['numberOfItems']=1
			item['weight']=weight
		
			off={}
			off['itemID']='2000001'
			off['status']={'status':{'statusCode':''}}
			off['offlineShipments']=off
		
			#End
			requestedShipment['items']={'item':item}
		
		#Send Request
		res= client.service.createShipment(header, requestedShipment)
			
		res=self.procc_res(res)
		#_logger.warn('RM API PROCC res %s' % str(res.__dict__))
		
		self.req_rm_state=res.completedShipmentInfo.status.status.statusCode.code
		self.track_number=res.completedShipmentInfo.allCompletedShipments.completedShipments[0].shipments[0].shipmentNumber[0]
		self.rm_state='registered'
		
		self.action_get_label()
		return True
		
	_name = 'shipments'
	
	rm_state = fields.Selection([
		 ('draft', "Not active"),
		 ('error', "Error"),
		 ('registered', "Registered"),
		  ('canceled', "Canceled"),
	], default='draft', copy=False, readonly=True)
	
	debug_mode = fields.Selection([('r', 'Real'), ('s', 'SandBox')], string="Mode")
	
	#shipment_type_code = fields.Selection([('Delivery', 'Delivery'), ('Return', 'Return')], required=True, string="Type", default='Delivery')
	
	service_occurence = fields.Selection([('1', '1')], string="Occurence")
	
	#service_type_code=fields.Selection([('I', 'International'),
	#								('1', 'Royal Mail 24 / 1st Class'),
	#								('2', 'Royal Mail 48 / 2nd Class'),
	#								('T', 'Royal Mail Tracked 24 / 48'),
	#								('D', 'Special Delivery Guaranteed'),
	#								('R', 'Tracked Returns')], string="Service Type", required=True, default='T')
	
	#service_offering_code=fields.Selection([
	#									('OSA', 'INTERNATIONAL SIGNED ON ACCOUNT'),
	#									('OLA', 'INTERNATIONAL STANDARD ON ACCOUNT'),
	#									('OTC', 'INTERNATIONAL TRACKED & SIGNED ON ACCT'),
	#									('OTA', 'INTERNATIONAL TRACKED ON ACCOUNT'),
										
	#									('TSS', 'Tracked returns'),
	#									('TPS', 'Royal Mail Tracked'), 
	#									('TPS01', 'Royal Mail Tracked 01'), 
	#									('TRM', 'TRM'), 
	#									('MP6', 'MP6')], string="Service", required=True,  default='TPS')
	
	weight = fields.Integer(string="Weight g.", default=100, required=True)
	service_type_id = fields.Many2one('shipments.service_type', string="Service type")
	offering_code_id = fields.Many2one('shipments.service', string="Service",  domain="[('service_type_id', '=', service_type_id)]")
	#service_format_code=fields.Selection([('E', 'E')], string="Service Format")
	service_format_id = fields.Many2one('shipments.service_format', string="Service Format",  domain="[('service_id', '=', offering_code_id)]")
	
	shipping_date = fields.Date(string="Shipping Date", default=fields.Date.today(), copy=False)
	
	recipient_id = fields.Many2one('res.partner', string="Recipient", required=True)
	
	track_number = fields.Char(string="Track number", readonly=False, copy=False)
	req_state = fields.Char(string="Request rm_state", readonly=True, copy=False)
	
	label1 = fields.Binary(string='Label 1', readonly=True, copy=False)
	label1_name = fields.Char(string="File name", readonly=True)
	
	event_time = fields.Datetime(string="Event date", readonly=True, copy=False)
	status_code = fields.Char(string="Status code", readonly=True, copy=False)
	summary_line = fields.Text(string="Summary line", readonly=True, copy=False)
	
	is_delivered = fields.Boolean(string="Delivered ?", compute='compute_vals')
	rm_tracking_link = fields.Char(string="Track and Trace", compute='compute_vals', readonly=True)
	
	@api.onchange('service_type_id')
	def compute_service_type_id(self):
		self.offering_code_id=False
		self.service_format_id=False
		
	@api.onchange('offering_code_id')
	def compute_service(self):
		self.service_format_id=False	
		
	@api.one	
	def compute_vals(self):
		if self.track_number:
			self.rm_tracking_link=u'http://www.royalmail.com/portal/rm/track?trackNumber='+self.track_number
		
		self.is_delivered=False
		
		history_obj=history_pool=self.env['shipments.history'].search([('model', '=', self._name), ('res_id', '=', self.id)])
		
		for curr in history_obj:
			if curr.track_message=='Delivered':
				self.is_delivered=True