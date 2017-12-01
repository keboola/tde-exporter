"""
wraps keboola connection api
runs and polls kbc components jobs
"""
import httplib2 # pip install httplib2
import json
import time
import os
import Exceptions
from logger import debug

connectionIndexUrl = os.environ['KBC_URL'] + '/v2/storage'
http = httplib2.Http()

def parseResponse(response):
    """
    take http @response, raise if status code is not 200
    @return object with header and body extracted from the @response
    """
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
    """
    call a GET to @url, if @token present use it
    return parsed response
    """
    headers = {}
    if token != None:
        headers = {'X-StorageApi-Token': token}
    response = http.request(url, 'GET', headers=headers)
    return parseResponse(response)

def postRequest(url, body, token, runId = None):
    """
    call POST to @url with @body and @token(optional)
    return parsed response
    """
    headers = {'X-Storageapi-Token': token}
    if runId:
        headers['X-KBC-RunId'] = runId
    headers['Content-Type'] = 'application/json; charset=UTF-8'
    body = json.dumps(body)
    response = http.request(url, 'POST', headers=headers, body=body)
    return parseResponse(response)

def getComponentUri(componentId):
    """
    retrieve component uri from the kbc index page by @componentId
    raise exception if not such component is present
    """
    body = loadConnectionIndex()['body']
    components = body['components']
    filtered = filter(lambda c: c['id'] == componentId, components)
    component = filtered[0] if len(filtered) > 0 else None
    if component == None:
        raise Exceptions.UploadException('Unknown component:{0}'.format(componentId))
    return component['uri']

def loadConnectionIndex():
    """
    return parsed response from GET kbc\index\storage
    """
    return getRequest(connectionIndexUrl, None)


def waitForAsyncJob(url, token):
    """
    every 5 seconds poll job @url until the job is finished
    return job detail
    """
    jobDetail = {}
    timeout = 5
    while jobDetail.get('isFinished', False) != True:
        jobDetail = getRequest(url, token)['body']
        time.sleep(timeout)
    return jobDetail


def runTask(componentId, params, token, runId = None):
    """
    run and poll async run job of a kbc component
    """
    componentUrl = "{0}/run".format(getComponentUri(componentId))
    response = postRequest(componentUrl, params, token, runId)
    jobDetail = response['body']
    jobId = jobDetail['id']
    debug('started upload to ', componentId, ' jobId: ', jobId)
    result = waitForAsyncJob(jobDetail['url'], token)
    if result['status'] != 'success':
        raise Exceptions.UploadException('Failed to upload file to ' + componentId + ' with jobId:' + str(jobId))
    debug('finished upload to ', componentId, ' jobId: ', jobId)
    return result
