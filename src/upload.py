import httplib2 # pip install httplib2
import json

connectionIndexUrl = 'https://connection.keboola.com/v2/storage'
http = httplib2.Http()

def parseResponse(response):
    header = response[0]
    status = int(header['status'])
    if status not in range(200,300):
        raise Exception('http request failed')
    body = json.loads(response[1])
    result = { 'header': header, 'body': body}
    return result

def getRequest(url):
    response = http.request(url, 'GET')
    return parseResponse(response)

def postRequest(url, body, token):
    headers = {'X-Storageapi-token': token}
    body = json.dumps(body)
    response = http.request(url, 'POST', headers=headers, body=body)
    return parseResponse(response)

def getComponenUri(componentId):
    body = loadConnectionIndex()['body']
    components = body['components']
    component = filter(lambda c: c['id'] == componentId, components)
    return component[0]['uri']

def loadConnectionIndex():
    return getRequest(connectionIndexUrl)

def uploadTask(componentId, params, token):
    return 0
