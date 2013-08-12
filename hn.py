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

    def to_backbone(self):
        """Convert comment to backbone.js model"""
        return {'author': self.user,
                'text': self.text,
                'date': self.create_ts}

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

def get_most_recent_comments(user, num_comments=10):
    """Returns the 100 most recent comments by USER, sorted by time
    posted (newest to oldest), in the form of a list containing
    Comment objects."""
    params = {'filter[fields][type]': 'comment',
              'filter[fields][username]': user,
              'sortby': 'create_ts desc',
              'limit': str(num_comments),
              'pretty_print': 'true'}
    results = get_hn_items(params)['results']
    return sorted(map(lambda result: Comment(result['item']),
                      results),
                  key=lambda comment: comment.create_ts,
                  reverse=True)

def user_exists(user):
    """Returns a dictionary of the user's information if they exist"""
    api_url = 'http://api.thriftdb.com/api.hnsearch.com/users/_search?'

    params = {'filter[fields][username]': user,
              'limit': '1',
              'pretty_print': 'true'}
    
    results = requests.get(api_url +
                           params_dict_to_str(params)).json()["results"]

    return len(results) > 0

