from reporter import reports

# def test_AGOL_create_report_itemid_not_in_metatable()


def test_AGOL_create_report_call_with_metatable_info(mocker):
    mock_object = mocker.Mock()

    mock_org = mocker.patch('reporter.tools.Organization')
    item = mocker.Mock()
    item.itemid = 'foo'
    mock_org.get_feature_services_in_folders.return_value = [(item, 'folder1')]
    mock_org.get_open_data_groups.return_value = ['Open Data Group']

    mock_metatable = mocker.patch('reporter.tools.Metatable')
    mock_row = mocker.Mock()
    mock_row.category = 'Test Category'
    mock_metatable.metatable_dict = {'foo': mock_row}

    reports.AGOLUsageReport.create_report(mock_object)

    assert mock_org.get_item_info.called_with(item, ['Open Data Group'], 'folder1', 'Test Category')


def test_AGOL_create_report_call_without_metatable_info(mocker):
    mock_object = mocker.Mock()

    mock_org = mocker.patch('reporter.tools.Organization')
    item = mocker.Mock()
    item.itemid = 'foo'
    mock_org.get_feature_services_in_folders.return_value = [(item, 'folder1')]
    mock_org.get_open_data_groups.return_value = ['Open Data Group']

    mock_metatable = mocker.patch('reporter.tools.Metatable')
    mock_row = mocker.Mock()
    mock_row.category = 'Test Category'
    mock_metatable.metatable_dict = {'bar': mock_row}

    reports.AGOLUsageReport.create_report(mock_object)

    assert mock_org.get_item_info.called_with(item, ['Open Data Group'], 'folder1', None)
