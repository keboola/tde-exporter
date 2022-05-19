import time
from kbc import postRequest, getRequest, getServiceUrl

QUEUE_URL = "https://queue{STACK}.keboola.com/jobs"

def runTaskQueueV2(componentId, params, token, runId):
    data = {
        "component": componentId,
        "mode": "run",
        "configData": params['configData']
    }

    jobDetail = postRequest(
        getServiceUrl(token, 'queue') + '/jobs', data, token, runId
    )

    attempt = 0
    finished = False
    while not finished:
        jobDetail = getRequest(jobDetail["body"]["url"], token)
        finished = jobDetail["body"]["isFinished"];
        ++attempt
        time.sleep(min(pow(2, attempt), 30))

    return jobDetail
