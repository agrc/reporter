"""
Report base class and the actual report classes that inherit from it. Each class should implement a create_report
and a save_report method.
"""

import csv
import datetime

from reporter import credentials

from . import tools


class Report:
    """
    Base class from which other reports should inherit
    """

    def __init__(self, logger, out_path):
        self.logger = logger
        self.out_path = out_path

    def create_report(self):
        """
        Return the report results in some form of data structure.
        """
        # self.logger.info('create_report not implemented')
        raise NotImplementedError('create_report not implemented')

    def save_report(self, data):
        """
        Write the information in 'data' to the Report's out_path.
        """
        # self.logger.info('save_report not implemented')
        raise NotImplementedError('save_report not implemented')


class AGOLUsageReport(Report):
    """
    Reports usage of AGOL Hosted Feature Services. Relies on SGID and AGOL metatables to determine whether item is
    considered part of the SGID.
    """

    def __init__(self, logger, out_path):
        super().__init__(logger, out_path)

    def create_report(self):
        """
        Returns a list of dicts whose keys are column headings and values are the column values:
        [{itemid: 'some_uuid', title: 'AGOL title', ...} ...]
        """
        self.logger.info('Creating AGOL Usage Report...')
        item_info_dicts = []

        org = tools.Organization(self.logger, credentials.ORG, credentials.USERNAME, credentials.PASSWORD)
        folders = org.get_users_folders()
        items = org.get_feature_services_in_folders(folders)
        open_data_groups = org.get_open_data_groups()

        metatable = tools.Metatable(self.logger)
        sgid_fields = ['TABLENAME', 'AGOL_ITEM_ID', 'AGOL_PUBLISHED_NAME', 'Authoritative']
        agol_fields = ['TABLENAME', 'AGOL_ITEM_ID', 'AGOL_PUBLISHED_NAME', 'CATEGORY']
        metatable.read_metatable(credentials.SGID_METATABLE, sgid_fields)
        metatable.read_metatable(credentials.AGOL_METATABLE, agol_fields)

        for item_tuple in items:
            item, folder = item_tuple
            metatable_category = None
            if item.itemid in metatable.metatable_dict:
                metatable_category = metatable.metatable_dict[item.itemid].category
            item_info_dicts.append(org.get_item_info(item, open_data_groups, folder, metatable_category))

        return item_info_dicts

    def save_report(self, data):
        """
        Saves agol usage info contained in data to the object's out_path. The keys of the first value are used as
        the csv file's schema.
        """
        self.logger.info(f'Saving AGOL Usage Report to {self.out_path}...')
        timestamp = datetime.datetime.now()

        #: Get the column values from the keys of the first item
        columns = list(data[0].keys())

        with open(self.out_path, 'w', newline='\n') as out_csv_file:
            out_writer = csv.DictWriter(out_csv_file, fieldnames=columns, delimiter=',')
            out_writer.writerow({columns[0]: timestamp})  #: Puts timestamp as first item in csv
            out_writer.writeheader()
            for row in data:
                out_writer.writerow(row)
