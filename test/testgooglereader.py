import unittest
import os
import sys

# insert application path
app_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), '../')
sys.path.insert(0, app_path)

from googlereader import GoogleReaderClient

FEED_NAME = 'BBC News FP'
FEED_URL = 'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml'


class TestGoogleReader(unittest.TestCase):
    '''Test class for Google Reader API client'''

    def setUp(self):
        '''Setups for each test'''
        cfg={'username': '', 'password': '', 'client_id': ''}
        self.client = GoogleReaderClient(cfg)

    def testSubscriptionList(self):
        '''Retrieving subscription list'''
        response = self.client.get_subscription_list()
        self.assertNotEquals(response['subscriptions'], None)

    def testSubscribeToFeed(self):
        'Subscribing to feed'
        response = self.client.subscribe_to_feed(FEED_NAME, FEED_URL)
        self.assertEquals(response, 'OK')

    def testSubscribeToFeed_with_info(self):
        'Subscribing to feed (with info response)'
        response = self.client.subscribe_to_feed(FEED_NAME, FEED_URL, True)
        self.assertNotEquals(response['streamId'], None)

    def testAddLabel(self):
        '''Adding a label'''
        response = self.client.add_label_to_feed(FEED_NAME, FEED_URL,
            'testLabel')
        self.assertEquals(response, 'OK')

    def testRemoveLabel(self):
        '''Removing a label'''
        response = self.client.remove_label_from_feed(FEED_NAME, FEED_URL,
            'testLabel')
        self.assertEquals(response, 'OK')

    def testUnsubscribeFromFeed(self):
        '''Unsubscribing from feed'''
        feed = self.client.subscribe_to_feed(FEED_NAME, FEED_URL, True)
        response = self.client.unsubscribe_from_feed(FEED_NAME,
            feed['streamId'])
        self.assertEquals(response, 'OK')

    def testMakeFolderPublic(self):
        '''Make a folder public'''
        tags = self.client.get_tag_list()['tags']
        response = self.client.edit_folder_or_tag(tags[0]['id'], False)
        self.assertEquals(response, 'OK')

    def testMakeFolderPrivate(self):
        '''Make a folder private'''
        tags = self.client.get_tag_list()['tags']
        response = self.client.edit_folder_or_tag(tags[0]['id'], True)
        self.assertEquals(response, 'OK')

    def testGetTagsList(self):
        '''Get list of tags'''
        response = self.client.get_tag_list()
        self.assertNotEquals(response['tags'], None)

    def testGetPreferencesList(self):
        '''Search get preferences list'''
        response = self.client.get_preferences_list()
        self.assertNotEquals(response['prefs'], 'OK')

    def testMarkAsRead(self):
        '''Mark item as read'''
        unread_items = self.client.get_unread_items(1)
        response = self.client.mark_as_read(unread_items['items'][0]['id'],
            unread_items['items'][0]['origin']['streamId'])
        self.assertEquals(response, 'OK')

    def testTagAdd(self):
        '''Adding a tag to an individual item '''
        unread_items = self.client.get_unread_items(1)
        response = self.client.add_tag(unread_items['items'][0]['id'],
            'tag_item_test')
        self.assertEquals(response, 'OK')

    def testTagRemove(self):
        '''Removing a tag from an individual item '''
        unread_items = self.client.get_unread_items(1)
        response = self.client.remove_tag(unread_items['items'][0]['id'],
            'tag_item_test')
        self.assertEquals(response, 'OK')

    def testGetUnreadCount(self):
        '''Get unread count'''
        response = self.client.get_unread_count(False)
        self.assertNotEquals(response['unreadcounts'], None)

    def testGetUnreadItems(self):
        '''Get unread Items'''
        response = self.client.get_unread_items(1)
        self.assertNotEquals(response['items'], None)

    def testSearchReadItems(self):
        '''Search read items'''
        response = self.client.search_read_items('the')
        self.assertNotEquals(response['results'], None)

    def testSearchStarredItems(self):
        '''Search starred items'''
        response = self.client.search_starred_items('the')
        self.assertNotEquals(response['results'], None)

    def testSearchSharedItems(self):
        '''Search shared items'''
        response = self.client.search_shared_items('the')
        self.assertNotEquals(response['results'], None)

    def testSearchFollowedItems(self):
        '''Search followed items'''
        response = self.client.search_followed_items('the')
        self.assertNotEquals(response['results'], None)

    def testSearchNotes(self):
        '''Search notes'''
        response = self.client.search_notes('the')
        self.assertNotEquals(response['results'], None)

    def testSearchFolder(self):
        '''Search folder items'''
        response = self.client.search_folder('the', 'javascript')
        self.assertNotEquals(response['results'], None)

    def testSearchFeed(self):
        '''Search feed items'''
        response = self.client.search_feed('the', FEED_URL)
        self.assertNotEquals(response['results'], None)

    def testSearchAll(self):
        '''Search All items'''
        response = self.client.search_all('the')
        self.assertNotEquals(response['results'], None)

if __name__ == '__main__':
    unittest.main()
