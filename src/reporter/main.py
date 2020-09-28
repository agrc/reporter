#!/usr/bin/env python
# * coding: utf8 *
"""
a description of what this module does.
this file is for testing linting...
"""

import datetime
import logging
import sys
from pathlib import Path

from . import reports

try:
    from . import credentials
except (ModuleNotFoundError, ImportError):
    from . import credentials_template as credentials


def run_reports(logger):
    """
    Main logic for instantiating report objects and running their methods.
    """

    now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    agol_out_path = Path(credentials.REPORT_DIR, 'AGOLUsage', f'AGOLReport_{now}.csv')

    reports_to_run = []
    reports_to_run.append(reports.AGOLUsageReport(logger, agol_out_path))

    for report in reports_to_run:
        data = report.create_report()
        report.save_report(data)


def main():
    """
    CLI entry point; sets up logger.
    """

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
