
OAUTH_URL = "https://login.windows.net/%s/oauth2/token?api-version=1.0"
GRAPH_DOMAIN = "graph.windows.net"
GRAPH_PRINCIPAL_ID = "00000002-0000-0000-c000-000000000000"

import json
import re
import types
import urllib
import urllib2

class pyOffice365():

	__re_skiptoken = re.compile('.*\$skiptoken=([^&]*).*')

	def __init__(self, domain, debug=False, apiversion='2013-04-05'):
		self.domain = domain
		self.__access_token = None
		self.apiversion = apiversion
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
		req = urllib2.Request(OAUTH_URL % (self.domain), urllib.urlencode(postData), headers)
		u = urllib2.urlopen(req)
		data = u.readlines()
		jdata = json.loads('\n'.join(data))
		if jdata.has_key("access_token"):
			self.__access_token =  jdata["access_token"]

	def __auth_header__(self):
		return {
			"Authorization": "Bearer %s" % (self.__access_token),
			"Accept": "application/json;odata=nometadata",
			"Content-Type": "application/json;odata=nometadata",
		}

	def __doreq__(self, command, postdata=None, querydata={}, method=None):
		querydata['api-version'] = self.apiversion
		
		req = urllib2.Request("https://%s/%s/%s?%s" % (GRAPH_DOMAIN, self.domain, command, urllib.urlencode(querydata)), data=postdata, headers=self.__auth_header__())

		if method is not None:
			req.get_method = lambda: method

		try:
			u = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			data = e.readlines()
			try:
				jdata = json.loads('\n'.join(data))
			except:
				jdata = data
			return jdata

		data = u.readlines()
		try:
			jdata = json.loads('\n'.join(data))
		except:
			jdata = data
		return jdata

	def get_tenant(self):
		return self.__doreq__("tenantDetails")

	def get_users(self):
		querydata = {}
		rdata = []

		while True:
			data = self.__doreq__("users", querydata=querydata)
			if type(data) != types.DictType:
				print data
				return None
			rdata += data["value"]
			if data.has_key("odata.nextLink"):
				skiptoken = self.__re_skiptoken.search(data["odata.nextLink"]).group(1)
				querydata["$skiptoken"] = skiptoken
			else:
				break

		return rdata

	def get_metadata(self):
		return self.__doreq__("$metadata")

	def get_skus(self):
		return self.__doreq__("subscribedSkus")

	def get_user(self, username):
		return self.__doreq__("users/%s@%s" % (username, self.domain))
	
	def create_user(self, userdata):
		return self.__doreq__("users", json.dumps(userdata))

	def update_user(self, username, userdata):
		return self.__doreq__("users/%s@%s" % (username, self.domain), postdata=json.dumps(userdata), method='PATCH')

	def assign_license(self, username, sku, remove = None):
		postData = {
			"addLicenses": [
				{
					"disabledPlans": [],
					"skuId": sku,
				}
			],
			"removeLicenses": remove,
		}

		return self.__doreq__("users/%s@%s/assignLicense" % (username, self.domain), postdata=json.dumps(postData))

