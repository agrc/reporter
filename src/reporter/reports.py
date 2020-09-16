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
        #: Log date
        timestamp = datetime.datetime.now()

        #: Get the column values from the keys of the first item and log as csv header
        columns = data[0].keys()
        # header = ','.join(columns)

        with open(self.out_path, 'w', newline='\n') as out_csv_file:
            out_writer = csv.writer(out_csv_file, delimiter=',')
            out_writer.writerow([timestamp])
            out_writer.writerow(columns)

            #TODO: finish
