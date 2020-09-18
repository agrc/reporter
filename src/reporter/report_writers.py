"""
A module holding different functions for writing data. Each function can accept an arbitrary data structure holding
the data to be written.
"""

import csv
import datetime


def list_of_dicts_to_csv(data, out_path):
    """
    Writes data, a list of dicts with the same keys, to the csv file specified by out_path.

    Generates the header from the keys in the first dictionary in the list
    """

    timestamp = datetime.datetime.now()

    #: Get the column values from the keys of the first item
    columns = list(data[0].keys())

    with open(out_path, 'w', newline='\n') as out_csv_file:
        out_writer = csv.DictWriter(out_csv_file, fieldnames=columns, delimiter=',')
        out_writer.writerow({columns[0]: timestamp})  #: Puts timestamp as first item in csv
        out_writer.writeheader()
        for row in data:
            out_writer.writerow(row)
