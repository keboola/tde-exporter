# TDE Exporter

## Description

TDE-exporter exports tables from KBC Storage into TDE file format([Tableau Data Extract](http://www.tableau.com/about/blog/2014/7/understanding-tableau-data-extracts-part1)).

User can run tde-exporter as any other keboola component or extractor etc., or register its run as **orchestration task**. After `\run` finishes, the resulting TDE files will be avaliable in *Storage->file uploads* section with URL to download.

## Tagging
The resulting file is always tagged by **default tags** `tde` and `table-export`, if the job proccess contains `runId` then the file is also tagged by runId in format `runId-<runid>`. If the runid is composed(eg 1234.9999) the only so called `orchestrator part`(before dot) is taken as runId tag value(e.g. from former case it would be: `runId-1234`). Configuration also allows append of custom tags along with default tags and runid tag(if present), see Configuration->Parameters->Tags.

## Empty Values
TDE-exporter handles empty(or null) values as valid `TDE specific null values` except for **string** data types where the actual empty value `""` is used. No error will ever be raised.


# Configuration
TDE-exporter is [Keboola Docker component](https://github.com/keboola/docker-bundle) that supports [custom configuration](http://docs.kebooladocker.apiary.io/#reference/run/create-a-job/custom-configuration) for `\run` API call described as follows:

`\run` API call:

POST  `https://syrup.keboola.com/docker/tde-exporter/run`


request body(config JSON):

```
{
  "configData": {
    "storage": {
      "input": {
        "tables": [
          {
            "source": "in.c-ex-dummy.dummy"
          }
        ]
      }
    },
    "parameters": {
      "tags": [
        "sometag"
      ],
      "typedefs": {
        "in.c-ex-dummy.dummy": {
          "id": {
            "type": "number"
          },
          "col1": {
            "type": "string"
          }
        }
      }
      "tables": {
        "in.c-ex-dummy.dummy": {
          "tdename": "customdummyname"
        }
      }
    }
  }
}
```
## Input tables:
Specified in request body in `configData:storage:input:tables` as array of `{"source":<tableid>}`. It can be customized(e.g. only specific columns or values) as described in [Keboola Docker Input Mapping](https://github.com/keboola/docker-bundle/blob/master/ENVIRONMENT.md#input-mapping)
## Parameters:
Another part for request body as `configData:parameters` JSON object, contains:

* tags: array of tags that will be assigned to the resulting file in sapi file uploads.
* typedefs: defines datatypes mapping of source tables columns to destination TDE columns:  `<table_id(must match source from input tables)>: {<column_name>:{type:<column_type>}...}`

e.g:
`"in.c-ex-dummy.dummy":{
                   "id":{"type":"number"},
                            "col1": {"type":"string"}
        }`


##supported column data types
    'boolean', 'number', 'decimal','date', 'datetime', 'string'.
### Custom TDE file Names
 Output TDE files can have custom names. To specify a custom name(customdummyname) for a table with tableId(in.c-ex-dummy.dummy) in input mapping sources, provide mapping structure in parameters property as follows:
```
      "tables": {
        "in.c-ex-dummy.dummy": {
          "tdename": "customdummyname"
        }
      }
```
.tde extension does not have to be supplied, if it is missing it will be appended automatically so for the example above the output TDE file name will be `customdummyname.tde`. The file name can contain up to maximumm **150 characters**(including .tde extension) and can contain alphanumeric characters, space, dot and '(' ')' '_' '-'.

### Date and Datetime column data types specification
Data for these datatypes can be specified in format described in [strptime function](http://pubs.opengroup.org/onlinepubs/009695399/functions/strptime.html).  Format can be specified in *typedefs* column definition e.g. `{"col1":{"type":"date", "format":"%m-%d-%Y"}}`. If no format is specified then default formats is used:

* **date** default format: `%Y-%m-%d`
* **datetime** default format: `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d %H:%M:%S.%f`
