#-------------------------------------------------------------------------------
# Name:        Defining Natural Subregions of Forest Polygons
# Purpose:
#
# Author:      monica.wach
#
# Created:     05/02/2013
# Last Modified: 19/06/2013
# Copyright:   (c) monica.wach 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
try:
    import arcpy
except:
    import arcgisscripting
    arcpy = arcgisscripting.create()
from arcpy import env

# Set Workspace
env.workspace = ws = "e:/TimberNorth_data/for_Pat/script_practice.gdb"

# Allow for overwrite of previously written files
env.overwriteOutput = True

# Convert natsubreg from coverage to feature class
inFeature = "g:/00/alpac/overview/natsubreg/polygon"
outLocation = ws
arcpy.FeatureClassToFeatureClass_conversion(inFeature, outLocation,
                                            "natsubreg")

# Run an Identity on Forest
inFeature = "e:/TimberNorth_data/base_data_export.gdb/FOREST"
identFeature = "natsubreg"
arcpy.Identity_analysis(inFeature, identFeature, "FOREST_natsubreg")

# Run a Sort on FOREST_natsubreg
arcpy.Sort_management("FOREST_natsubreg", "FOREST_natsubreg_sort",
                      [["Shape_Area", "DESCENDING"]])

# Set local variables
inTable = "FOREST_natsubreg_sort"
fieldName = "duplicates"
expression = "isDuplicate(!Poly_num!)"
codeblock = """uniqueList[]
def isDuplicate(inValue):
    if inValue in uniqueList:
        return 1
    else:
        uniqueList.append(inValue)
        return 0"""

# Add a Field to the sorted table for identifying duplicates
arcpy.AddField_management(inTable, fieldName, "SHORT")

# Calculate the values for 'duplicates' field
arcpy.CalculateField_management(inTable, fieldName, expression,
                                "PYTHON_9.3", codeblock)

# Create update cursor for feature class
with arcpy.da.UpdateCursor(inTable, [fieldName]) as cursor:

# Select and delete all rows in "FOREST_natsubreg_sort" table
# identified with a 1 as duplicates
    for row in cursor:
        if row[0] == 1:
            cursor.deleteRow()

# Output table in a CSV file
def get_rows(inTable, fields):
   with da.SearchCursor(inTable, fields) as cursor:
      for row in cursor:
         yield row
if __name__ == "__main__":
   inTable = arcpy.GetParameterAsText(0) # feature class/Table
   Forest_NatSubReg = arcpy.GetParameterAsText(1) # csv file
   desc = arcpy.Describe(inTable)
   fieldnames = [f.name for f in desc.fields if f.type not in ["Geometry", "Raster", "Blob"]]
   rows = get_rows(inTable, fieldnames)
   with open(Forest_NatSubReg,'wb') as out_file:
      out_writer = csv.writer(out_file)
      out_writer.writerow(fieldnames)
      for row in rows:
         out_writer.writerow(row)