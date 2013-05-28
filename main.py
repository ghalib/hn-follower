import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpserver

import hn
import database

DB = database.DB()

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
        session_id = "me"
        users = self.db.get_users(session_id)
        self.render('comment_view.html', compress_whitespace=True,
                    users=users)

class UserHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db
        
    def put(self, user):
        self.db.add_user("me", user)
        self.db.store_all(hn.get_most_recent_comments(user))

        # backbone.js's Collection's {wait: true} won't add the model
        # to the collection with an empty HTTP 200; only if JSON data
        # is returned
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
