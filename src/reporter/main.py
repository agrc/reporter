#!/usr/bin/env python
# * coding: utf8 *
"""
a description of what this module does.
this file is for testing linting...
"""

import logging
import sys
from pathlib import Path

from . import reports


def run_reports(logger):

    agol_out_path = Path(r'c:\temp\report_out_test.csv')

    reports_to_run = []
    reports_to_run.append(reports.AGOLUsageReport(logger, agol_out_path))

    for report in reports_to_run:
        data = report.create_report()
        report.save_report(data)


def main():

    cli_logger = logging.getLogger('reporter')
    cli_logger.setLevel(logging.INFO)
    detailed_formatter = logging.Formatter(
        fmt='%(levelname)-7s %(asctime)s %(module)10s:%(lineno)5s %(message)s', datefmt='%m-%d %H:%M:%S'
    )
    cli_handler = logging.StreamHandler(stream=sys.stdout)
    cli_handler.setLevel(logging.INFO)
    cli_handler.setFormatter(detailed_formatter)
    cli_logger.addHandler(cli_handler)

    run_reports(cli_logger)


if __name__ == '__main__':

    main()
