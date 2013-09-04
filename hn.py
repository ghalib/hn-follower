import json
import requests

class Comment:
    def __init__(self, item):
        # We only include the following fields from items
        self.user = item['username']
        self.text = item['text']
        self.comment_id = item['id']
        self.parent_id = item['parent_id']
        self.parent_sigid = item['parent_sigid']
        self.discussion = item['discussion']
        self.create_ts = item['create_ts']
        self.parent = self._get_parent_comment(self.parent_sigid,
                                               self.parent_id,
                                               self.discussion['id'])

    def to_backbone(self):
        """Convert comment to backbone.js model"""
        return {'author': self.user,
                'text': self.text,
                'date': self.create_ts,
                'parent': self.parent.__dict__ if self.parent is not None else None}

    def __str__(self):
        return "%s: %s : Posted on %s" % (self.user,
                                          self.text, self.create_ts)

    def _get_parent_comment(self, parent_sigid, parent_id,
                            discussion_id):
        """Returns the comment of id parent_id (None if there is no
        such comment). 

        Due to a quirk in the HNSearch API, we can only retrieve
        individual comments using the sigid."""
        if (parent_id == discussion_id):
            return None
        req_url = 'http://api.thriftdb.com/api.hnsearch.com/items/%s' % parent_sigid
        j = requests.get(req_url).json()
        if str(j.get('message')).startswith('Item not'):
            return None
        else:
            return ParentComment(j['username'], j['text'])

class ParentComment:
    def __init__(self, user, text):
        self.user = user
        self.text = text

    def __str__(self):
        return "%s: %s" % (self.user, self.text)

def params_dict_to_str(params):
    return '&'.join(('%s=%s' % (k, v)) for k, v in params.iteritems())

def get_hn_items(params):
    """Perform a search query for certain iteams, returning JSON
    result as dict."""
    search_url = 'http://api.thriftdb.com/api.hnsearch.com/items/_search?'
    j = requests.get(search_url + params_dict_to_str(params)).json()
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

def user_exists(username):
    """Check if username exists on HN"""
    api_url = 'http://api.thriftdb.com/api.hnsearch.com/users/_search?'
    params = {'filter[fields][username]': username,
              'limit': '1',
              'pretty_print': 'true'}
    results = requests.get(api_url +
                           params_dict_to_str(params)).json()["results"]
    return len(results) > 0

