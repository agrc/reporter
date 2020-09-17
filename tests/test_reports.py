from reporter import reports


def test_AGOL_save_report_gets_columns_right(mocker, tmp_path):
    test_data = [{'foo': 1, 'bar': 2}, {'bar': 4, 'foo': 3}]
    out_path = tmp_path / 'test.csv'
    # mocker.patch('reporter.reports.AGOLUsageReport')
    # mocker.patch.object('reporter.reports.AGOLUsageReport', 'out_path', out_path)

    mock_datetime = mocker.patch('datetime.datetime')
    mock_datetime.now.return_value = 'foo_date'

    mock_report = mocker.Mock()
    mock_report.out_path = out_path

    reports.AGOLUsageReport.save_report(mock_report, test_data)

    content = out_path.read_text()
    assert content == 'foo_date,\nfoo,bar\n1,2\n3,4\n'

    # def test_AGOL_create_report_itemid_not_in_metatable
