import httplib2 # pip install httplib2
import json
import time
from . import Exceptions

connectionIndexUrl = 'https://connection.keboola.com/v2/storage'
http = httplib2.Http()

def parseResponse(response):
    header = response[0]
    status = int(header['status'])
    if status not in range(200,300):
        if status < 500:
            raise Exceptions.UploadException('User error handling http request {0}'.format(response))
        else:
            raise Exception('http request failed: {0}'.format(response))
    body = json.loads(response[1])
    result = { 'header': header, 'body': body}
    return result


def getRequest(url, token):
    headers = {}
    if token != None:
        headers = {'X-StorageApi-Token': token}
    response = http.request(url, 'GET', headers=headers)
    return parseResponse(response)

def postRequest(url, body, token):
    headers = {'X-Storageapi-Token': token}
    headers['Content-Type'] = 'application/json; charset=UTF-8'
    body = json.dumps(body)
    response = http.request(url, 'POST', headers=headers, body=body)
    return parseResponse(response)

def getComponentUri(componentId):
    body = loadConnectionIndex()['body']
    components = body['components']
    filtered = filter(lambda c: c['id'] == componentId, components)
    component = filtered[0] if len(filtered) > 0 else None
    if component == None:
        raise Exceptions.UploadException('Unknown component:{0}'.format(componentId))
    return component['uri']

def loadConnectionIndex():
    return getRequest(connectionIndexUrl, None)


def waitForAsyncJob(url, token):
    jobDetail = {}
    timeout = 5
    while jobDetail.get('isFinished', False) != True:
        jobDetail = getRequest(url, token)['body']
        time.sleep(timeout)
    return jobDetail


def runTask(componentId, params, token):
    """
    run and poll async run job of a kbc component
    """
    componentUrl = "{0}/run".format(getComponentUri(componentId))
    response = postRequest(componentUrl, params, token)
    jobDetail = response['body']
    result = waitForAsyncJob(jobDetail['url'], token)
    if result['status'] != 'success':
        raise Exceptions.UploadException('Failed to upload file')
    return result