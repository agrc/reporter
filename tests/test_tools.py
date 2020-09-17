"""

"""

import datetime
from collections import namedtuple

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
    item.shared_with = {'groups': [group1_mock, group2_mock]}
    item.tags = ['tag1', 'tag2']
    item.size = 12582912  #: 12 MB
    item.usage('1Y').sum.return_value = 1234

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


def test_get_item_info_correct_values(mocker, item, metatable_row):

    org_mock = mocker.Mock()

    folder = 'folder'
    open_data_groups = ['TestSGIDGroup']

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, folder, metatable_row)
    assert test_dict['itemid'] == 'itemid'
    assert test_dict['title'] == 'title'
    assert test_dict['owner'] == 'owner'
    assert test_dict['folder'] == 'folder'
    assert test_dict['views'] == 42
    assert test_dict['modified'] == '2020-12-25 18:30:55'
    assert test_dict['authoritative'] == 'content_status'
    assert test_dict['open_data_group'] == 'True'
    assert test_dict['in_sgid'] == 'True'
    assert test_dict['groups'] == 'TestSGIDGroup, test_group'
    assert test_dict['tags'] == 'tag1, tag2'
    assert test_dict['sizeMB'] == 12
    assert test_dict['credits'] == 12 * credentials.HFS_CREDITS_PER_MB
    assert test_dict['cost'] == 12 * credentials.HFS_CREDITS_PER_MB * credentials.DOLLARS_PER_CREDIT
    assert test_dict['data_requests_1Y'] == 1234


def test_get_item_info_not_open_data(mocker, item, metatable_row):
    org_mock = mocker.Mock()

    group_mock = mocker.Mock()
    group_mock.title = 'test_group'
    item.shared_with = {'groups': [group_mock]}

    open_data_groups = ['TestSGIDGroup']

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, 'folder', metatable_row)

    assert test_dict['open_data_group'] == 'False'


def test_get_item_info_shelved_data_not_in_sgid(mocker, item, metatable_row):
    org_mock = mocker.Mock()

    open_data_groups = ['TestSGIDGroup']

    metatable_row.category = 'shelved'

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, 'folder', metatable_row)

    assert test_dict['in_sgid'] == 'False'


def test_get_item_info_static_data_in_sgid(mocker, item, metatable_row):
    org_mock = mocker.Mock()

    open_data_groups = ['TestSGIDGroup']

    metatable_row.category = 'static'

    test_dict = tools.Organization.get_item_info(org_mock, item, open_data_groups, 'folder', metatable_row)

    assert test_dict['in_sgid'] == 'True'
