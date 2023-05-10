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
from urlparse import urljoin

connectionIndexUrl = urljoin(os.environ['KBC_URL'], '/v2/storage')
http = httplib2.Http()

def getProjectFeatures(token):
    verifyToken = getRequest(connectionIndexUrl + '/tokens/verify', token)
    return verifyToken['body']['owner']['features']

def getServiceUrl(token, serviceId):
    verifyToken = getRequest(connectionIndexUrl, token)
    services = verifyToken["body"]['services']

    for service in services:
        if service['id'] == serviceId:
            return service['url']

    raise Exceptions('Unknown service id ' + serviceId)

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

def loadConnectionIndex():
    """
    return parsed response from GET kbc\index\storage
    """
    return getRequest(connectionIndexUrl, None)


def getRequest(url, token):
    """
    call a GET to @url, if @token present use it
    return parsed response
    """
    headers = {}
    if token != None:
        headers = {'X-StorageApi-Token': token}

    upload_max_retries = 5
    upload_retries = 0
    while upload_retries < upload_max_retries:
        upload_retries += 1
        try:
            response = http.request(url, 'GET', headers=headers)
            return parseResponse(response)
        except Exceptions.UploadException as upload_err:
            raise Exceptions.UploadException(str(upload_err))
        except Exception as err:
            if upload_retries < upload_max_retries:
                message = '%s Retrying upload' % (
                    str(upload_retries)
                )
                print(message)
                continue
            message = 'Error with %s retrying: %s' % (
               upload_retries,
               str(err)
            )
            raise Exception(message)

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
    upload_max_retries = 5
    upload_retries = 0
    while upload_retries < upload_max_retries:
        upload_retries += 1
        try:
            response = http.request(url, 'POST', headers=headers, body=body)
            return parseResponse(response)
        except Exceptions.UploadException as upload_err:
            raise Exceptions.UploadException(str(upload_err))
        except Exception as err:
            if upload_retries < upload_max_retries:
                message = '%s Retrying upload' % (
                    str(upload_retries)
                )
                print(message)
                continue
            message = 'Error with %s retrying: %s' % (
                upload_retries,
                str(err)
            )
            raise Exception(message)
