
import os
from eve import Eve
from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs
import requests
import json

#This data will change depending on the ip address of the server and port used when running odlw which uses the EVE framework. 
ENTRY_POINT = 'http://127.0.0.1:5000'
#This is the domain resource from the schema in the settings file
api_resource = 'odldata'



# Creates the URL based on resource provided. For now that resource is static based on the simple schema in the settings.py file
def endpoint(resource):
    return '%s/%s/' % (ENTRY_POINT, resource)

# Post ODLdata along with associated URL used to get ODLdata into a mongodatabase 
def odlw_post(url,odldata): 
 #This schema comes directly from Settings.py and is basic for now holding the GET URL and the associated response data    
    odlschema = [
        {
            'url': url,
            'jsonresponses': odldata
        },    
    ]

    headers = {'Content-Type': 'application/json'}
    r = requests.post(endpoint(api_resource),json.dumps(odlschema), headers=headers)
    status = r.status_code
    response = r.json()
    if status == 201 and response['_status'] == 'OK':
        _id = response['_id']
        updated_time = response['_updated']
        etag = response['_etag']
        return updated_time, etag, _id, status 
    else:
    	_id = 0
    	etag = ""
    	update_time = 0
    	return update_time, etag, _id, status

#funtion to get ODLdata from mongodatabase using the URL, ID and timestamp as a key. This is just one example of how to get data. the whole point would be to interface via REST API
#this function just allows easier testing of the API
def odlw_get(url,ids,timestamp):
	
	headers = {'Content-Type': 'application/json'}
	#query using timestamp, url and id values
	queryurl = endpoint(api_resource) + '?where={"url":"' +url+ '","_id":"'+ids+ '","_updated":"'+timestamp+ '"}'
	#query using just _ID value instead of timestamp
	#queryurl = endpoint(api_resource) + '?where={"url":"' +url+ '","_id":"'+ids+ '"}'
	
	#print queryurl + '\n\n'
	
	return requests.get(queryurl, headers=headers)
	#print "odlw_get returned ", response.status_code, '\n' 
	#print json.dumps(response.json(), indent=4) + '\n'
	
#function to delete a database entry based on the _id and etag of the stored data. 
#this function just allows easier testing of the API
def odlw_delete(_id,etag):
	headers = {'Content-Type': 'application/json', 'if-Match': etag}
	delurl = endpoint(api_resource) +_id
	return requests.delete(delurl, headers=headers)
	



#these are event hooks
# def post_get_callback(resource, request, lookup):
# def post_contacts_get_callback(request, lookup):



if __name__ == '__main__':
    # Heroku support: bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))

    app = Eve()
    Bootstrap(app)
    app.register_blueprint(eve_docs, url_prefix='/docs')

#THis is how you define hooks to run the def above which can be anything
    # app.on_post_GET += post_get_callback
    # app.on_post_GET_odldata += post_contacts_get_callback


    app.run(host='0.0.0.0', port=port, debug=True)

    
    