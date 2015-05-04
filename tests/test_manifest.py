import pytest
import src
import csv
import random
import time
import os
import yaml

def test_answer():
    assert 1 == 1

@pytest.fixture(params=[[],['tde'], ['sometag'], ['tde','sometag']])
def validTags(request):
    return request.param

@pytest.fixture (params=[["",""], [None, ""], ["runid", "runid"], ["runid.blabla", "runid"]])
def run_ids(request):
    runid = request.param[0]
    expected = request.param[1]
    if runid:
        os.environ['KBC_RUNID'] = runid
    return expected


def test_manifest(tmpdir, validTags, run_ids):
    outFileName = 'test_manifest'
    outFilePath = str(tmpdir.join(outFileName).realpath())
    tags = validTags
    src.createManifest(outFilePath, outFileName, tags)
    manifest =  yaml.load(open(outFilePath + '.manifest', 'r'))
    assert manifest['is_permanent'] ==  True
    assert manifest['is_public'] ==  False
    assert manifest ['is_encrypted'] == True
    #assert that each tag is in manifest->tags exactly once
    for tag in tags:
        assert manifest['tags'].count(tag) == 1
    assert type(manifest['tags']) == type([])
    if run_ids:
        assert manifest['tags'].count('runId-' + run_ids) == 1
