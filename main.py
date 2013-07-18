import sys

import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpserver

import hn
import database

DB = database.DB()
SESSION_ID = "me"

def read_users(usersfile):
    users = []
    for line in open(usersfile):
        user = line.strip()
        users.append(user)
    return users

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        users = self.db.get_users(SESSION_ID)
        self.render('comment_view.html', compress_whitespace=True,
                    users=users)

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

class CommentSupplier(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, user):
        # TODO: jsonify as with UserSupplier
        return self.db.get_comments(user)

application = tornado.web.Application([
    (r'/', MainHandler, dict(db=DB)),
    (r'/comments/(\w+)', CommentSupplier, dict(db=DB)),
    (r'/users/(\w+)', UserHandler, dict(db=DB))
],
template_path='templates',
static_path='static', 
debug=True)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
