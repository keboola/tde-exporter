import src
import sys
import pytest

def test_answer():
    assert 1 == 1

def tags():
    t = {'tags':['1','2']}
    return t

validColumnTypes = ['boolean', 'number', 'decimal', 'date', 'datetime', 'string']
def typedefs(sourceName):
    #generate all valid types with the same column name as the type
    columns = {}
    for idx,c in enumerate(validColumnTypes):
        columns['col' + str(idx)] = {'type': c}
    print columns
    return {'typedefs':
            {sourceName: columns }}

def tagsAndTypes(sourceName):
    a = tags().copy()
    a.update(typedefs(sourceName))
    return a

@pytest.fixture(params=[tags(), typedefs('test'), tagsAndTypes('test')])
def validConfig(request):
    config = { 'storage' :
        { 'input':{
            'tables': [{'source':'test'}]
        }
      },
               'parameters':request.param
    }
    return config


def test_configOK(validConfig):
    assert src.checkConfig(validConfig) == True
