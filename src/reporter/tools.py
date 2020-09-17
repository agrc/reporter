"""
Classes that do all the heavy lifting
"""

import datetime
import uuid
from collections import namedtuple

import arcgis

import arcpy

from . import credentials


class Organization:
    """
    An ArcGIS Online organization gis object and all the operations performed through it
    """

    def __init__(self, logger, org, username, password):

        self.logger = logger
        self.logger.info('==========')
        self.logger.info(f'Portal: {org}')
        self.logger.info(f'User: {username}')
        self.logger.info('==========')

        self.gis = arcgis.gis.GIS(org, username, password)
        self.user_item = self.gis.users.me  # pylint: disable=no-member

    def get_users_folders(self):
        """Get all the Feature Service item objects in the user's folders"""

        #: Build list of folders. 'None' gives us the root folder.
        self.logger.info(f'Getting {self.user_item.username}\'s folders...')
        folders = [None]
        for folder in self.user_item.folders:
            folders.append(folder['title'])

        return folders

    def get_feature_services_in_folders(self, folders):
        """
        Get info for every item in every folder

        Returns a list of tuples: [(item_object, folder_name), ... ]
        """

        feature_service_items = []

        self.logger.info('Getting item objects...')
        for folder in folders:
            for item in self.user_item.items(folder, 1000):
                if item.type == 'Feature Service':
                    feature_service_items.append((item, folder))

        return feature_service_items

    def get_open_data_groups(self):
        """
        Returns a list of the organization's groups that are enabled for Open Data
        """
        self.logger.info('Getting Open Data groups...')
        open_data_groups = []
        org_groups = self.gis.groups.search()  # pylint: disable=no-member
        for group in org_groups:
            if 'isOepnData' in group and group.isOpenData:
                open_data_groups.append(group.title)

        return open_data_groups

    def get_item_info(self, item, open_data_groups, folder, metatable_row):
        """
        Given an item object and a string representing the name of the folder it
        resides in, item_info builds a dictionary containing pertinent info about
        that item.
        """
        self.logger.info(f'Getting info for {item.title}...')
        item_dict = {}
        item_dict['itemid'] = item.itemid
        item_dict['title'] = item.title
        item_dict['owner'] = item.owner
        if folder:
            item_dict['folder'] = folder
        else:
            item_dict['folder'] = '_root'
        item_dict['views'] = item.numViews
        item_dict['modified'] = datetime.datetime.fromtimestamp(item.modified / 1000).strftime('%Y-%m-%d %H:%M:%S')
        item_dict['authoritative'] = item.content_status

        #: Sometimes we get a permission denied error on group listing, so we wrap
        #: it in a try/except to keep moving
        group_names = []
        try:
            for group in item.shared_with['groups']:
                group_names.append(group.title)
            groups = ', '.join(group_names)
        except:  # pylint: disable=bare-except
            groups = 'error'
        item_dict['groups'] = groups

        #: Check if any of the item's groups are enabled for Open Data
        is_open_data = False
        for group in group_names:
            if group in open_data_groups:
                is_open_data = True
                break
        if groups == 'error':
            item_dict['open_data_group'] = 'group error'
        else:
            item_dict['open_data_group'] = str(is_open_data)

        #: Item is part of SGID if its metatable group is not "shelved"
        item_dict['in_sgid'] = 'True'
        if metatable_row.category == 'shelved':
            item_dict['in_sgid'] = 'False'

        item_dict['tags'] = ', '.join(item.tags)
        size_in_mb = item.size / 1024 / 1024
        item_dict['sizeMB'] = size_in_mb
        item_dict['credits'] = size_in_mb * credentials.HFS_CREDITS_PER_MB
        item_dict['cost'] = size_in_mb * credentials.HFS_CREDITS_PER_MB * credentials.DOLLARS_PER_CREDIT

        #: Sometimes data usage also gives an error, so try/except that as well
        try:
            item_dict['data_requests_1Y'] = int(item.usage('1Y').sum())
        except:  # pylint: disable=bare-except
            item_dict['data_requests_1Y'] = 'error'

        return item_dict


class Metatable:
    """
    Represents the metatable containing information about SGID items uploaded to AGOL.
    read_metatable() can be called on both the SGID AGOLItems table or the AGOL-hosted AGOLItems_Shelved table.
    Table stored as namedtuples in self.metatable_dict using the itemid as the key:
        {item_id: [sgid_name, agol_name, category, authoritative]}
    Any duplicate item ids (either a table has the same AGOL item in more than one row, or the item id exists in
    multiple tables) are added to the self.duplicate_keys list.
    """

    def __init__(self, logger):
        #: A dictionary of the metatable records, indexed by the metatable's itemid
        #: values: {item_id: [sgid_name, agol_name, category, authoritative]}
        self.metatable_dict = {}
        self.duplicate_keys = []

        self.logger = logger

    def read_metatable(self, table, fields):
        """
        Read metatable 'table' into self.metatable_dict. Any duplicate Item IDs are added to self.duplicate_keys.

        table:      Path to a table readable by arcpy.da.SearchCursor
        fields:     List of fields names to access in the table.
        """

        self.logger.info(f'Reading in {table}...')

        MetatableRow = namedtuple('MetatableRow', ['sgid_name', 'agol_name', 'category', 'authoritative'])

        for row in self._cursor_wrapper(table, fields):

            #: If table is from SGID, get "authoritative" from table and set "category" to SGID. Otherwise,
            #: get "category" from table and set "authoritative" to 'n'.
            #: SGID's AGOLItems table has "Authoritative" field, shelved table does not.
            if 'Authoritative' in fields:
                table_sgid_name, table_agol_itemid, table_agol_name, table_authoritative = row
                table_category = 'SGID'
            else:
                table_sgid_name, table_agol_itemid, table_agol_name, table_category = row
                table_authoritative = 'n'

            #: Item IDs are UUIDs. If we can't parse the item id listed in the table, it means the layer is not
            #: in AGOL and this row should be skipped (catches both magic words and empty entries)
            try:
                uuid.UUID(table_agol_itemid)
            except (AttributeError, ValueError, TypeError):
                continue

            if table_agol_itemid not in self.metatable_dict:
                self.metatable_dict[table_agol_itemid] = MetatableRow(
                    table_sgid_name,
                    table_agol_name,
                    table_category,
                    table_authoritative,
                )
            else:
                self.duplicate_keys.append(table_agol_itemid)

    def _cursor_wrapper(self, table, fields):
        """
        Wrapper for arcpy.da.SearchCursor so that it can be Mocked out in testing.

        table:      Path to a table readable by arcpy.da.SearchCursor
        fields:     List of fields names to access in the table.
        """

        with arcpy.da.SearchCursor(table, fields) as search_cursor:
            for row in search_cursor:
                yield row
