# import socket

# HOST = '192.168.0.11'  # Standard loopback interface address (localhost)  - same network as Sensoterra
# PORT = 80       # Port to listen on (non-privileged ports are > 1023) - where sensor data is

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by', addr)
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             conn.sendall(data)


# This is the Davra to SensoTerra Bridge
# Copyright Davra Networks Ltd August 2019
# for use on the Davra Platform only as an embedded Microservice.

from flask import Flask
import os
import time, requests, os.path
import datetime
import sys
import getopt
import json
import base64
from binascii import unhexlify, b2a_base64
from time import gmtime, strftime
from random import randint
app = Flask(__name__)
#globals
start = int(round(time.time()))
print("Starting python app")


token1 ="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImE1NGQ4YmEyZTU2Yzk2Mjk4NTMyODZlNzYwMzJmZWYxZDk3Mjc1MmI0NjEzN2FlZmEzOTcwMzUzMjI1ZWVmOTg1NWU3MDM0ZmFkZWNjNmQ3In0.eyJhdWQiOiJuaWhhcmlrYS5yYWhtYW5AdGVhZ2FzYy5pZSIsImp0aSI6ImE1NGQ4YmEyZTU2Yzk2Mjk4NTMyODZlNzYwMzJmZWYxZDk3Mjc1MmI0NjEzN2FlZmEzOTcwMzUzMjI1ZWVmOTg1NWU3MDM0ZmFkZWNjNmQ3IiwiaWF0IjoxNTc2MjMzMzI4LCJuYmYiOjE1NzYyMzMzMjgsImV4cCI6MTU3ODk5ODEyOCwic3ViIjoiIiwic2NvcGVzIjpbImRlY29kZXIiXX0.wK8C0MDih5SvatoIN3uYBbPSbW1qcxtwPWk6zDQg1xOlALMlC4f7nMN4Ab2DdJC4sFuKEhlude_Pf5jeTEySz6YxqrmGcj-Q-rU8DQlMU0Jw8azOCVnuT33siU6PMMapL7zAeby6tRBezfURiTDjX3JlmINLby3RgkPLwXXDAsnvEM4YyFVWiVKlN0H_smT669l0Gbm2tvOEe4Noa1MOsekZK7QKm15SfyhD59bllh7npWTpMgU4uHmSwpeLbvBRWWt872VQgbBItt0NQUOD869U_P_Phr1JGLzlR3Q17ZstreRIFnUJPRlmojd7yeyj8l97S2DAybx6rrq5SzfZ9Q"
# RESPONSE from NL [{"bver":3,"bn":"urn:dev:com.sensoterra:18000218597","bt":1564659048,"u":"lat","v":52.2924232},{"u":"lon","v":-6.4994755},{"v":34.4,"u":"%vol","depth":15,"soil":"SAND","ut":5400},{"v":34.3,"u":"%vol","depth":15,"soil":"SAND","t":-3600,"ut":5400},{"v":34,"u":"%vol","depth":15,"soil":"SAND","t":-7200,"ut":5400},{"v":33.9,"u":"%vol","depth":15,"soil":"SAND","t":-10800,"ut":5400},{"v":33.9,"u":"%vol","depth":15,"soil":"SAND","t":-14400,"ut":5400},{"v":33.9,"u":"%vol","depth":15,"soil":"SAND","t":-18000,"ut":5400}]
pnPayload = "{\"moteType_id\":\"5d3eee30a039900015f930f2\"}"   # this is the id of the device type don't change this
pnEndPoint = "http://pervasivenation.davra.com"
pnQueryurl = pnEndPoint + "/moteManager/api/v1/payloads/query"
objectStoreUrl = pnEndPoint+"/api/v1/objectstore/"
lastTimeStamp = 1576233707014
collection ="teagasc"

colurl = objectStoreUrl+str(collection)

print(colurl)
internalHeader = {
    'Content-Type': "application/json",
    'Authorization': "Bearer FYs11VA8hMxnBG3joviTd188WWW4zXU8VUwabf97o8Rzh80P",
    'cache-control': "no-cache"
    }
    
# header for sensoterra    
  

@app.route("/")

def readSettings():
# this function will read in a JSON file and will return an json object
    settings=""
    try:
       with open("/src/settings.json","r") as fs:
         text = fs.readlines()
         for line in text:
             line = line.rstrip()
             settings=settings+str(line.strip('\n'))
             print("The token was read " + str(line))
    except:
        
        print("There is a problem opening the settings file")
    finally:
       fs.close

    return settings    
def checkObjectStore(VERB, searchurl, internalHeader,col):
    payload = ""
    print(searchurl)
    response = requests.request(VERB, searchurl, data=payload, headers=internalHeader)
    print("Waiting 1 second " +str(response.status_code))
    if response.status_code == 200:
       print("RestHeart collection  found " + str(response.status_code))
# should read in the last timestamp       
         
    else:
       print("RestHeart collection not found " + str(response.status_code))   
       ans = createObjectStore(internalHeader,collection, searchurl)
    return response.text
###### end of checkObjectStore()

def createObjectStore(internalHeader, collectionName, colurl):

########################## create the object store collections ~#############################
    documentCollection = collectionName
    payload =""
    urlToSend = colurl
    print(urlToSend)

    response = requests.request("PUT", urlToSend, data=payload, headers=internalHeader)
    if response.status_code == 200:
       print("RestHeart " + str(documentCollection) + "  collection  created " + str(response.status_code))
       time.sleep(1)
       ts = ((long(time.time())*100)-((86400*1.5)*1000)) #set the last time for a day and a half back
       timePayload = json.dumps({"timeStamp":ts})
       updateLastTime(urlToSend, timePayload, internalHeader )
    else:
       print("RestHeart " + str(documentCollection) + "  collection  was NOT created " + str(response.status_code))   
    
    return response.status_code
###### end of   createObjectStore()

def updateLastTime(urlToSend, timePayload, internalHeader ):
# updates the lastTimeStamp in the objectstore

    response = requests.request("PUT", urlToSend, data=timePayload, headers=internalHeader)
    print("changed the time =====================> " + str(timePayload))
    return response.text
    
#end of updateLastTime()   
def getTimeStamp(colurl, internalHeader):
# returns the currently store time stamp in the objectstore for the collection
       time.sleep(1)
       response = requests.request("GET", colurl, data="", headers=internalHeader)
       tsObj = json.loads(response.text)
       print(response.text + "  " + str(tsObj['timeStamp']))    
       tbr = long(tsObj['timeStamp'])
       return tbr   # return the timestamp as long
       
#######   end of getTimeStamp()

def parseDevicePayloads(receivedFrames, sensoTerraHeaders, lastTimeStamp, colurl, internalHeader):
# this function parses out each of the return rows from receivedFrames and uses the time stamp as the indicator to POST to NL
# once the timestamp of the dataframe is > than the lastTimeStamp they will be pushed.
# after the POST to NL the timestamp is updated in the objectstore
    x = 0
    currentTimeStamp = 0

    for singleFrame in receivedFrames:
        try:
#           get the outer metrics as post in to inmarsat. 
            loraPort =2
            LoRaDevice = singleFrame["deveui"]
            tstamp = singleFrame["timestamp"]
            print("This is the time stamp " + str(tstamp))
            
            dataFrm = singleFrame["payload"]["dataFrame"]         #the actual payload
            fcnt= singleFrame["payload"]["fcnt"]                  #fcnt
            rssi = singleFrame["payload"]["rssi"]                 #lora rssi
            snr= singleFrame["payload"]["snr"]
            sf_used=singleFrame["payload"]["sf_used"]             #sf used
            live = singleFrame["payload"]["live"]
            loraId = singleFrame["payload"]["id"]
            decrypted = singleFrame["payload"]["decrypted"]       # always true
            type = "payloads/ul"    
            plTimeStamp = singleFrame["payload"]["timestamp"]     #payload timestamp
            print("This is the payload " + str(dataFrm))
            dfValue= str(dataFrm)  
            converted = base64.b64decode(dfValue).encode('hex')   # convert the base64 string back into hex string 
            print("This is the result " + str(converted)) 
            payload = {"payload":converted}
 

            sensourl = "https://monitor.sensoterra.com/apiportal/v2/decoder/" + str(LoRaDevice)+"/payload?encoding=hex" 
            payload = {"port": 1, "payload":converted , "count":fcnt}
            payload = json.dumps(payload)

            time.sleep(.2)
            if  tstamp > lastTimeStamp :
                currentTimeStamp = tstamp
                response = requests.request("POST", sensourl, data=payload, headers=sensoTerraHeaders)
                print("Not present updating record " + str(currentTimeStamp))
                print("Result from NL " + response.text)
                timePayload = json.dumps({"timeStamp":tstamp})
                updateLastTime(colurl, timePayload, internalHeader )

                
            else:
                print("Record already inserted but still updating the time stamp")

        except:
            print("Issue with Row ")
            x=x 
        finally:                
            x=x+1
    return currentTimeStamp    
#end of parseDevicePayloads)
if __name__ == '__main__':
     dirpath = os.getcwd()
     print("current directory is : " + dirpath)
     foldername = os.path.basename(dirpath)
     print("Directory name is : " + foldername)  
#     settingsObj = json.loads(readSettings())    
#     deviceArray =  str(settingsObj["decoder"])
     deviceArray =  {"5d3eee30a039900015f930f2"}
     accessToken =  "Bearer " + str(token1)


     sensoTerraHeaders = {
              'Content-Type': "application/json",
              'Accept': "application/senml+json",
              'Authorization': accessToken,
              'Cache-Control': "no-cache",
              } 

 
       
     time.sleep(10)         
     returnedTS = 0
     searchurl = colurl 
     answer = checkObjectStore("GET", searchurl, internalHeader, collection)
     print(answer)
     time.sleep(1)
     
     tbr = getTimeStamp(colurl, internalHeader)
     print("This is the returned Time " + str(tbr))

     while True:
        for singleDevice in deviceArray:

            response = requests.request("POST", pnQueryurl, data=pnPayload, headers=internalHeader)
            print(response.text)    
            receivedFrames = json.loads(response.text)
            print("The last Time stamp...................." + str(lastTimeStamp))
            
            
            returnedTS = parseDevicePayloads(receivedFrames, sensoTerraHeaders, lastTimeStamp,colurl,internalHeader)
            if returnedTS > lastTimeStamp:
                lastTimeStamp = returnedTS
                print("The last Time stamp is " + str(lastTimeStamp)  +"    " +  str(returnedTS))
            else:
                print("No Records updated since " + str(lastTimeStamp))
        print("Sweep finished now " + str(datetime.datetime.now()) + " and will restart again in 60 Mins. for time stamps after " + str(lastTimeStamp))
        
#        print("Sweep finished now " + str(datetime.datetime.now()) + " and will restart again in 5 Mins. for time stamps after " + str(lastTimeStamp))   
        time.sleep(3600)
        print("Davra SensoTerra Bridge")