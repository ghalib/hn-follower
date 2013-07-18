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
    
    UserList.prototype.contains = function(name) {
        return this.any(function(_user) {
            return _user.get("name") === name;
        });
    };

    var UserView = Backbone.View.extend({
        tagName: "li",

        template: _.template($('#user-template').html()),
        
        events: {
            "click a.destroy" : "clear"
        },

        initialize: function() {
            this.listenTo(this.model, 'destroy', this.remove);
        },

        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        },

        clear: function() {
            this.model.destroy();
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

            // Populate Users from the page instead of making an Ajax
            // call
            var userCollection = $(".user").map(function() {
                var name = $(this).text();
                return {"name": name};
            }).get();
            Users.reset(userCollection);
        },
        
        addUser: function(user) {
            var view = new UserView({model: user});
            this.$("#user-list").append(view.render().el);
        },
        
        createUser: function(e) {
            e.preventDefault(); // Prevent page reload on submit
            var user = this.input.val().trim();
            this.input.val('');
            if (!user || Users.contains(user)) return;

            Users.create({name: user}, {wait: true});
        }
    
    });
    var App = new AppView();
});


