"""

"""

import datetime

import pytest

from reporter import credentials, tools


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

    _get_sharing_mock = mocker.patch('reporter.tools._get_sharing')
    _get_sharing_mock.return_value = Exception

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, folder, category)

    assert test_dict['sharing_everyone'] == 'sharing_error'
    assert test_dict['sharing_org'] == 'sharing_error'
    assert test_dict['sharing_groups'] == 'sharing_error'
    assert test_dict['open_data_group'] == 'group error'


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
