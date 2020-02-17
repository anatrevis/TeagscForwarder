
import base64
from flask import Flask, request #import main Flask class and request object
import requests

app = Flask(__name__) #create the Flask app

storeClientID = 'niharika.rahman@teagasc.ie'
storeClientSecret = '8ac699db07885411414408228d1435162fe53243'


def send_data_sensoterra(deveui, jsondata, accessToken):
  URL = "https://monitor.sensoterra.com/apiportal/v2/decoder/%s/payload?soil=CLAY&encoding=hex" %deveui

  sensoTerraHeaders = {
        'Content-Type': "application/json",
        'Accept': "application/senml+json",
        'Authorization': accessToken,
        'Cache-Control': "no-cache",
        }

  r = requests.post(URL, json=jsondata, headers=sensoTerraHeaders)

  responsedata = r.json()

  print('Response: %s' % responsedata)
  return responsedata

def request_oauth_token():
  URL = 'https://monitor.sensoterra.com/apiportal/v2/oauth/token'
  oauthHeaders = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        }
  oauth_body = {
        'client_id': storeClientID,
        'client_secret': storeClientSecret,
        'grant_type': 'client_credentials',
        'scope': 'decoder'
        }

  r = requests.post(URL, json=oauth_body, headers=oauthHeaders)

  responsedata = r.json()

  print('Oauth data: %s' % responsedata)

  return responsedata['access_token'] if responsedata['access_token'] else ''


@app.route('/sensoterra/rest/callback/payloads/ul', methods=['POST']) #GET requests will be blocked
def json_example():
  req_data = request.get_json()

  storedAccessToken = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjU5YThhODMyYzg5NGI3OTNjZTc2M2ZkNGExYWY1MTZmZDQwNDBmZDZjMjYxZmYzNzkyNDhkMTE4NmE0NDdiMmE5OGVmM2ZhMWYyOWFjYzFhIn0.eyJhdWQiOiJuaWhhcmlrYS5yYWhtYW5AdGVhZ2FzYy5pZSIsImp0aSI6IjU5YThhODMyYzg5NGI3OTNjZTc2M2ZkNGExYWY1MTZmZDQwNDBmZDZjMjYxZmYzNzkyNDhkMTE4NmE0NDdiMmE5OGVmM2ZhMWYyOWFjYzFhIiwiaWF0IjoxNTgxNjMyMTE5LCJuYmYiOjE1ODE2MzIxMTksImV4cCI6MTU4NDIyNDExOSwic3ViIjoiIiwic2NvcGVzIjpbImRlY29kZXIiXX0.EIAqM9W0iGff2oTSMua1y2OZ442iEe0UHq3n5fxqQHoXXYfQAcNEqD7rTGBMJynsgj4mS69z_j9PXVZOAlgOVKujDnG_wuF9tOaCYpqee-5u_9O8GccCdzvS3Vac_l5Fp6McSTxt_O1GzAQywoNoI6bUjCXx05lUJurW-blUdefTM15XJn89LU4DcH5Udb-nrUjBrzTRPkD2Fag1faR20pcNG5_KN1zWq7rDUYN18oHxycQfvm-a3fNsdfAIFtsNbwecfPiUHdp_3QSt7PpAb5cw9DMyeNGVQJg5KZTqJ-wfCqPR0_LYhrAiJI9wQDfSE4dsYC_KjxffD9Afh9rn9A"

  port = int(req_data['port'])
  count = int(req_data['fcnt'])
  dataFrameB64 = req_data['dataFrame'] #two keys are needed because of the nested object
  dataFrameHEX = base64.b64decode(dataFrameB64).hex()
  deveui = req_data['deveui'] #an index is needed because of the array

  body = {'port': port,
          'payload': dataFrameHEX,
          'count': count
          }

  responsedata = None
  try:
    responsedata = send_data_sensoterra(deveui, body, storedAccessToken)

    if 'error' in responsedata:
      storedAccessToken =  "Bearer " + request_oauth_token()
      responsedata = send_data_sensoterra(deveui, body, storedAccessToken)

  except:
    print('Unable to forward data do sensoterra')


  return str(responsedata) if responsedata else "{error:'Unable to forward'}"


    # sensoterra_curl = "curl -X POST \"https://monitor.sensoterra.com/apiportal/v2/decoder/{deveui}/payload?encoding=hex\" -H \"accept: application/senml+json\" -H \"authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImMyNzJiNDBiNzA5MGM2YjI0YzVlYTUwY2QxNjhlZTQ1YThiNDkzOTNhZTMzZDI0MWU4ZTZhNWIwOWExYTVhM2YxZDIzYWI5NmFiM2RiNjA5In0.eyJhdWQiOiJuaWhhcmlrYS5yYWhtYW5AdGVhZ2FzYy5pZSIsImp0aSI6ImMyNzJiNDBiNzA5MGM2YjI0YzVlYTUwY2QxNjhlZTQ1YThiNDkzOTNhZTMzZDI0MWU4ZTZhNWIwOWExYTVhM2YxZDIzYWI5NmFiM2RiNjA5IiwiaWF0IjoxNTgxNDM5NTIzLCJuYmYiOjE1ODE0Mzk1MjMsImV4cCI6MTU4NDAzMTUyMywic3ViIjoiIiwic2NvcGVzIjpbImRlY29kZXIiXX0.NosXsE-g9PXnTSu3f-NuNlUxjnVWP7XDp6TgQHifF7cTEnbRfSYmTuRPr9jt1ieFjDlwudR-NBGp2nxWjXOkJ5e_27ataO-9c82RikD671V8wpa7aJpiP_DBrejQDfIJf95QhiZ3jF4vA8hVKXO1zzWAHGTo8YXDmGgB54LqAr-7zHJC21ean_6OzdA8Gd9uPXlqo7sJBu7fBqFMr8sFrvfdV8tw_4cCv8sC0sWDHfAzp8Y1h1qXrYi9zkX8DXFnG5Se9mEgZW_3Wq-IQcfrU5BRDOxRswCom8cYIE6AVCCN45IIronvHWzB3q2asKK386uvc2Be3oA3NaBToA047w\" -H \"Content-Type: application/json\" -d \"{ \"port\": 1, \"payload\": \"fa403e900fe403fa803e30000e\", \"count\": 860}\""
    # print (sensoterra_curl)
    # return '''
    #        The time_on_air_ms value is: {}
    #        The devaddr value is: {}
    #        The dataFrame is: {}
    #        The deveui is: {}'''.format(time_on_air_ms, devaddr, dataFrameHEX, deveui)


if __name__ == '__main__':
  app.run(debug=True, host='87.44.16.100', port=8080) #run app in debug mode on port 5000
