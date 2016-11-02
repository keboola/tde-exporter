import pytest
from src.main import uploadFiles
from src.main import emptydir
from src.uploadTasks import runUploadTasks
from src.kbc import *
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

def test_uploadfailRunId(kbc_componentId):
    params = {}
    token = ''
    with pytest.raises(Exceptions.UploadException) as exc:
        runTask(kbc_componentId, params, token, 'testrunid')
    assert 'UploadException' in str(exc)


def test_runUnknownComponentFail():
    with pytest.raises(Exceptions.UploadException) as exc:
        runTask('asdasd', {}, '')
    assert 'Unknown component' in str(exc)

def test_phpUploadEmptyFiles(tmpdir):
    sourceFolder = str(tmpdir.mkdir("tde-files").realpath())

    assert uploadFiles(sourceFolder, 'asdasd', 'asd') == True
    assert uploadFiles(sourceFolder, 'asdasd', None) == True
    os.mknod(sourceFolder + "/newfile.tde")
    os.mknod(sourceFolder + "/newfile.manifest")
    assert emptydir(sourceFolder) == True
    assert os.path.exists(sourceFolder) == False

    # with pytest.raises(Exception) as exc:
    #     uploadFiles('asdasd', 'asd')
    # assert 'Error uploading files' in str(exc)
    # with pytest.raises(Exception) as exc2:
    #     uploadFiles('asdasd', None)
    # assert 'Error uploading files' in str(exc2)



# def test_uploadtmp():
#     componentId = 'wr-dropbox'
#     params = json.loads('{"configData":{"storage":{"input":{"files":[{"query":"id:147088910"}]}},"parameters":{"credentials":"tde-exporter-test","mode":true}}}')
#     token = ''
#     result = runTask(componentId, params, token)
#     print result
#     assert 1 == 1



def test_emptyUploadTasks():
    config1 = {
        'parameters' : {}
    }
    config2 = {
        'parameters':{
            'uploadTasks': []
        }
    }
    token = '123'
    runId = 'runid'
    runUploadTasks(config1, token, runId)
    runUploadTasks(config2, token, runId)
    assert 1 == 1
