import sys

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.escape import json_encode

import hn
import database

DB = database.DB()
SESSION_ID = "me"

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        self.render('comment_view.html', compress_whitespace=True)

class UserHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def put(self, user):
        if not hn.user_exists(user):
            sys.stderr.write("User '%s' does not exist\n" % user)
            return

        self.db.add_user(SESSION_ID, user)
        self.db.store_all(hn.get_most_recent_comments(user))

        # backbone.js's Collection's {wait: true} won't add the model
        # to the collection with an empty HTTP 200; only if JSON data
        # is returned
        self.write({"user": user})

    def delete(self, user):
        self.db.del_user(SESSION_ID, user)
        self.write({"user": user})

class UserSupplier(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        users = self.db.get_users(SESSION_ID)
        if users:
            self.write(self._userlist_to_json(users))
        
    def _userlist_to_json(self, users):
        """Convert Python list of users into backbone.js model JSON"""
        userlist = [{"name": user} for user in users]
        return json_encode(userlist)
        
class CommentSupplier(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, user):
        # Temporarily, always get the newest comments straight from
        # HNSearch rather than our DB. This will change when we
        # implement automatic periodic DB comment-population

        # comments = self.db.get_comments(user)
        comments = hn.get_most_recent_comments(user)
        comment_models = [comment.to_backbone() for comment in comments]
        self.write(json_encode(comment_models))

application = tornado.web.Application([
    (r'/', MainHandler, dict(db=DB)),
    (r'/comments/(\w+)', CommentSupplier, dict(db=DB)),
    (r'/users/(\w+)', UserHandler, dict(db=DB)),
    (r'/users', UserSupplier, dict(db=DB))
],
template_path='templates',
static_path='static', 
debug=True)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
