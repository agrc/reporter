#!/usr/bin/env python
# * coding: utf8 *
"""
a description of what this module does.
this file is for testing linting...
"""

import logging

from pathlib import Path

from . import reports


def run_reports(logger):

    agol_out_path = Path(r'c:\temp\report_out_test.csv')

    reports_to_run = []
    reports_to_run.append(reports.AGOLUsageReport(logger, agol_out_path))

    for report in reports_to_run:
        data = report.create_report()
        report.save_report(data)


if __name__ == '__main__':

    reporter_logger = logging.Logger('Reporter')

    run_reports(reporter_logger)
