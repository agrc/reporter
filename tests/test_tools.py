"""

"""

import datetime

from reporter import credentials, tools


def test_get_item_info_correct_values(mocker):

    org_mock = mocker.Mock()

    group1_mock = mocker.Mock()
    group1_mock.title = 'Utah SGID TestSGIDGroup'
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

    folder = 'folder'

    test_dict = tools.Organization.get_item_info(org_mock, item, folder)
    assert test_dict['itemid'] == 'itemid'
    assert test_dict['title'] == 'title'
    assert test_dict['owner'] == 'owner'
    assert test_dict['folder'] == 'folder'
    assert test_dict['views'] == 42
    assert test_dict['modified'] == '2020-12-25 18:30:55'
    assert test_dict['authoritative'] == 'content_status'
    assert test_dict['open_data'] == 'yes'
    assert test_dict['groups'] == 'Utah SGID TestSGIDGroup, test_group'
    assert test_dict['tags'] == 'tag1, tag2'
    assert test_dict['sizeMB'] == 12
    assert test_dict['credits'] == 12 * credentials.HFS_CREDITS_PER_MB
    assert test_dict['cost'] == 12 * credentials.HFS_CREDITS_PER_MB * credentials.DOLLARS_PER_CREDIT
    assert test_dict['data_requests_1Y'] == 1234
