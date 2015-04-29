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


def test_manifest(tmpdir, validTags):
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
