#Description

TDE-exporter exports tables from KBC Storage into TDE file format([Tableau Data Extract](http://www.tableau.com/about/blog/2014/7/understanding-tableau-data-extracts-part1)).

User can run tde-exporter as any other keboola component or extractor etc., or register its run as **orchestration task**. After `\run` finishes, the resulting TDE files will be avaliable in *Storage->file uploads* section with URL to download.

TDE-exporter is [Keboola Docker component](https://github.com/keboola/docker-bundle) that supports [custom configuration](http://docs.kebooladocker.apiary.io/#reference/run/create-a-job/custom-configuration) for `\run` API call described as follows:

# Configuration

`\run` API call:

POST  `https://syrup.keboola.com/docker/tde-exporter/run`


request body(config JSON):

`
{
    "configData": {
        "storage": {
            "input": {
                "tables": [
                    {  "source": "in.c-ex-dummy.dummy" }
                ]
            }
        },
          "parameters":{
           "tags":["sometag"],
           "typedefs":{
            "in.c-ex-dummy.dummy":{
                   "id":{"type":"number"},
                            "col1": {"type":"string"}
        }}}}}
`
## Input tables:
Specified in request body in `configData:storage:input:tables` as array of `{"source":<tableid>}`. It can be customized(e.g. only specific columns or values) as described in [Keboola Docker Input Mapping](https://github.com/keboola/docker-bundle/blob/master/ENVIRONMENT.md#input-mapping)
## Parameters:
Another part for request body as `configData:parameters` JSON object, contains:

* tags: array of tags that will be assigned to the resulting file in sapi file uploads
* typedefs: defines datatypes mapping of source tables columns to destination TDE columns:  `<table_id(must match source from input tables)>: {<column_name>:{type:<column_type>}...}` 

e.g:
`"in.c-ex-dummy.dummy":{
                   "id":{"type":"number"},
                            "col1": {"type":"string"}
        }`


##supported column data types
    'boolean', 'number', 'decimal','date', 'datetime', 'string'.

### Date and Datetime column data types specification
Data for these datatypes can be specified in format described in [strptime function](http://pubs.opengroup.org/onlinepubs/009695399/functions/strptime.html).  Format can be specified in *typedefs* column definition e.g. `{"col1":{"type":"date", "format":"%m-%d-%Y"}}`. If no format is specified then default formats is used:

* **date** default format: `%Y-%m-%d`
* **datetime** default format: `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d %H:%M:%S.%f`
