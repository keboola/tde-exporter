from Exceptions import UploadException
from kbc import runTask

componentIdMap = {
    'tableauServer': 'wr-tableau-server',
    'dropbox': 'wr-dropbox',
    'gdrive': 'wr-google-drive'
}

def getParameters(config, path):
    try:
        return reduce(lambda d, k: d[k], ['parameters'] + path, config)
    except:
        return None

def generateTaskRunParameters(componentId, credentials):
    storage = {
        "input": {
            "files": [
                {
                    "filter_by_run_id": True,
                    "tags": ['tde']
                }
            ]
        }
    }

    paramsMap = {
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
              'query': "+tags:tde +tags:table-export",
                'filterByRunId': True,
                'targetFolder': credentials.get('targetFolder')
            }
      }
    }
    return paramsMap[componentId]




def runUploadTasks(config, token):
    """
    For all @components from @config:params:uploadTasks call \run with token and runId
    that takes all files filtered by this job runId
    """
    components = getParameters(config, ['uploadTasks'])
    if components == None:
        return
    if not isinstance(components, list):
        raise UploadException(component + ' not found')

    for component in components:
        componentId = componentIdMap.get(component)
        if not componentId:
            raise UploadException(component + ' not found')
        #take saved credentials object
        credentials = getParameters(config, [component])
        params = generateTaskRunParameters(componentId, credentials)
        runTask(componentId, params, token)

   #for each component in config:parameters:uploadTasks
   #  generate run params for upload of files filtered by runId
   #
