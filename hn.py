import json
import requests

class Comment:
    def __init__(self, item):
        # We only include the following fields from items
        self.user = item['username']
        self.text = item['text']
        self.comment_id = item['id']
        self.parent_id = item['parent_id']
        self.discussion = item['discussion']
        self.create_ts = item['create_ts']

    def __str__(self):
        return "%s: %s : Posted on %s" % (self.user,
                                          self.text, self.create_ts)

def params_dict_to_str(params):
    return '&'.join(('%s=%s' % (k, v)) for k, v in params.iteritems())

def get_hn_items(params):
    """Perform a search query for certain iteams, returning JSON
    result as dict."""
    api_url = 'http://api.thriftdb.com/api.hnsearch.com/items/_search?'
    j = requests.get(api_url + params_dict_to_str(params)).json()
    return j

def get_most_recent_comments(user):
    """Returns the 100 most recent comments by USER, sorted by time
    posted (newest to oldest), in the form of a list containing
    Comment objects."""
    params = {'filter[fields][type]': 'comment',
              'filter[fields][username]': user,
              'sortby': 'create_ts desc',
              'limit': '100',
              'pretty_print': 'true'}
    results = get_hn_items(params)['results']
    return sorted(map(lambda result: Comment(result['item']),
                      results),
                  key=lambda comment: comment.create_ts)

