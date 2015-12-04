__author__ = 'vovan'

import requests


base_url='https://api.bookeo.com/v2/'
secretKey='xxxx'
apiKey='xxx'
apiKey='xxx'


def get_bookeo_vals (command, vals={}, type='GET'):
	print 'Procc ', command
	payload = {'secretKey':secretKey, 'apiKey': apiKey}
	payload.update(vals)

	r = requests.get("https://api.bookeo.com/v2/"+command, params=payload)

	res= r.json()

	if r.status_code==200:
		if res.has_key('info'):
			print res['info']

		if res.has_key('data'):
			return res['data']
		else:
			return res

	else:
		raise Exception(r.json()['message'])


def test():
	#res=get_bookeo_vals ('settings/products')
	#for curr in res:
	#	print
	#	print curr


	vals={ 'startTime':'2015-08-01T09:00:00+11:00', 'endTime':'2015-08-30T09:00:00+11:00'}
	res= get_bookeo_vals ('bookings', vals)

	for curr in res:
		create_vals = {}

		print '*'*30
		#print curr

		#print curr['eventId']
		#print curr['productName']

		#print curr['title']

		#event_name=curr['eventId']
		#print curr['eventId'][-10:]

		#print curr['participants']['numbers']

		for pp in curr['participants']['numbers']:

			if pp['peopleCategoryId']=='Cadults':
				create_vals['adult']= pp['number']

			if pp['peopleCategoryId']=='Cchildren':
				create_vals['child']= pp['number']

			if pp['peopleCategoryId']=='Cinfant':
				create_vals['infant']= pp['number']

		#print create_vals
		#print curr['bookingNumber']

		print curr['canceled']


		#print curr

	#print  get_bookeo_vals ('customers/%s' % '232MU44YK14D5C13F624', vals)


test()

#Procc  customers/232MU44YK14D5C13F624
#{u'phoneNumbers': [{u'type': u'mobile', u'number': u'0910951491'}], u'numBookings': 258, u'firstName': u'HOT VACATIONS', u'numCancelations': 2, u'lastName': u'SERG', u'startTimeOfNextBooking': u'2015-10-28T09:00:00+07:00', u'creationTime': u'2015-05-16T16:35:00+07:00', u'acceptSmsReminders': True, u'member': True, u'credit': {u'currency': u'THB', u'amount': u'0'}, u'streetAddress': {u'countryCode': u'TH'}, u'emailAddress': u'seregaphuket@gmail.com', u'startTimeOfPreviousBooking': u'2015-10-26T09:00:00+07:00', u'numNoShows': 0, u'id': u'232MU44YK14D5C13F624'}
