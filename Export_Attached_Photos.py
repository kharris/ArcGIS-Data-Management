import arcpy
from arcpy import da
import os

#Get the name of the feature class with attached photos and the location to save the photos as parameters
inTable = arcpy.GetParameterAsText(0)
fileLocation = arcpy.GetParameterAsText(1)

#Loop through each feature in the feature class and save the attached photo in the specified file
with da.SearchCursor(inTable, ['DATA', 'ATT_NAME', 'ATTACHMENTID']) as cursor:
    for item in cursor:
        attachment = item[0]
        filenum = "ATT" + str(item[2]) + "_"
        filename = str(item[1])
        open(fileLocation + os.sep + filename, 'wb').write(attachment.tobytes())
        del item
        del filenum
        del filename
        del attachment
