"""
Report base class and the actual report classes that inherit from it. Each class should implement a create_report and a save_report method.
"""

import csv
import datetime

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
        self.logger.info('create_report not implemented')

    def save_report(self, data):
        """
        Write the information in 'data' to the Report's out_path.
        """
        self.logger.info('save_report not implemented')


class AGOLUsageReport(Report):

    def __init__(self, logger, out_path):
        super().__init__(logger, out_path)

    def create_report(self):
        """
        Returns a list of dicts whose keys are column headings and values are the column values:
        [{itemid: 'some_uuid', title: 'AGOL title', ...} ...]
        """
        item_info_dicts = []

        org = tools.Organization(self.logger)
        folders = org.get_users_folders()
        items = org.get_feature_services_in_folders(folders)

        for item_tuple in items:
            item, folder = item_tuple
            item_info_dicts.append(org.get_item_info(item, folder))

        return item_info_dicts

    def save_report(self, data):
        """
        Saves agol usage info contained in data to the object's out_path. The keys of the first value are used as
        the csv file's schema.
        """
        timestamp = datetime.datetime.now()

        #: Get the column values from the keys of the first item
        columns = list(data[0].keys())

        with open(self.out_path, 'w', newline='\n') as out_csv_file:
            out_writer = csv.DictWriter(out_csv_file, fieldnames=columns, delimiter=',')
            out_writer.writerow({columns[0]: timestamp})  #: Puts timestamp as first item in csv
            out_writer.writeheader()
            for row in data:
                out_writer.writerow(row)
