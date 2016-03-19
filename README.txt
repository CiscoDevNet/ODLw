
ODLw - Open Daylight widget: 

ODL APIs allow programmatic access to multiple mounted devices for both config and operational data.  Config data is persistent and based on configuration data entered into the router however operational data is dynamic and based on the routers state at any given time.  A RESTFUL based tool is needed to store dynamic data and or any ODL response data for future access. 

ODLw Requirements:

A tool (application/process) that allows the storage of ODL restful response data. Must provide an API for programmatic interaction. This Tool will be referenced as ODL database widget or ODLw    

ODLw Functional Outline:

Data collection from ODL already has a vast API and will be used to collect the needed data from ODL. After ODL data collection (from whatever programatic method used) the URL and JSON response data will be used as primary inputs to ODLw's RESTFUL API.

A POST to ODLw will be used to store ODL data using the exact URL that was used to GET the data as well as the data itself. 
A GET to ODLw will be used to retrieve any ODL data previously stored in database. Filtering and sorting will be available as well as lookups of nested dictionaries that result from POSTed data. NOTE: the schema of data dictionaries can be identified by previously knowing the API response structure and or e.g. having access to the YANG model used if YANG was the basis for the schema. All stored data will have full time stamping, including created and updated timestamps. User authentication can be enabled if needed 

ODLw Unknowns:  

It is assumed all access MUST be in the form of a RESTFUL API. If that is the case there are pre/post data insertion hooks that could be called on the server side to <execute code> to achieve future/additional “needs”. It is unclear what those needs are at the moment.  

ODLw High-Level Architecture: 

ODLw is created from the Eve framework http://python-eve.org/. Python test code has been written to test/use ODLw however its RESTFUL API is the only interface required to use ODLw. In full disclosure this is a starting point only as most of the heavy lifting here is done via the EVE framework which enables the RESTFUL API. 


Using test.py:

Step0: Start mongodb

Step1: run oddlw.py via python odlw.py (this starts the API using defaults in settings.py file)
Step2: run test.py via python test.py
It will print out and then ask you to choose which built in API you want to use. These are just test APIs and access the Always on OSC server

Choose URL # 5 to GET all mounted devices
 Choose URL # 4 to GET interface config from mounted router node iosxrv-6 from Cisco-IOS-XR-ifmgr-oper(213-07-22)
 Choose URL # 7 to GET operational network-topology
 Choose URL # 6 to GET info on mounted device iosxrv-6
 Choose URL # 1 to GET loc-rib
 Choose URL # 3 to GET interface properties from mounted router node iosxrv-6 using Cisco-IOS-XR-ifmgr-oper(213-07-22)
 Choose URL # 2 to GET system time from mounted router node iosxrv-6 using Cisco-IOS-XR-shellutil-oper(2013-07-22)
 Choose URL # 8 to GET PCEP topology
Select the URL number to GET and run through odlw store/retrieve/delete test:

Once you select the URL it will GET that data from OSC Always on Server
It will then using the REST API POST that data to MongoDB
It will then GET that data using ID, URL and timestamp
It will then DELETE that data using ID and Etag



Manually using just the API

Step 1: GET  ODL data. This example is using two GET calls to an always on OSC server “oscsandbox.cisco.com" to get a mounted vXR router named iosxrv-6 interface information.  You will need an authentication header to GET this data.  Assume that was done for the sake of this example.   

url = "https://oscsandbox.cisco.com:443/controller/restconf/operational/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-ifmgr-oper:interface-properties/"

The above RESTFUL call to the server was used to produce the below operational JSON response data. The Below response data can be converted to a dictionary and can be decoded/parsed by understanding the schema. In the below case that schema comes from the Cisco-IOS-XR-ifmgr-oper@2015-01-07.yang model 

*Only interface GigabitEthernet0/0/0/1 shown 

Response data = {
    "interface-properties": {
        "data-nodes": {
            "data-node": [
                {
                    "data-node-name": "0/0/CPU0",
                    "system-view": {
                        "interfaces": {
                            "interface": [
                                {
                                    "interface-name": "GigabitEthernet0/0/0/1",
                                    "encapsulation": "ether",
                                    "bandwidth": 1000000,
                                    "sub-interface-mtu-overhead": 0,
                                    "l2-transport": false,
                                    "interface": "GigabitEthernet0/0/0/1",
                                    "actual-line-state": "im-state-up",
                                    "type": "IFT_GETHERNET",
                                    "actual-state": "im-state-up",
                                    "encapsulation-type-string": "ARPA",
                                    "mtu": 1514,
                                    "state": "im-state-up",
                                    "line-state": "im-state-up"
                                }]
  
The below REST URL GET is a config example were you can get configuration data such as interface IP addresses.     

url = "https://oscsandbox.cisco.com:443/controller/restconf/config/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-ifmgr-cfg:interface-configurations/"

*Only interface GigabitEthernet0/0/0/1 shown 

Response = {
    "interface-configurations": {
        "interface-configuration": [
            {
                "active": "act",
                "interface-name": "GigabitEthernet0/0/0/1",
                "description": "to iosxrv-5",
                "Cisco-IOS-XR-ipv4-io-cfg:ipv4-network": {
                    "addresses": {
                        "primary": {
                            "netmask": "255.255.255.252",
                            "address": "10.0.0.38"
                        }
                    }
                }


Step 2: Now that you have data to store you can use the ODLw’s REST API to store the data along with the URL used to originally GET this data.  Prereq for Step2 is to have a mongoDB database running as well as ODLw enabled on the backend Server of choice.  
 
The Python Code below (from POSTMAN) loads the database via a POST and is following the basic schema below (This schema is defined in the ODLw code and could be as complex as needed however due to the vast difference in schema for every ODL API call the schema here is purposely left very basic i.e. The URL(url = string) used to GET the data and the JSON data (jsonresponse = dictionary)from that URL. 

odldata = [{ 'url’: uri, 'jsonresponses': odldata},]
 
The above schema allows the user to store the URL and the resulting data into the database. Note that this is easily done within Python code and or any programming language.  Example code has been written but is not reviewed here. 

The Below URL is basically the server side MongoDB API application defaults running locally using port 5000 accessing the odldata resource. The odldata resource has the above mentioned schema. 

url = "http://127.0.0.1:5000/odldata/"

payload = "[{\"jsonresponses\": {\"interface-configurations\": {\"interface-configuration\": [{\"active\": \"act\", \"Cisco-IOS-XR-ipv4-io-cfg:ipv4-network\": {\"addresses\": {\"primary\": {\"netmask\": \"255.255.255.252\", \"address\": \"10.0.0.34\"}}}, \"interface-name\": \"GigabitEthernet0/0/0/0\", \"description\": \"to iosxrv-3\"}, {\"active\": \"act\", \"Cisco-IOS-XR-ipv4-io-cfg:ipv4-network\": {\"addresses\": {\"primary\": {\"netmask\": \"255.255.255.0\", \"address\": \"172.16.1.207\"}}}, \"interface-name\": \"MgmtEth0/0/CPU0/0\", \"description\": \"OOB Management\"}, {\"active\": \"act\", \"interface-virtual\": \"\", \"Cisco-IOS-XR-ipv4-io-cfg:ipv4-network\": {\"addresses\": {\"primary\": {\"netmask\": \"255.255.255.255\", \"address\": \"192.168.0.6\"}}}, \"interface-name\": \"Loopback0\", \"description\": \"Loopback\"}, {\"active\": \"act\", \"Cisco-IOS-XR-ipv4-io-cfg:ipv4-network\": {\"addresses\": {\"primary\": {\"netmask\": \"255.255.255.252\", \"address\": \"10.0.0.26\"}}}, \"interface-name\": \"GigabitEthernet0/0/0/2\", \"description\": \"to iosxrv-2\"}, {\"active\": \"act\", \"Cisco-IOS-XR-ipv4-io-cfg:ipv4-network\": {\"addresses\": {\"primary\": {\"netmask\": \"255.255.255.252\", \"address\": \"10.0.0.38\"}}}, \"interface-name\": \"GigabitEthernet0/0/0/1\", \"description\": \"to iosxrv-5\"}]}}, \"url\”: \"https://oscsandbox.cisco.com:666/controller/restconf/config/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-ifmgr-cfg:interface-configurations/\"}]"

headers = {
    'content-type': "application/json", }

response = requests.request("POST", url, data=payload, headers=headers)

For sake of example assume both above GETs were stored into the Tool via a similar POST operation. 

Step3: Your data has been stored i.e POSTED to the database. Now you can use REST API to GET the stored data. If you know the schema of the data you stored you can query for it specifically in the database using either a unique ID field that was created when the data was stored or the URL as a key via the ?where statement. Please note that no matter what you query on you will always get the full jsonresponse data that you stored into the database.  The reason all your stored data must be returned is that the schema for storage being used here is simply the URL and the data as a result of that URL. Unless that data/schema is known ahead of time the individual components of that data can’t be retrieved separately. It could be done per API call but since there are 100s of calls it isn’t practical to re-create the schema for each call. 

The below GET will retrieve your data based on the URL used to initially GET it from ODL as well as the timestamp of its creation. This is just one example of how to GET your data from ODLw.

Example GET URL: http://127.0.0.1:5000/odldata?where={"url”: "https://oscsandbox.cisco.com:443/controller/restconf/operational/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-ifmgr-oper:interface-properties/","_created": "Tue, 08 Mar 2016 19:58:22 GMT”}

The above GET will result in the entire ODL jsonresponse getting returned
{
    "interface-properties": {
        "data-nodes": {
            "data-node": [
                {
                    "data-node-name": "0/0/CPU0",
                    "system-view": {
                        "interfaces": {
                            "interface": [
                                {
                                    "interface-name": "GigabitEthernet0/0/0/1",
                                    "encapsulation": "ether",
                                    "bandwidth": 1000000,
                                    "sub-interface-mtu-overhead": 0,
                                    "l2-transport": false,
                                    "interface": "GigabitEthernet0/0/0/1",
                                    "actual-line-state": "im-state-up",
                                    "type": "IFT_GETHERNET",
                                    "actual-state": "im-state-up",
                                    "encapsulation-type-string": "ARPA",
                                    "mtu": 1514,
                                    "state": "im-state-up",
                                    "line-state": "im-state-up"
                                }]

OR

Another method using a query string if you know the schema of the data you stored  you can use the below method.  This method is powerful as you can query on virtually anything you stored in the jsonresponse field. The only drawback is you must understand the data’s schema and you must also ensure you are looking at the correct data I.e. You may have stored that same data several times with repeat POSTs. If duplicate data exists you will need the _ID, _etag or any of the timestamps to uniquely identify the data. 

You can see below we are making a query of a deeply nested dictionary. In the below case you can see we are walking this nested dictionary until we identify the interface by name.
Example GET URL: http://127.0.0.1:5000/odldata?where={"jsonresponses.interface-properties.data-nodes.data-node.system-view.interfaces.interface.interface-name":"GigabitEthernet0/0/0/1","_created": "Tue, 08 Mar 2016 19:58:22 GMT”}

{
    "interface-properties": {
        "data-nodes": {
            "data-node": [
                {
                    "data-node-name": "0/0/CPU0",
                    "system-view": {
                        "interfaces": {
                            "interface": [
                                {
                                    "interface-name": "GigabitEthernet0/0/0/1",
                                    "encapsulation": "ether",
                                    "bandwidth": 1000000,
                                    "sub-interface-mtu-overhead": 0,
                                    "l2-transport": false,
                                    "interface": "GigabitEthernet0/0/0/1",
                                    "actual-line-state": "im-state-up",
                                    "type": "IFT_GETHERNET",
                                    "actual-state": "im-state-up",
                                    "encapsulation-type-string": "ARPA",
                                    "mtu": 1514,
                                    "state": "im-state-up",
                                    "line-state": "im-state-up"
                                }]


Here is the actual data returned. It is formatted in an _items list. _update, _links, _created, _id, _etag, _meta keys are all added automatically from the EVE framework. 

{
    "_items": [
        {
            "_updated": "Tue, 08 Mar 2016 19:58:22 GMT",
            "jsonresponses": {
                "interface-properties": {
                    "data-nodes": {
                        "data-node": [
                            {
                                "data-node-name": "0/0/CPU0",
                                "system-view": {
                                    "interfaces": {
                                        "interface": [
                                            {
                                                "encapsulation-type-string": "ARPA",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "MgmtEth0/0/CPU0/0",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 1514,
                                                "line-state": "im-state-up",
                                                "bandwidth": 0,
                                                "interface": "MgmtEth0/0/CPU0/0",
                                                "encapsulation": "ether",
                                                "type": "IFT_ETHERNET"
                                            },
                                            {
                                                "encapsulation-type-string": "Null",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "Null0",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 1500,
                                                "line-state": "im-state-up",
                                                "bandwidth": 0,
                                                "interface": "Null0",
                                                "encapsulation": "null",
                                                "type": "IFT_NULL"
                                            },
                                            {
                                                "encapsulation-type-string": "ARPA",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "GigabitEthernet0/0/0/2",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 1514,
                                                "line-state": "im-state-up",
                                                "bandwidth": 1000000,
                                                "interface": "GigabitEthernet0/0/0/2",
                                                "encapsulation": "ether",
                                                "type": "IFT_GETHERNET"
                                            },
                                            {
                                                "encapsulation-type-string": "FINT_BASE_CAPS",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "FINT0/0/CPU0",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 8000,
                                                "line-state": "im-state-up",
                                                "bandwidth": 0,
                                                "interface": "FINT0/0/CPU0",
                                                "encapsulation": "fint_base",
                                                "type": "IFT_FINT_INTF"
                                            },
                                            {
                                                "encapsulation-type-string": "Loopback",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "Loopback0",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 1500,
                                                "line-state": "im-state-up",
                                                "bandwidth": 0,
                                                "interface": "Loopback0",
                                                "encapsulation": "loopback",
                                                "type": "IFT_LOOPBACK"
                                            },
                                            {
                                                "encapsulation-type-string": "ARPA",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "GigabitEthernet0/0/0/1",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 1514,
                                                "line-state": "im-state-up",
                                                "bandwidth": 1000000,
                                                "interface": "GigabitEthernet0/0/0/1",
                                                "encapsulation": "ether",
                                                "type": "IFT_GETHERNET"
                                            },
                                            {
                                                "encapsulation-type-string": "ARPA",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "GigabitEthernet0/0/0/0",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 1514,
                                                "line-state": "im-state-up",
                                                "bandwidth": 1000000,
                                                "interface": "GigabitEthernet0/0/0/0",
                                                "encapsulation": "ether",
                                                "type": "IFT_GETHERNET"
                                            },
                                            {
                                                "encapsulation-type-string": "nV-Loopback",
                                                "sub-interface-mtu-overhead": 0,
                                                "interface-name": "nV-Loopback0",
                                                "state": "im-state-up",
                                                "actual-state": "im-state-up",
                                                "actual-line-state": "im-state-up",
                                                "l2-transport": false,
                                                "mtu": 1500,
                                                "line-state": "im-state-up",
                                                "bandwidth": 0,
                                                "interface": "nV-Loopback0",
                                                "encapsulation": "nv_loopback",
                                                "type": "IFT_NV_LOOPBACK"
                                            }
                                        ]
                                    }
                                },
                                "locationviews": {
                                    "locationview": [
                                        {
                                            "interfaces": {
                                                "interface": [
                                                    {
                                                        "encapsulation-type-string": "ARPA",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "MgmtEth0/0/CPU0/0",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 1514,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 0,
                                                        "interface": "MgmtEth0/0/CPU0/0",
                                                        "encapsulation": "ether",
                                                        "type": "IFT_ETHERNET"
                                                    },
                                                    {
                                                        "encapsulation-type-string": "Null",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "Null0",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 1500,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 0,
                                                        "interface": "Null0",
                                                        "encapsulation": "null",
                                                        "type": "IFT_NULL"
                                                    },
                                                    {
                                                        "encapsulation-type-string": "ARPA",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "GigabitEthernet0/0/0/2",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 1514,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 1000000,
                                                        "interface": "GigabitEthernet0/0/0/2",
                                                        "encapsulation": "ether",
                                                        "type": "IFT_GETHERNET"
                                                    },
                                                    {
                                                        "encapsulation-type-string": "FINT_BASE_CAPS",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "FINT0/0/CPU0",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 8000,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 0,
                                                        "interface": "FINT0/0/CPU0",
                                                        "encapsulation": "fint_base",
                                                        "type": "IFT_FINT_INTF"
                                                    },
                                                    {
                                                        "encapsulation-type-string": "Loopback",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "Loopback0",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 1500,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 0,
                                                        "interface": "Loopback0",
                                                        "encapsulation": "loopback",
                                                        "type": "IFT_LOOPBACK"
                                                    },
                                                    {
                                                        "encapsulation-type-string": "ARPA",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "GigabitEthernet0/0/0/1",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 1514,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 1000000,
                                                        "interface": "GigabitEthernet0/0/0/1",
                                                        "encapsulation": "ether",
                                                        "type": "IFT_GETHERNET"
                                                    },
                                                    {
                                                        "encapsulation-type-string": "ARPA",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "GigabitEthernet0/0/0/0",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 1514,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 1000000,
                                                        "interface": "GigabitEthernet0/0/0/0",
                                                        "encapsulation": "ether",
                                                        "type": "IFT_GETHERNET"
                                                    },
                                                    {
                                                        "encapsulation-type-string": "nV-Loopback",
                                                        "sub-interface-mtu-overhead": 0,
                                                        "interface-name": "nV-Loopback0",
                                                        "state": "im-state-up",
                                                        "actual-state": "im-state-up",
                                                        "actual-line-state": "im-state-up",
                                                        "l2-transport": false,
                                                        "mtu": 1500,
                                                        "line-state": "im-state-up",
                                                        "bandwidth": 0,
                                                        "interface": "nV-Loopback0",
                                                        "encapsulation": "nv_loopback",
                                                        "type": "IFT_NV_LOOPBACK"
                                                    }
                                                ]
                                            },
                                            "locationview-name": "0/0/CPU0"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            "url”: "https://oscsandbox.cisco.com:443/controller/restconf/operational/opendaylight-inventory:nodes/node/iosxrv-6/yang-ext:mount/Cisco-IOS-XR-ifmgr-oper:interface-properties/",
            "_links": {
                "self": {
                    "href": "odldata/56df2ede0b05cb27b307d5a8",
                    "title": "odldata"
                }
            },
            "_created": "Tue, 08 Mar 2016 19:58:22 GMT",
            "_id": "56df2ede0b05cb27b307d5a8",
            "_etag": "5a0e9f03dc221ec53b4cdb41951854ad7a3241f7"
        }
    ],
    "_links": {
        "self": {
            "href": "odldata?where={\"jsonresponses.interface-properties.data-nodes.data-node.system-view.interfaces.interface.interface-name\":\"GigabitEthernet0/0/0/1\",\"_created\": \"Tue, 08 Mar 2016 19:58:22 GMT\"}",
            "title": "odldata"
        },
        "parent": {
            "href": "/",
            "title": "home"
        }
    },
    "_meta": {
        "max_results": 25,
        "total": 1,
        "page": 1
    }
}



Other query examples:

The below will return all the URL links used to store data
http://127.0.0.1:5000/odldata/?projection={"url”:1}

A DELETE or PATCH will require the use of the _etag in an  if-Match header.
Example: delete object id or _id=56df2ede0b05cb27b307d5a8  with an etag of 5a0e9f03dc221ec53b4cdb41951854ad7a3241f7

headers = {'Content-Type': 'application/json', 'if-Match': ‘5a0e9f03dc221ec53b4cdb41951854ad7a3241f7'}
response = requests.delete(http://127.0.0.1:5000/odldata/56df2ede0b05cb27b307d5a8 , headers=headers) 



Jay Herbert
Systems Engineer.sales
jherbert@cisco.com
Mobile: +1 770 289 2577 

CCIE - 7619 Emeritus


