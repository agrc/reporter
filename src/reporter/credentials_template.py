"""
Secrets template file. Ensure real secrets file is excluded from git in .gitignore
"""

#: A URL for your AGOL org. e.g. https://utah.maps.arcgis.com
ORG = ''

USERNAME = ''
PASSWORD = ''

#: The full path to the AGOLItems table in SGID e.g. r'C:\temp\SGID.sde\TableName`
SGID_METATABLE = ''
#: The URL to the AGOLItems_shelved feature service layer e.g. https://server.com/arcgis/AGOLItems_shelved/FeatureServer/0
AGOL_METATABLE = ''

HFS_CREDITS_PER_MB = 0.24
DOLLARS_PER_CREDIT = 0.1

#: e.g. r'C:\temp'
REPORT_DIR = ''
