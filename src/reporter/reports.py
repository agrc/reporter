"""
Report base class and the actual report classes that inherit from it. Each class should implement a create_report
and a save_report method.
"""

from . import credentials, report_writers, tools


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

        raise NotImplementedError('create_report not implemented')

    def save_report(self, data):
        """
        Write the information in 'data' to the Report's out_path.
        """

        raise NotImplementedError('save_report not implemented')


class AGOLUsageReport(Report):
    """
    Reports usage of AGOL Hosted Feature Services. Relies on SGID and AGOL metatables to determine whether item is
    considered part of the SGID.
    """

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

        report_writers.list_of_dicts_to_csv(data, self.out_path)
