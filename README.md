
Sample usage:

```python
import json
import pyOffice365

domain = "example.onmicrosoft.com"
domainid = "<DOMAIN GUID>"
appid = "<APPSERVICEPRINCIPAL GUID>"
key = "<APPSERVICEPRINCIPAL SYMMETRIC KEY>"

o = pyOffice365.pyOffice365(domain, domainid)

o.login(appid, key)

results = o.get_users()
print json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))

newUser = {
	"AccountEnabled": "true",
	"Country": "Australia",
	"DisplayName": "example 1",
	"GivenName": "example",
	"MailNickname": "example1",
	"Password": "can9r5gR40jJFFlL",
	"Surname": "one",
	"UsageLocation": "AU",
	"UserPrincipalName": "example1@example.onmicrosoft.com",
}

results = o.create_user(newUser)

print json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))

results = o.assign_license("example1", sku)

print json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))

```
