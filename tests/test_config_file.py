import json
import os

import pytest
import yaml

import src

CONFIG = {
    'storage': {'input': {'tables': [{'source': 'in.c-main.table', 'columns': ['id', 'name']}]}},
    'parameters': {
        'tags': ['sometag'],
        'tables': {'in.c-main.table': {'tdename': 'table.tde'}},
        'typedefs': {'in.c-main.table': {'id': {'type': 'number', 'format': None}}},
    },
}


def writeJson(dataDir, config):
    with open(os.path.join(dataDir, 'config.json'), 'w') as f:
        json.dump(config, f)


def writeYaml(dataDir, config):
    with open(os.path.join(dataDir, 'config.yml'), 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False)


def test_json_and_yaml_load_identically(tmpdir):
    jsonDir = tmpdir.mkdir('json')
    yamlDir = tmpdir.mkdir('yaml')
    writeJson(str(jsonDir), CONFIG)
    writeYaml(str(yamlDir), CONFIG)

    fromJson = src.loadConfigFile(str(jsonDir))
    fromYaml = src.loadConfigFile(str(yamlDir))

    assert fromJson == fromYaml
    assert type(fromJson['parameters']['tags'][0]) is type(fromYaml['parameters']['tags'][0])


def test_json_wins_over_yaml(tmpdir):
    writeJson(str(tmpdir), CONFIG)
    writeYaml(str(tmpdir), {'storage': {'input': {'tables': []}}})

    assert src.loadConfigFile(str(tmpdir))['parameters']['tags'] == ['sometag']


def test_missing_config_fails(tmpdir):
    with pytest.raises(IOError):
        src.loadConfigFile(str(tmpdir))


def test_non_ascii_values_stay_unicode(tmpdir):
    writeJson(str(tmpdir), {'parameters': {'tags': [u'\u010dlen']}})

    assert src.loadConfigFile(str(tmpdir))['parameters']['tags'] == [u'\u010dlen']


def test_manifest_from_json_config_is_plain_yaml(tmpdir):
    writeJson(str(tmpdir), CONFIG)
    config = src.loadConfigFile(str(tmpdir))
    outFilePath = str(tmpdir.join('table.tde'))

    src.createManifest(outFilePath, 'table.tde', config['parameters']['tags'])

    with open(outFilePath + '.manifest') as f:
        content = f.read()
    assert '!!python' not in content
    assert 'sometag' in yaml.safe_load(content)['tags']
