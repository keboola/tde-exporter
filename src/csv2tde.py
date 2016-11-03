import sys
import csv
import time
import datetime
import locale
import array
import re
import ConfigParser
import os

# Import Tableau module
from dataextract import *
TDE_RESET_THRESHOLD = 100000
colNames = [] #typedefs.keys()
colTypes = []
colDefs = [] #contains definition object for each column
def getColumnDefinition(colName, typedefs):
    if colName in typedefs:
        return typedefs[colName]
    else:
        return {'type': Type.UNICODE_STRING}

def getColumnType(colName, typedefs):
    if colName in typedefs:
        return schemaIniTypeMap[typedefs[colName]['type'].lower()]
    else:
        return Type.UNICODE_STRING


# Define type maps
schemaIniTypeMap = {
    'boolean':  Type.BOOLEAN,
    'number':   Type.INTEGER,
    'decimal':  Type.DOUBLE,
    'date':     Type.DATE,
    'datetime': Type.DATETIME,
    'string':   Type.UNICODE_STRING,
}

def setDate(row, colNo, value, colDef) :
        format = "%Y-%m-%d"
        if 'format' in colDef:
                format = colDef['format']
        d = datetime.datetime.strptime(value, format)
        row.setDate( colNo, d.year, d.month, d.day )

def setDateTime(row, colNo, value, colDef) :
        format = "%Y-%m-%d %H:%M:%S"
        if( value.find(".") != -1) :
                format = "%Y-%m-%d %H:%M:%S.%f"
        if 'format' in colDef:
                format = colDef['format']
        d = datetime.datetime.strptime(value, format)
        row.setDateTime( colNo, d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond/100 )

fieldSetterMap = {
        Type.BOOLEAN:        lambda row, colNo, value, colDef: row.setBoolean( colNo, value.lower() == "true" ),
        Type.INTEGER:        lambda row, colNo, value, colDef: row.setInteger( colNo, int(value) ),
        Type.DOUBLE:         lambda row, colNo, value, colDef: row.setDouble( colNo, float(value) ),
        Type.UNICODE_STRING: lambda row, colNo, value, colDef: row.setString( colNo, value.decode('utf-8') ),
        Type.CHAR_STRING:    lambda row, colNo, value, colDef: row.setCharString( colNo, value ),
        Type.DATE:           lambda row, colNo, value, colDef: setDate(row, colNo, value, colDef),
        Type.DATETIME:       lambda row, colNo, value, colDef: setDateTime( row, colNo, value, colDef )
}
# Define createTable function
def createTable(line, extract, typedefs, isFirstCreation):
    if line:
        # append with empty columns so we have the same number of columns as the header row
        while len(colNames) < len(line):
            colDefs.append(None)
            colNames.append(None)
            colTypes.append(Type.UNICODE_STRING)
        # write in the column names from the header row
        colNo = 0
        for colName in line:
            colNames[colNo] = colName
            #print "coltype for ", colName, 'is ', getColumnType(colName)
            colTypes[colNo] = getColumnType(colName, typedefs)
            colDefs[colNo] = getColumnDefinition(colName, typedefs)
            colNo += 1

    # for any unnamed column, provide a default
    for i in range(0, len(colNames)):
        if colNames[i] is None:
            colNames[i] = 'F' + str(i + 1)

    # create the schema and the table from it
    tableDef = TableDefinition()
    for i in range(0, len(colNames)):
        tableDef.addColumn( colNames[i], colTypes[i] )
    tableName = "Extract"
    table = None
    if extract.hasTable(tableName) and not isFirstCreation:
            table = extract.openTable(tableName)
    else:
            table = extract.addTable( tableName, tableDef )
    return table, tableDef

def convert(csvReader, tdeFile, typedefs) :
    hasHeader = True
    global colNames
    global colTypes
    global colDefs

    colNames = [] #typedefs.keys()
    colTypes = []
    colDefs = [] #contains definition object for each column

    locale.setlocale(locale.LC_ALL, '')
    print "Creating extract:", tdeFile
    # Read the table
    rowNo = 0
    csvHeader = None
    extract = Extract(tdeFile)
    table = None  # set by createTable
    tableDef = None

    for line in csvReader:
        # Create the table upon first row (which may be a header)
        if rowNo == 0:
            csvHeader = line
            table, tableDef = createTable( csvHeader if hasHeader else None , extract, typedefs, True)
            if hasHeader:
                rowNo +=1
                continue
        # We have a table, now write a row of values
        row = Row(tableDef)
        colNo = 0
        for field in line:
            if( colTypes[colNo] != Type.UNICODE_STRING and field == "" ) :
                row.setNull( colNo )
            else :
                fieldSetterMap[colTypes[colNo]](row, colNo, field, colDefs[colNo]);
            colNo += 1

        table.insert(row)

        # Output progress line
        rowNo += 1
        if rowNo % TDE_RESET_THRESHOLD == 0:
            extract.close()
            extract = Extract(tdeFile)
            table, tableDef = createTable( csvHeader if hasHeader else None , extract, typedefs, False)
            print locale.format("%d", rowNo, grouping=True), "rows inserted",
    # END OF FOR CYCLE

    # close the extract if we didnt reach the closing row
    if rowNo % TDE_RESET_THRESHOLD != 0:
        extract.close()
