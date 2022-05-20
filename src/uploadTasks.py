from Exceptions import UploadException
from kbc import getProjectFeatures
from queuev1 import runTaskQueueV1
from queuev2 import runTaskQueueV2
import copy

componentIdMap = {
    'tableauServer': 'wr-tableau-server',
    'dropbox': 'wr-dropbox',
    'gdrive': 'wr-google-drive',
    'keboola.wr-dropbox-v2': 'keboola.wr-dropbox-v2',
    'keboola.wr-google-drive': 'keboola.wr-google-drive'

}

def getParameters(config, path):
    """
    return object defined by @path(list) from parameters object of the given config
    """
    try:
        return reduce(lambda d, k: d[k], ['parameters'] + path, config)
    except:
        return None

def generateTaskRunParameters(componentId, credentials):
    """
    return object that will be passed as params to \run api call
    should configure the component to take all uploaded files shared with current parent runId
    """
    storage = {
        "input": {
            "files": [
                {
                    "filter_by_run_id": True,
                    "tags": ['tde'],
                    "limit": 100
                }
            ]
        }
    }

    credentialsOnly = copy.deepcopy(credentials)
    credentialsOnly.pop('folder', None)
    credentialsOnly.pop('targetFolder', None)

    paramsMap = {
      'keboola.wr-google-drive':
        {
          'configData':
            {
              'authorization': {'oauth_api': credentialsOnly},
              'storage': storage,
              'parameters': {'files': {'folder': credentials.get('folder')}}
            }
      },
      'keboola.wr-dropbox-v2':
        {
          'configData':
            {
              'authorization': {'oauth_api': credentialsOnly},
              'storage': storage,
              'parameters': {'mode': 'rewrite'}
            }
      },
      'wr-tableau-server':
        {
          'configData':
            {
              'storage': storage,
              'parameters': credentials
            }
      },
      'wr-dropbox':
        {
          'configData':
            {
                'storage': storage,
                'parameters':
                {
                    'mode': True, #rewrite files in destination
                    'credentials': credentials.get('id')
                }
          }
      },
      'wr-google-drive':
        {
          'external':
            {
              'account':
                {
                    'email': credentials.get('email'),
                    'accessToken': credentials.get('accessToken'),
                    'refreshToken': credentials.get('refreshToken')

                },
              'targetFolder': credentials.get('targetFolder'),
              'query': "+tags:tde +tags:table-export",
              'filterByRunId': True
            }
      }
    }
    return paramsMap[componentId]




def runUploadTasks(config, token, runId):
    """
    For all @components from @config:params:uploadTasks call \run with token
    that takes all files filtered by parent job runId
    """
    components = getParameters(config, ['uploadTasks'])
    if (not components) or components is None:
        return
    # if not isinstance(components, list):
    #     raise UploadException(component + ' not found')

    for component in components:
        componentId = componentIdMap.get(component)
        if not componentId:
            raise UploadException(component + ' not found')
        #take saved credentials object
        credentials = getParameters(config, [component])
        params = generateTaskRunParameters(componentId, credentials)

        features = getProjectFeatures(token)
        if "queuev2" in features:
            runTaskQueueV2(componentId, params, token, runId)
        else:
            runTaskQueueV1(componentId, params, token, runId)
