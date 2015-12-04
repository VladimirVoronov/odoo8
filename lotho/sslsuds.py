import httplib
import urllib2

from suds.transport.http import HttpTransport
from suds.client import Client
from suds.options import Options
from suds.properties import Unskin

import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)

def getClient(url, key, cert):
	transport = HttpClientAuthTransport(key, cert, timeout=60)
	return Client(url, transport = transport, faults=False)

# SUDS Client Auth solution
# Modified by Liam Friel (liam.friel@s3group.co): use of kwargs directly
class HttpClientAuthTransport(HttpTransport):
	def __init__(self, key, cert, **kwargs):
		HttpTransport.__init__(self, **kwargs)
		self.urlopener = urllib2.build_opener(HTTPSClientAuthHandler(key, cert))
		
#HTTPS Client Auth solution for urllib2, inspired by
# http://bugs.python.org/issue3466
# and improved by David Norton of Three Pillar Software. In this
# implementation, we use properties passed in rather than static module
# fields.
class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
	def __init__(self, key, cert):
		urllib2.HTTPSHandler.__init__(self)
		self.key = key
		self.cert = cert
		
	def https_open(self, req):
		#Rather than pass in a reference to a connection class, we pass in
		# a reference to a function which, for all intents and purposes,
		# will behave as a constructor
		return self.do_open(self.getConnection, req)
	
	def getConnection(self, host, timeout=None):
		try:
			connection = httplib.HTTPSConnection(host, timeout=timeout, key_file=self.key, cert_file=self.cert)
		except:
			# Python versions pre-2.6
			connection = httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)			
		return connection
	
