$(function() {
    var User = Backbone.Model.extend({
        defaults: {
            name: ""
        },

        idAttribute: "name"
    });
    
    var UserList = Backbone.Collection.extend({
        model: User,
        url: '/users'
    });
    
    var Comment = Backbone.Model.extend({
        defaults: {
            author: "",
            text: "",
            date: "",
            parent: null
        }
    });

    var CommentList = Backbone.Collection.extend({
        model: Comment,

        initialize: function(models, options) {
            this.author = options.author;
        },

        url: function() {
            return '/comments/' + this.author;
        }
    });

    UserList.prototype.contains = function(name) {
        return this.any(function(_user) {
            return _user.get("name") === name;
        });
    };

    var UserView = Backbone.View.extend({
        tagName: "li",

        template: _.template($('#user-template').html()),
        
        events: {
            "click a.destroy": "clear"
        },

        initialize: function() {
            this.listenTo(this.model, 'destroy', this.remove);
        },

        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        },

        clear: function() {
            var m = this.model;
            this.$el.fadeOut(400, function() {
                m.destroy();
            });
        }
    });
    
    var CommentListView = Backbone.View.extend({
        tagName: "div",

        attributes: {
            "class": "tab-pane"
        },

        template: _.template($('#comment-list-template').html()),

        initialize: function() {
            this.$el.attr("id", this.model.get("name"));
            this.listenTo(this.model, 'destroy', this.remove);
        },

        render: function() {
            this.$el.html(this.template());
            return this;
        }
    });

    var CommentView = Backbone.View.extend({
        tagName: "li",

        render: function() {
            this.$el.html(this.model.get('text'));
            return this;
        }

    });

    var Users = new UserList();
    
    var AppView = Backbone.View.extend({
        el: $("#app"),
        
        events: {
            "submit #add-user": "createUser"
        },
        
        initialize: function() {
            this.input = this.$("input");
            this.listenTo(Users, 'add', this.addUser);
            this.listenTo(Users, 'reset', this.addAllUsers);

            Users.fetch();
        },
        
        addUser: function(user) {
            var userView = new UserView({model: user});
            this.$("#user-list").append(userView.render().el);
            var commentListView = new CommentListView({model: user});
            this.$(".tab-content").append(commentListView.render().el);
            this.addAllComments(user);
        },
        
        addAllUsers: function() {
            Users.each(this.addUser, this);
        },

        addComment: function(comment) {
            var commentView = new CommentView({model: comment});
            var commentListNode = $("#" + comment.get("author") + " ul");
            commentListNode.append(commentView.render().el);
        },

        addAllComments: function(user) {
            var comments = new CommentList([], {author: user.get("name")});
            addComment = this.addComment;
            comments.fetch({success: function() {
                comments.each(addComment, this);
            }});
        },

        createUser: function(e) {
            e.preventDefault(); // Prevent page reload on submit
            var user = this.input.val().trim();
            this.input.val('');
            if (!user || Users.contains(user)) return;
            // {wait: true} means don't create a view in browser until
            // we get a response from server
            Users.create({name: user}, {wait: true});
        }
    
    });
    var App = new AppView();
});


