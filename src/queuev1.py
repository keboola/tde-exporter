"""
wraps keboola connection api
runs and polls kbc components jobs
"""
import httplib2 # pip install httplib2
import time
import os
import Exceptions
from logger import debug
from kbc import postRequest, getRequest, loadConnectionIndex

connectionIndexUrl = os.environ['KBC_URL'] + '/v2/storage'
http = httplib2.Http()


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


def runTaskQueueV1(componentId, params, token, runId = None):
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
