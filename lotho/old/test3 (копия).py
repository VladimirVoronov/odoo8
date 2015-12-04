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


user_name='ksenia.epishkina@gmail.comAPI'
password = 'Password2014!'

key=os.getcwd()+'/certs/mykey.pem'
cert=os.getcwd()+'/certs/mycert.pem'

application_id='0127229000'

client= getClient('file://'+os.getcwd()+'/schemas/ShippingAPI_V2_0_8.wsdl', key, cert)

tt=datetime.now()

create_date =  time.strftime('%Y-%m-%dT%H:%M:%S', tt.timetuple())
create_date2 =  time.strftime('%Y-%m-%dT%H:%M:%SZ', tt.timetuple())
#or
#create_date =  str(DateTime(tt))

nonce =  str(random.randint(0,9999999999))
hashedpassword = sha.new(password).digest()
digest = sha.new(nonce + create_date2 + hashedpassword).digest()
pass_digi = base64.b64encode(digest)
code_nonce = base64.b64encode(nonce)
trans_id= str(random.randint(0,9999999999))

indetification={
					'applicationId': application_id,
					'transactionId':trans_id,
					}
integration_header={
	'dateTime': create_date,
	'version': '2',
	'identification':indetification,
	}

mm={
''

}

print 'Nonce = ', nonce
print 'pass_digi= ', pass_digi
print 'code_nonce= ', code_nonce
print 'create_date= ', create_date
print 'trans id= ', trans_id

#print client

security = Security()

token = UsernameToken(user_name, pass_digi)
token.setnonce(code_nonce)
token.setcreated(create_date2)

security.tokens.append(token)

client.set_options(wsse=security)

cancel_numbers={'shipmentNumber':'RQ221150289GB'}
vals={
	'cancelShipments':cancel_numbers
	}

#print client.service.createShipment(integration_header)
v1 = ('v1', 'http://www.royalmailgroup.com/integration/core/V1')
v2 = ('v2', 'http://www.royalmailgroup.com/api/ship/V2')

root = Element('cancelShipments')
u = Element('shipmentNumber')
u.setText('RQ221150289GB')
root.append(u)

inter=Element('integrationHeader', ns=v2)

u = Element('dateTime', ns=v1)
u.setText(create_date)
inter.append(u)	

u = Element('version', ns=v1)
u.setText('2')
inter.append(u)

u = Element('identification', ns=v1)

c=Element('applicationId', ns=v1)
c.setText(application_id)
u.append(c)	

c=Element('transactionId', ns=v1)
c.setText(trans_id)
u.append(c)	

inter.append(u)	
		
print client.service.cancelShipment(integration_header, cancel_numbers)
#print client.service.cancelShipment(inter, root)
