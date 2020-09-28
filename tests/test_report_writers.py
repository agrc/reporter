from reporter import report_writers


def test_list_of_dicts_to_csv_gets_columns_right(mocker, tmp_path):
    test_data = [{'foo': 1, 'bar': 2}, {'bar': 4, 'foo': 3}]
    out_path = tmp_path / 'test.csv'

    mock_datetime = mocker.patch('datetime.datetime')
    mock_datetime.now.return_value.strftime.return_value = 'foo_date'

    report_writers.list_of_dicts_to_csv(test_data, out_path)

    content = out_path.read_text()
    assert content == 'foo_date,\nfoo,bar\n1,2\n3,4\n'


def test_list_of_dicts_to_rotating_logger_correct_output(mocker, tmp_path):
    test_data = [{'foo': 1, 'bar': 2}, {'bar': 4, 'foo': 3}]
    out_path = tmp_path / 'test.csv'

    mock_datetime = mocker.patch('datetime.datetime')
    mock_datetime.now.return_value.strftime.return_value = 'foo_date'

    report_writers.list_of_dicts_to_rotating_logger(test_data, out_path)

    content = out_path.read_text()
    assert content == 'foo_date\nfoo|bar\n1|2\n3|4\n'
