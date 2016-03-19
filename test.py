import requests
import json 
import random
import base64
import logging
import pymongo
from pymongo import MongoClient
from datetime import datetime
from odlw import odlw_post
from odlw import odlw_get
from odlw import odlw_delete



# Disable warnings because of the use of verify=False in requests methods
requests.packages.urllib3.disable_warnings()

#Used to access the always on OSC controller can be changed to access any controller
AlwaysOn_OSC = "https://oscsandbox.cisco.com/controller/"

url_dict={
	"url1": {"desc":"loc-rib",
			"url":AlwaysOn_OSC + "restconf/operational/bgp-rib:bgp-rib/rib/example-bgp-rib/loc-rib"},
	
	"url2": {"desc":"system time from mounted router node iosxrv-6 using Cisco-IOS-XR-shellutil-oper(2013-07-22)",
			"url":AlwaysOn_OSC + "restconf/operational/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-shellutil-oper:system-time/"},
	
	"url3": {"desc":"interface properties from mounted router node iosxrv-6 using Cisco-IOS-XR-ifmgr-oper(213-07-22)",
			"url":AlwaysOn_OSC + "restconf/operational/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-ifmgr-oper:interface-properties/"},

	"url4": {"desc":"interface config from mounted router node iosxrv-6 from Cisco-IOS-XR-ifmgr-oper(213-07-22)",
			"url":AlwaysOn_OSC + "restconf/config/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-ifmgr-cfg:interface-configurations/"},
	
	"url5": {"desc":"all mounted devices",
			"url":AlwaysOn_OSC + "restconf/operational/opendaylight-inventory:nodes/"},

	"url6": {"desc":"info on mounted device iosxrv-6",
			"url":AlwaysOn_OSC + "restconf/operational/opendaylight-inventory:nodes/node/iosxrv-6/"},

	"url7": {"desc":"operational network-topology",
			"url":AlwaysOn_OSC + "restconf/operational/network-topology:network-topology"},
	
	"url8": {"desc":"PCEP topology",
			"url":AlwaysOn_OSC + "restconf/operational/network-topology:network-topology/topology/pcep-topology"},
	
	
	}




#Get Token will grab a token and store in base64string. This is needed to use the always on OSC data. This function just writes the token to a file

def getosctoken():
	url = "https://oscsandbox.cisco.com/controller-auth"
	querystring = {"grant_type":"password","username":"admin","password":"C!sc0123","scope":"sdn"}
	headers = { 'content-type': "application/x-www-form-urlencoded"}
	response = requests.post(url, headers=headers, params=querystring, verify=False)
	resdata = response.json()
	username = "token"
	password = resdata['access_token']
	base64string = base64.encodestring(('%s:%s' % (username,password)).encode())
	basic_header = "Basic %s" % base64string.decode()
	basic_header = basic_header.strip('\n')
	tok = open("tokenfile.txt", "wb")
	tok.write(basic_header)
	tok.close()
	print "Token file has been refreshed"


def getoscdata(url,tokenheader):

	headers = {'authorization': tokenheader,'cache-control': "no-cache"}
	response = requests.get(url, headers=headers, verify=False)
	if response.status_code == 200: 
	    #print json.dumps(response.json(), indent=4) + '\n\n\n'
	    return response.json()
	else:
		print "ODL call failed with status code {}" .format(response.status_code)
		response = {}
		return response

#This function just automatically checks if the token for the "Always on OSC server" is a valid token by trying it 
def needtoken():
	result = False
	fo = open("tokenfile.txt", "r+")
	basicheader = fo.read()
	fo.close()
	url = url_dict["url1"]["url"]
	odldata = getoscdata(url,basicheader)
	if odldata == {}:
		result = True
	return result  

def printurl_dict():
	#print json.dumps(url_dict, indent=4) + '\n\n\n'
    for key,value in url_dict.iteritems():
		print " Choose URL # {} to GET {}".format(key[-1:], value["desc"])  
		
	


	


if __name__ == '__main__':
	#The above code ensures the token to be used for the "always on OSC sever" in valid. If not it grabs a new token and stores it in tokenfile.txt
	ntoken = needtoken()
	if ntoken:
		getosctoken()

	#Makes a call to the "always on OSC server" after setting what data via URL we are going to test i.e. GET
	fo = open("tokenfile.txt", "r+")
	basicheader = fo.read()
	fo.close()
	
	#prints GET options
	printurl_dict()


	#choose which API you would like to test
	ans = input("Select the URL number to GET and run through odlw store/retrieve/delete test:")
	url = url_dict["url"+ str(ans)]["url"]
	print url
	
	odldata = getoscdata(url, basicheader)
	print "The following JSON data was received via GET to {}".format(url)
	print json.dumps(odldata, indent=4) + '\n\n\n'


	#odlw_post called to POST data in mongo database. This could be done by using the EVE REST APIs or Pymongo methods.
	timestamp,etag,ids,status = odlw_post(url,odldata)
	print "ODL data was stored with the following parameters: \n id = {} \n timestamp = {} \n etag = {} \n status = {}".format(ids,timestamp,etag,status)
	

	#odlw_get uses the EVE API to GET ODL stored data using URL, timestamp and _id from mongo database
	res = odlw_get(url,ids,timestamp)
	if res.status_code == 200:
		print "\n\nThe following JSON data was received via GET from mongodb database using the following keys: \n url = {} \n ids = {} \n timestamp = {}".format(url,ids,timestamp)
		print json.dumps(res.json(),indent=4) + '\n'
	        

	#Delete a database document by using its id tag and etag. 
	d = odlw_delete(ids,etag)
	if d.status_code == 204:
		print "\n\nJSON data with an id tag of {} and etag of {} was deleted from mongo database".format(ids,etag)
	


        