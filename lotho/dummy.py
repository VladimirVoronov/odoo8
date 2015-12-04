# -*- encoding: utf-8 -*-

##############################################################################
#
#
##############################################################################

from rm_lib import get_my_client


client, header =get_my_client()

cancel_numbers={'shipmentNumber':'xxxx'}
vals={
	'cancelShipments':cancel_numbers
	}
print client
res= client.service.createShipment(header, {})

for curr in res.integrationFooter.errors:
	print curr[1][0]['errorCode']
	print curr[1][0]['errorDescription']
