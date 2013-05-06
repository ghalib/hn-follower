import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpserver

import hn
import database

DB = database.DB()
USERS = DB.r.keys()

def read_users(usersfile):
    users = []
    for line in open(usersfile):
        user = line.strip()
        users.append(user)
    return users

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('comment_view.html')

class UserHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db
        
    def post(self):
        j = tornado.escape.json_decode(self.request.body)
        user = j['name']
        print 'Received POST for user %s' % user

class UserSupplier(tornado.web.RequestHandler):
    def initialize(self, users):
        self.users = users

    def get(self):
        userdict = {'users': self.users}
        self.write(userdict)

class CommentSupplier(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, user):
        # TODO: jsonify as with UserSupplier
        return db.get_comments(user)

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/get_all_users', UserSupplier, dict(users=USERS)),
    (r'/get_comments/(\w+)', CommentSupplier, dict(db=DB)),
    (r'/users', UserHandler, dict(db=DB))
],
template_path='templates',
static_path='static', 
debug=True)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
