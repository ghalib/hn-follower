import pickle
# Find the best implementation available on this platform
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import redis

class Pickler(object):
    """Simple helper class to use pickle with a reusable string buffer
    object"""
    def __init__(self):
        self.tmpstr = StringIO()

    def __del__(self):
        # close the StringIO buffer and delete it
        self.tmpstr.close()
        del self.tmpstr

    def dump(self, obj):
        """Pickle an object and return the pickled string"""
        # empty current buffer
        self.tmpstr.seek(0,0)
        self.tmpstr.truncate(0)
        # pickle obj into the buffer
        pickle.dump(obj, self.tmpstr)
        # move the buffer pointer to the start
        self.tmpstr.seek(0,0)
        # return the pickled buffer as a string
        return self.tmpstr.read()

    def load(self, obj):
        """Load a pickled object string and return the object"""
        # empty the current buffer
        self.tmpstr.seek(0,0)
        self.tmpstr.truncate(0)
        # load the pickled obj string into the buffer
        self.tmpstr.write(obj)
        # move the buffer pointer to start
        self.tmpstr.seek(0,0)
        # load the pickled buffer into an object
        return pickle.load(self.tmpstr)

class DB(object):
    def __init__(self, host=None, port=None, db=None):
        """Establishes a connection to the specified Redis db.
        Example: db = DB('localhost', 6379, 0)"""
        self.pickler = Pickler()
        self.host = 'localhost' if host is None else host
        self.port = 6379 if port is None else port
        self.db = 0 if db is None else db
        self.r = redis.StrictRedis(self.host, self.port, self.db)

    def store(self, comment):
        """Stores a comment in a Redis set, keyed by username."""
        payload = self.pickler.dump(comment)
        return self.r.sadd(comment.user, payload)

    def store_all(self, comments):
        """Stores all comments in a collection."""
        for comment in comments:
            self.store(comment)

    def add_user(self, session_id, user):
        """Given a user to follow, adds it to the list of follow
        targets"""
        if self.r.zscore(session_id, user) is None:
            order = self.r.zcard(session_id)
            self.r.zadd(session_id, order, user)
            return True
        else:
            return False

    def del_user(self, session_id, user):
        self.r.zrem(session_id, user)
        return True

    def get_users(self, session_id):
        return self.r.zrange(session_id, 0, -1)

    def get_comments(self, user):
        """Given a username key, returns a list of comments from
        Redis, sorted by time posted to HN in most to least-recent."""
        redis_set = self.r.smembers(user)
        if not redis_set:
            raise KeyError("Redis: No such user")
        comments = [self.pickler.load(c) for c in redis_set]
        sorted_comments = sorted(comments, 
                                 key=lambda comment: comment.create_ts,
                                 reverse=True)
        return sorted_comments
