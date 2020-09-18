"""
A module holding different functions for writing data. Each function can accept an arbitrary data structure holding
the data to be written.
"""

import csv
import datetime
import logging


def list_of_dicts_to_csv(data, out_path):
    """
    Writes data, a list of dicts with the same keys, to the csv file specified by out_path Path object.

    Generates the header from the keys in the first dictionary in the list
    """

    timestamp = datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')

    #: Get the column values from the keys of the first item
    columns = list(data[0].keys())

    with open(out_path, 'w', newline='\n') as out_csv_file:
        out_writer = csv.DictWriter(out_csv_file, fieldnames=columns, delimiter=',')
        out_writer.writerow({columns[0]: timestamp})  #: Puts timestamp as first item in csv
        out_writer.writeheader()
        for row in data:
            out_writer.writerow(row)


def list_of_dicts_to_rotating_logger(data, out_path, separator='|', rotate_count=18):
    """
    Logs a list of dictionaries with the same keys (obtained from the first dictionary in the list) to a rotating
    csv file via the logging module.

    data:           List of dictionaries that have the same keys. Reads the keys of the first dictionary to get the
                    column names.
    out_path:       Path object to the base report file. Automatically rotated by a logging RotatingFileHandler on each
                    call.
    separator:      The character used as a csv delimiter. Default to '|' to avoid common conflicts with text data.
    rotate_count:   The number of files to save before RotatingFileHandler deletes old reports. Defaults to 2.5 weeks
                    of daily reports.

    """
    #: Set up a rotating file handler for the report log
    report_logger = logging.getLogger('report_logger')
    report_handler = logging.handlers.RotatingFileHandler(out_path, backupCount=rotate_count)
    report_handler.doRollover()  #: Rotate the log on each run
    report_handler.setLevel(logging.INFO)
    report_logger.addHandler(report_handler)
    report_logger.setLevel(logging.INFO)

    #: Log date
    timestamp = datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
    report_logger.info(timestamp)

    #: Get the column values from the keys of the first dict and log as csv header
    columns = list(data[0].keys())
    header = separator.join(columns)
    report_logger.info(header)

    #: Iterate through the list, using the columns generated above to ensure the order stays the same for each row.
    for row in data:
        item_list = [str(row[col]) for col in columns]
        report_logger.info(separator.join(item_list))
