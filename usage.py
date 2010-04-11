from googlereader import GoogleReaderClient


def usage(cfg):
    g = GoogleReaderClient(cfg)

    feed_title = 'BBC FP'
    feed_url = 'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml'
    # Unread count
    r = g.get_unread_count()
    print "Unread count: %s" % len(r['unreadcounts'])

    # get list of subscriptions
    r = g.get_subscription_list()
    print "Found %s subscriptions" % len(r['subscriptions'])

    # Subscribe to feed
    print 'Subscribing to feed url: %s ' % feed_url
    new_feed = g.subscribe_to_feed(feed_title, feed_url, True)
    print new_feed
    print 'Retrieving feed contents for %s' % r['subscriptions'][0]['id']
    print g.get_feed_contents(r['subscriptions'][0]['id'], 2)

    # atom test
    # print g.get_feed_contents(feed_url, 2, use_atom=True)

    print 'Retrieving feed details for %s' % r['subscriptions'][0]['id']
    print g.get_feed_details(r['subscriptions'][0]['id'], False)

    print 'Retrieving unread items'
    unread_items = g.get_unread_items(1)
    print len(unread_items['items'])

    # atom test
    # unread_items2 = g.get_unread_items(1, feed_id=feed_url, use_atom=True)
    # print len(unread_items2['items'])

    # Change state of individual items
    print 'Marking as read'
    print g.mark_as_read(unread_items['items'][0]['id'],
        unread_items['items'][0]['origin']['streamId'])

    # Tag individual items
    print 'Adding tag to item ' + unread_items['items'][0]['title']
    print g.add_tag(unread_items['items'][0]['id'], 'addTagTest')

    print 'Removing tag from item ' + unread_items['items'][0]['title']
    print g.remove_tag(unread_items['items'][0]['id'], 'addTagTest')

    print 'Retrieving starred items'
    print g.get_starred_items(1)

    print 'Retrieving broadcast items with label %s ' % 'labelTest'
    i = g.get_broadcast_items(2, label='labelTest')
    print i

    # Renaming feed
    print 'Renaming feed:'
    print g.edit_feed_title('BBC FrontPage', new_feed['streamId'])

    # Add label to feed
    print "Adding label ('testLabel2') to %s feed" % new_feed['query']
    print g.add_label_to_feed(feed_title, new_feed['streamId'], 'testLabel2')
    print "Removing label ('testLabel2') from %s feed" % new_feed['query']
    print g.remove_label_from_feed(feed_title, new_feed['streamId'], 'te')

    # Get tag list
    print 'Retrieving list of tags'
    tags = g.get_tag_list()
    for t in tags['tags']:
        print t['id']

    print 'Making label public'
    print g.edit_folder_or_tag(tags['tags'][0]['id'], True)

    # Delete tag
    print 'Deleting tag %s ' % 'testLabel2'
    t = g.delete_tag('testLabel2')

    # Unsubscribe
    print 'Unsubscribing from feed'
    print g.unsubscribe_from_feed(feed_title, new_feed['streamId'])

    print 'exporting'
    print g.export_OPML()

if __name__ == '__main__':
    # pass in credentials
    usage({'username': '', 'password': '', 'client_id': ''})
