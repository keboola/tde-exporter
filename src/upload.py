import httplib2 # pip install httplib2
import json

connectionIndexUrl = 'https://connection.keboola.com/v2/storage'

def parseResponse(response):
    body = json.loads(response[1])
    result = { 'header': response[0], 'body': body}
    return result

def getRequest(url):
    h = httplib2.Http()
    response = h.request(url, 'GET')
    return parseResponse(response)


def getComponenUri(componentId):
    body = loadConnectionIndex()['body']
    components = body['components']
    component = filter(lambda c: c['id'] == componentId, components)
    return component[0]['uri']

def loadConnectionIndex():
    return getRequest(connectionIndexUrl)



def uploadTask(componentId, params):
    return 0
