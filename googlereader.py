'''Client for the Google Reader API'''

import re
from restclient import restClient
from time import time

# http://code.google.com/p/pyrfeed/wiki/GoogleReaderAPI
class GoogleReaderClient(restClient):
    '''Client for the Google Reader API'''
    # urls
    __GOOGLE_URL = 'https://www.google.com'
    __READER_URL = __GOOGLE_URL + '/reader'
    __LOGIN_URL = __GOOGLE_URL + '/accounts/ClientLogin'
    __TOKEN_URL = __READER_URL + '/api/0/token'
    __SUBSCRIPTION_LIST_URL = __READER_URL + '/api/0/subscription/list'
    __TAG_LIST_URL = __READER_URL + '/api/0/tag/list'
    __PREFERENCE_LIST_URL = __READER_URL + '/api/0/preference/list'
    __SUBSCRIPTION_URL = __READER_URL + '/api/0/subscription/edit'
    __SUBSCRIPTION_URL_QUICK = __READER_URL + '/api/0/subscription/quickadd'
    __EDIT_FOLDER_URL = __READER_URL + '/api/0/tag/edit'
    __EDIT_TAG_URL = __READER_URL + '/api/0/edit-tag'
    __DISABLE_TAG_URL = __READER_URL + '/api/0/disable-tag'
    __UNREAD_COUNT = __READER_URL + '/api/0/unread-count'
    __SEARCH_URL = __READER_URL + '/api/0/search/items/ids'
    __USER_INFO_URL = __READER_URL + '/api/0/user-info'

    # feed urls
    # __READING_LIST = __READER_URL + '/api/0/stream/contents/user/%s/state/com.google/reading-list'
    # __UNREAD_ITEMS_URL = __READER_URL + '/api/0/stream/contents/user/%s/state/com.google/reading-list'
    # __FEED_READ_ITEMS_URL = __READER_URL + '/atom/user/-/state/com.google/read'
    __FEED_ITEMS_BY_LABEL_URL = __READER_URL + '/api/0/stream/contents/user/%s/label/%s'
    __FEED_ITEMS_BY_STATE_URL = __READER_URL + '/api/0/stream/contents/user/%s/state/com.google/%s'
    __FEED_CONTENTS_URL = __READER_URL + '/api/0/stream/contents/%s'
    __FEED_DETAILS_URL = __READER_URL + '/api/0/stream/details'
    __ATOM_FEED_URL = __READER_URL + '/atom/feed/%s'

    # actions
    __ADD_ACTION = 'a'
    __REMOVE_ACTION = 'r'
    __SUBSCRIBE_ACTION = 'subscribe'
    __UNSUBSCRIBE_ACTION = 'unsubscribe'
    __EDIT_ACTION = 'edit'
    __DELETE_TAG_ACTION = 'user/%s/label/%s'

    # state types
    __STATE_READ_ITEMS = 'user/%s/state/com.google/read'
    __STATE_STARRED_ITEMS = 'user/%s/state/com.google/starred'
    __STATE_SHARED_ITEMS = 'user/%s/state/com.google/broadcast'
    __STATE_FOLLOWED_ITEMS = 'user/%s/state/com.google/broadcast-friends'
    __STATE_NOTE_ITEMS = 'user/%s/state/com.google/created'
    __STATE_FOLDER_ITEMS = 'user/%s/label/%s'
    __FEED_ID = 'feed/%s'

    __SEARCH_CONTENTS_URL = __READER_URL + '/api/0/stream/items/contents?ck=%s&client=%s'
    __EXPORT_OPML = __READER_URL + '/subscriptions/export'

    def __init__(self, config):
        restClient.__init__(self, config)

        self.__username = config['username'] if 'username' in config else None
        self.__password = config['password'] if 'password' in config else None
        self.__client_id = config['client_id'] if 'client_id' in config else None
        self.__response_format = config['response_format'] if ('response_format' in config and config['response_format'] in ['json', 'xml']) else 'json'
        self.__token = None
        self.__google_reader_cookie_id = None
        self.__user_id = None

        if (self.__username is not None and self.__password is not None):
            self.__login()

    def __login(self):
        '''
        Login to Google Reader
        '''
        # request without serialization as response is cookie data not json
        response = self.request(
            'POST',
            self.__LOGIN_URL,
            body={
                'Email': self.__username,
                'Passwd': self.__password,
                'service': 'reader',
                'source': self.__client_id,
                'continue': self.__GOOGLE_URL},
            deserialize=False
            )

        #pre-check first for HTTP 200 (needed?)
        if response.status_int == 200 and response.body.startswith('SID='):
            self.__google_reader_cookie_id = str(re.search('SID=(\S*)',
                response.body).group(1))
            self.__user_id = self.__get_user_info()
            return True
        return False

    def __get_user_info(self):
        ''' Get user info eg client id'''
        user_info = self.request(
            'GET',
            self.__USER_INFO_URL,
            headers=self.__build_request_headers(),
            ck=str(int(time())),
            client=self.__client_id)

        return user_info['userId']

    def __update_token(self):
        ''' Gets a updated token'''
        headers = self.__build_request_headers()
        token_data = self.request(
            'GET',
            self.__TOKEN_URL,
            headers=headers,
            client=self.__client_id,
            output=self.__response_format,
            ck=str(int(time())),
            deserialize=False)
        self.__token = token_data.body
        return self.__token

    def __build_request_headers(self, headers=None):
        '''Populates correct headers to make authorised requests'''
        if headers is None:
            headers = {}
        headers['User-agent'] = self.__client_id
        headers['Cookie'] = 'Name=SID; SID=%s; Domain=.google.com; Path=/;Expires=160000000000' % self.__google_reader_cookie_id
        return headers

    def __edit_item_state(self, item_id, label, action, feed_url=None):
        ''' Edits a specific item by adding or removing a tag'''
        self.__update_token()
        args = {
            'i': item_id,
            'T': self.__token}
        if feed_url is None:
            args[action] = 'user/-/label/'+label
        else:
            args['s'] = feed_url if feed_url.startswith('feed/') else self.__FEED_ID % feed_url
            args[action] = self.__STATE_READ_ITEMS % self.__user_id

        return self.request(
            'POST',
            self.__EDIT_TAG_URL+'?client='+self.__client_id,
            body=args,
            headers=self.__build_request_headers())

    def __edit_subscription(self, feed_title=None, feed_url=None, label=None,
        label_action=None, action=None):
        """Performs an edit operation upon a feed. Possible operations are
            subscribe, unsubscribe and adding or removing labels
        """

        if feed_title and feed_url:
            self.__update_token()
            args = {
                's': feed_url if feed_url.startswith('feed/') else self.__FEED_ID % feed_url,
                't': feed_title,
                'ac': action,
                'T': self.__token}
            # add or remove label if edit action
            if action is self.__EDIT_ACTION:
                if label and label_action:
                    args[label_action] = 'user/-/label/'+label
            return self.request(
                'POST',
                self.__SUBSCRIPTION_URL+'?client='+self.__client_id,
                body=args,
                headers=self.__build_request_headers())

    def edit_folder_or_tag(self, folder__tag_id, is_public=False):
        ''' Make a folder public or private  '''
        self.__update_token()
        args = {
            's': folder__tag_id,
            'pub': str(is_public).lower(),
            'T': self.__token,
            't': folder__tag_id}
        return self.request(
            'POST',
            self.__EDIT_FOLDER_URL+'?client='+self.__client_id,
            body=args,
            headers=self.__build_request_headers())

    def subscribe_to_feed(self, feed_title, feed_url, quickAdd=False):
        ''' Adds a feed '''
        # Use quick add url; returns feed information
        if quickAdd is True:
            if self.__token == None:
                self.__update_token()
            args={
                'T': self.__token,
                'quickadd': feed_url}

            return self.request(
                'POST',
                self.__SUBSCRIPTION_URL_QUICK+'?client=%s&ck=%s' % (self.__client_id, str(int(time()))),
                body=args,
                headers=self.__build_request_headers())
        else:
            response = self.__edit_subscription(
                feed_title,
                feed_url,
                action=self.__SUBSCRIBE_ACTION)
            return response

    def unsubscribe_from_feed(self, feed_title, feed_url):
        ''' Removes a feed '''
        return self.__edit_subscription(
            feed_title,
            feed_url,
            action=self.__UNSUBSCRIBE_ACTION)

    def add_label_to_feed(self, feed_title, feed_url, label):
        ''' Adds a label to a feed '''
        return self.__edit_subscription(feed_title,
            feed_url,
            label=label,
            label_action=self.__ADD_ACTION,
            action=self.__EDIT_ACTION)

    def remove_label_from_feed(self, feed_title, feed_url, label):
        ''' Removes a label from a feed '''
        return self.__edit_subscription(feed_title,
            feed_url,
            label=label,
            label_action=self.__REMOVE_ACTION,
            action=self.__EDIT_ACTION)

    def edit_feed_title(self, newTitle, feed_url):
        '''Edit a title of a specific item '''
        return self.__edit_subscription(newTitle, feed_url, action=self.__EDIT_ACTION)

    def add_tag(self, item_id, tag):
        '''Add a label or tag onto a specific item '''
        return self.__edit_item_state(item_id, tag, self.__ADD_ACTION)

    def remove_tag(self, item_id, tag):
        '''Remove a label or tag onto a specific item '''
        return self.__edit_item_state(item_id, tag, self.__REMOVE_ACTION)

    def delete_tag(self, tag):
        '''Disable tag'''
        self.__update_token()

        return self.request(
            'POST',
            self.__DISABLE_TAG_URL+'?client='+self.__client_id,
            body={
                's': tag if tag.startswith('user/') else self.__DELETE_TAG_ACTION % (self.__user_id, tag),
                'ac': 'disable-tags',
                'T': self.__token},
            headers=self.__build_request_headers())

    def get_subscription_list(self):
        ''' Returns full list of subscribed feeds'''
        return self.request(
            'GET',
            self.__SUBSCRIPTION_LIST_URL,
            headers=self.__build_request_headers(),
            client=self.__client_id,
            output=self.__response_format,
            ck=str(int(time())))

    def get_tag_list(self):
        ''' Get list of tags and labels '''
        return self.request(
            'GET',
            self.__TAG_LIST_URL,
            headers=self.__build_request_headers(),
            client=self.__client_id,
            output=self.__response_format,
            ck=str(int(time())))

    def get_preferences_list(self):
        ''' Get list of preferences '''
        return self.request(
            'GET',
            self.__PREFERENCE_LIST_URL,
            headers=self.__build_request_headers(),
            client=self.__client_id,
            output=self.__response_format,
            ck=str(int(time())))

    def set_response_format(self, response_format):
        ''' Set output of data, either json or xml'''
        if response_format not in ['json', 'xml']:
            raise ValueError("%s is invalid. Must be 'json' or 'xml'" % response_format)
        self.__response_format = response_format

    def get_feed_details(self, feed_id, fetchTrends=False):
        return self.request(
            'GET',
            self.__FEED_DETAILS_URL,
            headers=self.__build_request_headers(),
            s=feed_id,
            tz=0,
            fetchTrends=str(fetchTrends).lower(),
            output=self.__response_format,
            ck=str(int(time())),
            client=self.__client_id)

    def get_feed_contents(self, feed_id, num=20, order='n', use_atom=False):
        return self.request(
            'GET',
            self.__FEED_CONTENTS_URL % (feed_id) if use_atom is False else self.__ATOM_FEED_URL % feed_id,
            headers=self.__build_request_headers(),
            r=order,
            n=num,
            ck=str(int(time())),
            client=self.__client_id)

    def mark_as_read(self, feed_item_id, feed_url=None):
        '''
        Marks item as read
        '''
        return self.__edit_item_state(feed_item_id, 'read', self.__ADD_ACTION, feed_url)

    def get_unread_count(self, get_all=False):
        '''
        Gets unread count of subscriptions
        '''
        return self.request(
            'GET',
            self.__UNREAD_COUNT,
            headers=self.__build_request_headers(),
            client=self.__client_id,
            output=self.__response_format,
            all=str(get_all).lower())

    def get_items_by_state_or_label(self, state, num, order='n', exclude_state=None, label=None, feed_id=None, use_atom=False):
        ''' Retrieves items by specified state or label using specified feed 
        or reading list if not specified'''
        if label is None:
            if feed_id is not None and use_atom is True:
                resource_url = self.__ATOM_FEED_URL % feed_id
            else:
                resource_url = self.__FEED_ITEMS_BY_STATE_URL % (self.__user_id, state)
        else:
            if feed_id is not None and use_atom is True:
                resource_url = self.__ATOM_FEED_URL % feed_id
            else:
                resource_url = self.__FEED_ITEMS_BY_LABEL_URL % (self.__user_id, label)

        if exclude_state is not None:
            response = self.request(
                'GET',
                resource_url,
                headers=self.__build_request_headers(),
                xt='user/-/state/com.google/%s' % exclude_state,
                r=order,
                n=num,
                ck=str(int(time())),
                client=self.__client_id)
        else:
            response = self.request(
                'GET',
                resource_url,
                headers=self.__build_request_headers(),
                r=order,
                n=num,
                ck=str(int(time())),
                client=self.__client_id)
        return response

    def get_all_items(self, num=20, order='n', label=None, feed_id=None, use_atom=False):
        '''
        Get all items
        '''
        return self.get_items_by_state_or_label('reading-list', num, order, label, feed_id=feed_id, use_atom=use_atom)

    def get_starred_items(self, num=20, order='n', exclude_state=None, label=None, feed_id=None, use_atom=False):
        '''
        Get starred items
        '''
        return self.get_items_by_state_or_label('starred', num, order, exclude_state, label, feed_id=feed_id, use_atom=use_atom)

    def get_broadcast_items(self, num=20, order='n', exclude_state=None, label=None, feed_id=None, use_atom=False):
        '''
        Get starred items
        '''
        return self.get_items_by_state_or_label('broadcast', num, order, exclude_state, label, feed_id=feed_id, use_atom=use_atom)

    def get_kept_unread_items(self, num=20, order='n', exclude_state=None, label=None, feed_id=None, use_atom=False):
        '''
        Get kept-unread items
        '''
        return self.get_items_by_state_or_label('kept-unread', num, order, exclude_state, label, feed_id=feed_id, use_atom=use_atom)

    def get_fresh_items(self, num=20, order='n', exclude_state=None, label=None, feed_id=None, use_atom=False):
        '''
        Get starred items
        '''
        return self.get_items_by_state_or_label('fresh', num, order, exclude_state, label, feed_id=feed_id, use_atom=use_atom)

    def get_starred_items(self, num=20, order='n', exclude_state=None, label=None, feed_id=None, use_atom=False):
        '''
        Get starred items
        '''
        return self.get_items_by_state_or_label('starred', num, order, exclude_state, label, feed_id=feed_id, use_atom=use_atom)

    def get_unread_items(self, num=20, order='n', label=None, feed_id=None, use_atom=False):
        '''
         Get unread items
        '''
        return self.get_items_by_state_or_label('reading-list', num, order, exclude_state='read', label=label, feed_id=feed_id, use_atom=use_atom)

    def __search(self, query, search_type, num=20):
        '''
        Search method that calls the webservices.
        Used by all other search methods
        '''
        return self.request(
            'GET',
            self.__SEARCH_URL,
            headers=self.__build_request_headers(),
            q=query,
            s=search_type,
            num=num,
            client=self.__client_id,
            output=self.__response_format,
            ck=str(int(time())))

    def search_all(self, query, num=20):
        '''Search within everything for query'''
        return self.request(
            'GET',
            self.__SEARCH_URL,
            headers=self.__build_request_headers(),
            q=query,
            num=num,
            client=self.__client_id,
            output=self.__response_format,
            ck=str(int(time())))

    def search_read_items(self, query, num=20):
        '''Search within read items for query'''
        return self.__search(
            query,
            self.__STATE_READ_ITEMS % self.__user_id,
            num)

    def search_starred_items(self, query, num=20):
        '''Search within starred items for query'''
        return self.__search(
            query,
            self.__STATE_STARRED_ITEMS % self.__user_id,
            num)

    def search_shared_items(self, query, num=20):
        '''Search within shared items for query'''
        return self.__search(
            query,
            self.__STATE_SHARED_ITEMS % self.__user_id,
            num)

    def search_followed_items(self, query, num=20):
        '''Search followed people for query'''
        return self.__search(
            query,
            self.__STATE_FOLLOWED_ITEMS % self.__user_id,
            num)

    def search_folder(self, query, folder, num=20):
        '''Search within specified folder for query'''
        return self.__search(
            query,
            self.__STATE_FOLDER_ITEMS % (self.__user_id, folder),
            num)

    def search_notes(self, query, num=20):
        '''Search within notes for query'''
        return self.__search(
            query,
            self.__STATE_NOTE_ITEMS % self.__user_id,
            num)

    def search_feed(self, query, feed_id, num=20):
        '''Search within specified feed for query'''
        return self.__get_search_contents(self.__search(query, feed_id, num)['results'])

    def __get_search_contents(self, content_ids):
        self.__update_token()
        self.debug(True)
        return self.request(
            'POST',
            self.__SEARCH_CONTENTS_URL % (str(int(time())), self.__client_id),
            body = '%s&T=%s' %( ''.join(['i=%s&' % (i['id']) for i in content_ids]), self.__token),
            headers=self.__build_request_headers({'Content-Type':'application/x-www-form-urlencoded; charset=utf-8'})
        )

    def export_OPML(self):
        return self.request(
            'GET',
            self.__EXPORT_OPML,
            headers=self.__build_request_headers(),
            deserialize=False).body

# do we need these as we're just essentially getting a wrapper around a python dict?
class GoogleFeedReader(object):
    """
        Essentially a collection of GoogleReaderFeedItem objects?
    """
    def __init__(self, g):
        self.__client = g
        self.num_unread = self.get_unread_number()
        self.unread_items = {}
        self.feeds = {}
        
    def get_tags(self):
        """docstring for get_tags"""
        tags = []
        gTags = self.__client.get_tag_list()
        for t in gTags['tags']:
            tags.append(GoogleReaderFolder(t, self.__client))
        return tags
    
    def get_subscriptions(self):
        """docstring for get_subscriptions"""
        pass
    
    def export(self, filename):
        """docstring for export"""
        return self.__client.export_OPML()

    def get_unread_number(self):
        """docstring for get_unread_number"""
        """"""
        unread_counts = self.__client.get_unread_count()
        for u in unread_counts['unreadcounts']:
            if u['id'].endswith('/reading-list'):
                return u['count']
        return unread_counts['max']

    def get_unread_items(self, num=20):
        """docstring for get_unread_items"""
        unread_items = self.__client.get_unread_items(num)
        for u in unread_items['items']:
            self.__add_feed(u['origin'])
            self.unread_items[u['id']] = GoogleReaderFeedItem(u, self.__client)
        return self.unread_items

    def subscribe(self, feed_url):
        return self.__add_feed(self.__client.subscribe_to_feed('', feed_url, True))
        
    def __add_feed(self, feed):
        """Add feed"""
        if feed['streamId'] not in self.feeds:
            self.feeds[feed['streamId']] = GoogleReaderFeed(feed, self.__client)
        return self.feeds[feed['streamId']]
            
class GoogleReaderFeed(object):
    """GoogleReaderFeed"""
    def __init__(self, feed, g):
        '''get attributes of config and store?'''
        self.__client = g
        self.data = {}
        self.data['title'] = feed['title'] if 'title' in feed else ''
        self.data['streamId'] = feed['streamId'] if 'streamId' in feed else None
        self.data['htmlUrl'] = feed['htmlUrl'] if 'htmlUrl' in feed else ''
        self.data['categories'] = {}
        
    def rename(self, new_title):
        r = self.__client.edit_feed_title(new_title, self.data['streamId'])
        if r == 'OK':
            self.data['title'] = new_title
            return True
        else:
            return False
    
    def unsubscribe(self):
        r = self.__client.unsubscribe_from_feed(self.data['title'], self.data['streamId'])
        return True if r == 'OK' else False        

    def get_details(self, get_trend_info=False):
        r = self.__client.get_feed_details(self.data['streamId'], get_trend_info)
        for p in r:
            self.data[p] = r[p]
        return r

    def get_contents(self, num=20):
        r = self.__client.get_feed_contents(self.data['streamId'], num)
        for p in r:
            self.data[p] = r[p]
        return r
        
    def add_label(self, label):
        r = self.__client.add_label_to_feed(self.data['title'], self.data['streamId'], label)
        if r == 'OK':
            self.data['categories'][label] = label
            return True
        else:
            return False

    def remove_label(self, label):
        r = self.__client.remove_label_from_feed(self.data['title'], self.data['streamId'], label)
        if r == 'OK':
            del self.data['categories'][label]
            return True
        else: 
            return False

    def search(self, query, num=20):
        return self.__client.search_feed(query, self.data['streamId'], num)

    def get_categories(self):
        return self.data['categories']

class GoogleReaderFeedItem(object):
    '''GoogleReader Feed Item'''
    
    def __init__(self, item, g):
        '''get attributes of config and store?'''
        # ['origin', 'updated', 'author', 'title', 'alternate', 'comments', 'summary', 'crawlTimeMsec', 'annotations', 'published', 'id', 'categories', 'likingUsers']
        self.__client = g
        self.data = {}
        for p in ['updated', 'author', 'title', 'alternate', 'comments', 'summary', 'crawlTimeMsec', 'annotations', 'published', 'id', 'categories', 'likingUsers']:
            if p in item:
                self.data[p] = item[p]
            
    def set_state(self, state):
        pass

    def search(self, query):
        pass

    def get_contents(self):
        pass
    
    def rename(self):
        pass

class GoogleReaderFolder(object):
    '''GoogleReaderFolder'''
    def __init__(self, folder, g):
        '''get attributes of config and store?'''
        self.__client = g
        self.data['id'] = folder['id']
        self.data['sortid'] = folder['sortid']
        self.data['title'] = folder['title'] if 'title' in folder else self.id.split('/').pop()

    def set_public(self, is_public):
        r = self.__client.edit_folder_or_tag(self.data['id'], is_public)
        return True if r == 'OK' else False

    def delete(self):
        r = self.__client.delete_tag(self.data['id'])
        return True if r == 'OK' else False