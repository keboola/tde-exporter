import pytest
from src.upload import *
import csv
import random
import time
import os


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
   uri = getComponenUri(kbc_componentId)
   assert len(uri) > 1
