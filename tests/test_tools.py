"""

"""

import datetime
from collections import namedtuple

import pytest

from reporter import tools

try:
    from reporter import credentials
except (ModuleNotFoundError, ImportError):
    from reporter import credentials_template as credentials


@pytest.fixture(scope='function')
def item(mocker):
    """
    A default set of good values for the item to return
    """

    group1_mock = mocker.Mock()
    group1_mock.title = 'TestSGIDGroup'
    group2_mock = mocker.Mock()
    group2_mock.title = 'test_group'

    item = mocker.Mock()
    item.itemid = 'itemid'
    item.title = 'title'
    item.owner = 'owner'
    item.numViews = 42
    test_date = datetime.datetime(2020, 12, 25, 18, 30, 55)
    item.modified = test_date.timestamp() * 1000
    item.content_status = 'content_status'
    item.shared_with = {'everyone': True, 'org': True, 'groups': [group1_mock, group2_mock]}
    item.tags = ['tag1', 'tag2']
    item.size = 12582912  #: 12 MB
    item.usage('1Y').sum.return_value = 1234.0

    return item


@pytest.fixture(scope='function')
def metatable_row(mocker):
    """
    Default set of valid SGID values for metatable.
    """
    metatable_row = mocker.Mock()
    metatable_row.sgid_name = 'SGID.TEST.Layer'
    metatable_row.agol_name = 'Utah Test Layer'
    metatable_row.category = 'SGID'
    metatable_row.authoritative = 'y'

    return metatable_row


def test_get_item_info_correct_values(mocker, item):

    org_mock = mocker.Mock()

    folder = 'folder'
    open_data_groups = ['TestSGIDGroup']
    category = 'SGID'

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, folder, category)
    assert test_dict['itemid'] == 'itemid'
    assert test_dict['title'] == 'title'
    assert test_dict['owner'] == 'owner'
    assert test_dict['folder'] == 'folder'
    assert test_dict['views'] == 42
    assert test_dict['modified'] == '2020-12-25 18:30:55'
    assert test_dict['authoritative'] == 'content_status'
    assert test_dict['sharing_everyone'] == 'True'
    assert test_dict['sharing_org'] == 'True'
    assert test_dict['sharing_groups'] == 'TestSGIDGroup, test_group'
    assert test_dict['open_data_group'] == 'True'
    assert test_dict['in_sgid'] == 'True'
    assert test_dict['tags'] == 'tag1, tag2'
    assert test_dict['sizeMB'] == 12
    assert test_dict['monthly_credits'] == 12 * credentials.HFS_CREDITS_PER_MB
    assert test_dict['monthly_cost'] == 12 * credentials.HFS_CREDITS_PER_MB * credentials.DOLLARS_PER_CREDIT
    assert test_dict['data_requests_1Y'] == 1234


def test_get_item_info_not_open_data(mocker, item):
    org_mock = mocker.Mock()

    group_mock = mocker.Mock()
    group_mock.title = 'test_group'
    item.shared_with = {'everyone': True, 'org': True, 'groups': [group_mock]}

    open_data_groups = ['TestSGIDGroup']
    category = 'SGID'

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, 'folder', category)

    assert test_dict['open_data_group'] == 'False'


def test_get_item_info_shelved_data_not_in_sgid(mocker, item):
    org_mock = mocker.Mock()

    open_data_groups = ['TestSGIDGroup']

    category = 'shelved'

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, 'folder', category)

    assert test_dict['in_sgid'] == 'False'


def test_get_item_info_static_data_in_sgid(mocker, item):
    org_mock = mocker.Mock()

    open_data_groups = ['TestSGIDGroup']

    category = 'static'

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, 'folder', category)

    assert test_dict['in_sgid'] == 'True'


def test_get_item_info_root_folder(mocker, item):
    org_mock = mocker.Mock()

    folder = None
    open_data_groups = ['Foo']
    category = 'static'

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, folder, category)

    assert test_dict['folder'] == '_root'


def test_get_item_info_sharing_error(mocker, item):
    org_mock = mocker.Mock()

    folder = 'Foo'
    open_data_groups = ['Foo']
    category = 'static'

    _retry_mock = mocker.patch('reporter.tools.retry')
    _retry_mock.side_effect = Exception

    _get_sharing_mock = mocker.patch('reporter.tools._get_sharing')
    _get_sharing_mock.side_effect = Exception

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, folder, category)

    assert test_dict['sharing_everyone'] == 'sharing_error'
    assert test_dict['sharing_org'] == 'sharing_error'
    assert test_dict['sharing_groups'] == 'sharing_error'
    assert test_dict['open_data_group'] == 'group error'


def test_get_item_info_usage_error(mocker, item):
    org_mock = mocker.Mock()

    folder = 'Foo'
    open_data_groups = ['Foo']
    category = 'static'

    _retry_mock = mocker.patch('reporter.tools.retry')
    _retry_mock.side_effect = Exception

    _get_usage_mock = mocker.patch('reporter.tools._get_usage')
    _get_usage_mock.side_effect = Exception

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, folder, category)

    assert test_dict['data_requests_1Y'] == 'error'


def test_get_sharing_valid_data(item):
    sharing = tools._get_sharing(item)
    assert sharing[0] == 'True'
    assert sharing[1] == 'True'
    assert sharing[2] == 'TestSGIDGroup, test_group'


def test_get_open_data_groups_open_data_True(mocker):

    group_mock = mocker.Mock(spec=['isOpenData', 'title'], name='group mock')
    group_mock.isOpenData = True
    group_mock.title = 'OpenDataGroup'

    gis_mock = mocker.Mock(name='gis mock')

    gis_mock.gis.groups.search.return_value = [group_mock]

    open_data_groups = tools.Organization.get_open_data_groups(gis_mock)

    assert open_data_groups == ['OpenDataGroup']


def test_get_open_data_groups_open_data_False(mocker):

    group_mock = mocker.Mock(spec=['isOpenData', 'title'], name='group mock')
    group_mock.isOpenData = False
    group_mock.title = 'PrivateGroup'

    gis_mock = mocker.Mock(name='gis mock')

    gis_mock.gis.groups.search.return_value = [group_mock]

    open_data_groups = tools.Organization.get_open_data_groups(gis_mock)

    assert open_data_groups == []


def test_get_feature_services_in_folders_one_item(mocker):

    folders = ['folder']

    item_mock = mocker.Mock()
    item_mock.type = 'Feature Service'

    org_mock = mocker.Mock()
    org_mock.user_item.items.return_value = [item_mock]

    items_folders = tools.Organization.get_feature_services_in_folders(org_mock, folders)

    assert items_folders == [(item_mock, 'folder')]


def test_get_feature_services_in_folders_empty_for_no_feature_services(mocker):

    folders = ['folder']

    item_mock = mocker.Mock()
    item_mock.type = 'Bad Service'

    org_mock = mocker.Mock()
    org_mock.user_item.items.return_value = [item_mock]

    items_folders = tools.Organization.get_feature_services_in_folders(org_mock, folders)

    assert items_folders == []


def test_get_users_folders(mocker):
    fake_folder = {'title': 'test folder'}

    org_mock = mocker.Mock()
    org_mock.user_item.folders = [fake_folder]

    folders = tools.Organization.get_users_folders(org_mock)

    assert folders == [None, 'test folder']


def test_get_users_folders_returns_None_for_root(mocker):
    org_mock = mocker.Mock()
    org_mock.user_item.folders = []

    folders = tools.Organization.get_users_folders(org_mock)

    assert folders == [None]


def test_retry_calls_method_four_times(mocker):
    mocker.patch('reporter.tools.sleep')

    worker_mock = mocker.Mock()
    worker_mock.side_effect = Exception

    try:
        tools.retry(worker_mock)
    except:
        pass

    assert worker_mock.call_count == 4


def test_read_sgid_metatable_to_dictionary(mocker):

    def return_sgid_row(self, table, fields):
        #: table_sgid_name, table_agol_itemid, table_agol_name, table_authoritative
        for row in [['table name', '11112222333344445555666677778888', 'agol title', None]]:
            yield row

    sgid_fields = ['TABLENAME', 'AGOL_ITEM_ID', 'AGOL_PUBLISHED_NAME', 'Authoritative']

    mocker.patch('reporter.tools.Metatable._cursor_wrapper', return_sgid_row)

    mock_logger = mocker.Mock()

    test_table = tools.Metatable(mock_logger)
    test_table.read_metatable('something', sgid_fields)

    assert test_table.metatable_dict['11112222333344445555666677778888'] == ('table name', 'agol title', 'SGID', None)


def test_read_agol_metatable_to_dictionary(mocker):

    def return_agol_row(self, table, fields):
        #: table_sgid_name, table_agol_itemid, table_agol_name, table_category
        for row in [['table name', '11112222333344445555666677778888', 'agol title', 'shelved']]:
            yield row

    agol_fields = ['TABLENAME', 'AGOL_ITEM_ID', 'AGOL_PUBLISHED_NAME', 'CATEGORY']

    mocker.patch('reporter.tools.Metatable._cursor_wrapper', return_agol_row)

    mock_logger = mocker.Mock()

    test_table = tools.Metatable(mock_logger)
    test_table.read_metatable('something', agol_fields)

    assert test_table.metatable_dict['11112222333344445555666677778888'] == ('table name', 'agol title', 'shelved', 'n')


def test_read_metatable_returns_nothing_on_bad_uuid(mocker):

    def return_agol_row(self, table, fields):
        #: table_sgid_name, table_agol_itemid, table_agol_name, table_category
        for row in [['table name', 'bad_uuid', 'agol title', 'shelved']]:
            yield row

    agol_fields = ['TABLENAME', 'AGOL_ITEM_ID', 'AGOL_PUBLISHED_NAME', 'CATEGORY']

    mocker.patch('reporter.tools.Metatable._cursor_wrapper', return_agol_row)

    mock_logger = mocker.Mock()

    test_table = tools.Metatable(mock_logger)
    test_table.read_metatable('something', agol_fields)

    assert test_table.metatable_dict == {}


def test_read_metatable_handles_duplicate_rows(mocker):

    def return_agol_row(self, table, fields):
        #: table_sgid_name, table_agol_itemid, table_agol_name, table_category
        for row in [
            ['table name', '11112222333344445555666677778888', 'agol title', 'shelved'],
            ['table name', '11112222333344445555666677778888', 'agol title', 'shelved'],
        ]:
            yield row

    agol_fields = ['TABLENAME', 'AGOL_ITEM_ID', 'AGOL_PUBLISHED_NAME', 'CATEGORY']

    mocker.patch('reporter.tools.Metatable._cursor_wrapper', return_agol_row)

    mock_logger = mocker.Mock()

    test_table = tools.Metatable(mock_logger)
    test_table.read_metatable('something', agol_fields)

    assert test_table.metatable_dict['11112222333344445555666677778888'] == ('table name', 'agol title', 'shelved', 'n')
    assert test_table.duplicate_keys == ['11112222333344445555666677778888']
