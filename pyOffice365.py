
OAUTH_URL = "https://accounts.accesscontrol.windows.net/tokens/OAuth/2"
GRAPH_DOMAIN = "graph.windows.net"
GRAPH_PRINCIPAL_ID = "00000002-0000-0000-c000-000000000000"

import json
import urllib
import urllib2

class pyOffice365():

	def __init__(self, domain, debug=False):
		self.domain = domain
		self.__access_token = None
		if debug:
			urllib2.install_opener(urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=1)))

	def login(self, user, passwd):
		postData = {
			"grant_type": "client_credentials",
			"resource": "%s/%s@%s" % (GRAPH_PRINCIPAL_ID, GRAPH_DOMAIN, self.domain),
			"client_id": "%s@%s" % (user, self.domain),
			"client_secret": passwd,
		}
		headers = {
			"Content-Type": "application/x-www-form-urlencoded",
		}
		req = urllib2.Request(OAUTH_URL, urllib.urlencode(postData), headers)
		u = urllib2.urlopen(req)
		data = u.readlines()
		jdata = json.loads('\n'.join(data))
		if jdata.has_key("access_token"):
			self.__access_token =  jdata["access_token"]

	def __auth_header__(self):
		return {
			"Authorization": "Bearer %s" % (self.__access_token),
			"Accept": "application/json;odata=nometadata",
			"Content-Type": "application/json;odata=nometadaa",
		}

	def __doreq__(self, command, data=None):
		req = urllib2.Request("https://%s/%s/%s?api-version=0.9" % (GRAPH_DOMAIN, self.domain, command), data=data, headers=self.__auth_header__())

		try:
			u = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			print e.read()
			return None

		data = u.readlines()
		try:
			jdata = json.loads('\n'.join(data))
		except:
			jdata = data
		return jdata

	def get_tenant(self):
		return self.__doreq__("tenantDetails")

	def get_users(self):
		return self.__doreq__("users")

	def get_metadata(self):
		return self.__doreq__("$metadata")

	def get_user(self, username):
		return self.__doreq__("users/%s@%s" % (username, self.domain))
	
	def create_user(self, userdata):
		return self.__doreq__("users", json.dumps(userdata))

	def assign_license(self, username, sku):
		postData = {
			"addLicenses": [
				{
					"disabledPlans": [],
					"skuId": sku,
				}
			],
			"removeLicenses": None,
		}

		return self.__doreq__("users/%s@%s/assignLicense" % (username, self.domain), json.dumps(postData))

