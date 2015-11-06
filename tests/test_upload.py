import pytest
from src.upload import *
from src import Exceptions
import csv
import random
import time
import os
import json

def test_answer():
    assert 1 == 1

def test_loadIndex():
    index = loadConnectionIndex()
    header = index['header']
    status = header['status']
    assert status == '200'


@pytest.fixture(params=['wr-google-drive', 'wr-tableau-server', 'wr-dropbox'])
def kbc_componentId(request):
    return request.param

def test_getComponentUri(kbc_componentId):
   uri = getComponentUri(kbc_componentId)
   assert len(uri) > 1

def test_request500Fail():
    with pytest.raises(Exception) as exc:
        postRequest('www.asdasd.dd', {}, '')
    assert 'Error' in str(exc)

def test_request400Fail():
    with pytest.raises(Exceptions.UploadException) as exc:
        postRequest(connectionIndexUrl, {}, '')
    assert 'User error' in str(exc)

def test_uploadfail(kbc_componentId):
    params = {}
    token = ''
    with pytest.raises(Exceptions.UploadException) as exc:
        runTask(kbc_componentId, params, token)
    assert 'UploadException' in str(exc)

def test_runUnknownComponentFail():
    with pytest.raises(Exceptions.UploadException) as exc:
        runTask('asdasd', {}, '')
    assert 'Unknown component' in str(exc)


# def test_uploadtmp():
#     componentId = 'wr-dropbox'
#     params = json.loads('{"configData":{"storage":{"input":{"files":[{"query":"id:147088910"}]}},"parameters":{"credentials":"tde-exporter-test","mode":true}}}')
#     token = ''
#     result = runTask(componentId, params, token)
#     print result
#     assert 1 == 1
