# -*- encoding: utf-8 -*-

##############################################################################
#
##############################################################################

from sslsuds import getClient
from suds.sax.element import Element
from suds.wsse import *
import os
import uuid

import os
import sha
import binascii
import base64
import time
import random

sandbox_app_id='0127229000'
work_app_id='0404554000'

path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

key=path+'/certs/mykey.pem'
cert=path+'/certs/mycert.pem'
	
def get_my_client(sandbox=True):
	# WARNING -don't forget path wsse file !!!! 
	
	#print path
	#print os.getcwd()
	#Variables
	user_name='ksenia.epishkina@gmail.comAPI'
	password = 'Password2014!'
	
	#Init client
	if sandbox:
		wsdl_file='sandbox_ShippingAPI_V2_0_8.wsdl'
		application_id=sandbox_app_id
	else:
		wsdl_file='ShippingAPI_V2_0_8.wsdl'
		application_id=work_app_id
		
	client= getClient('file://'+path+'/schemas/'+wsdl_file, key, cert)
	
	#Calc Variables
	tt=datetime.now()
	create_date =  time.strftime('%Y-%m-%dT%H:%M:%SZ', tt.timetuple())

	nonce =  str(random.randint(0,9999999999))
	hashedpassword = sha.new(password).digest()
	digest = sha.new(nonce + create_date + hashedpassword).digest()
	pass_digi = base64.b64encode(digest)
	code_nonce = base64.b64encode(nonce)
	trans_id= str(random.randint(0,9999999999))
	
	#Print debug info
	#print 'Nonce = ', nonce
	#print 'pass_digi= ', pass_digi
	#print 'code_nonce= ', code_nonce
	#print 'create_date= ', create_date
	#print 'trans id= ', trans_id
	
	#Set Security Header
	security = Security()
	
	token = UsernameToken(user_name, pass_digi)
	token.setnonce(code_nonce)
	token.setcreated(create_date)
	
	security.tokens.append(token)
	
	client.set_options(wsse=security)
	
	#Set vals integrationHeader
	indetification={
					'applicationId': application_id,
					'transactionId':trans_id,
					}
	header={
					'dateTime': create_date,
					'version': '2',
					'identification':indetification,
	}

	return client, header

def get_tracking_client():
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
	wsdl_file='Tracking_API_V1.2.wsdl'
	client= getClient('file://'+path+'/schemas/'+wsdl_file, key, cert)
	
	#Calc Variables
	tt=datetime.now()
	create_date =  time.strftime('%Y-%m-%dT%H:%M:%SZ', tt.timetuple())
	trans_id= str(random.randint(0,9999999999))
	
	#Set vals integrationHeader
	#work_app_id
	#sandbox_app_id
	
	indetification={'applicationId': work_app_id,
					'transactionId':trans_id,
					}
		
	header={		'dateTime': create_date,
					'version': '1.0',
					'identification':indetification,
	}

	return client, header

#client, header=get_tracking_client()
#print client

#res= client.service.getSingleItemHistory(header, 'JC442410020GB')
#res= client.service.getSingleItemHistory(header, 'FG243638793GB')
#res= client.service.getSingleItemSummary(header, 'FG243638793GB')
#res= client.service.getProofOfDelivery(header, 'FG243638793GB')
#print res 
#reply=res[1]

#if reply.integrationFooter.errors:
	#error_text=''
	#for curr in reply.integrationFooter.errors[0]:
#		error_text+='Error code %s - %s \r\n' % (curr.errorCode,  curr.errorDescription)
#	
#	print error_text
#else:
#	for curr in reply['trackDetail']:
#		print 'aaaa', curr


