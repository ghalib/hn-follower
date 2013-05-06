$(function() {
    var User = Backbone.Model.extend({
        defaults: {
            name: ""
        }
    });
    
    var UserList = Backbone.Collection.extend({
        model: User,
        url: '/users'
    });
    
    var UserView = Backbone.View.extend({
        tagName: "li",
        template: _.template($('#user-template').html()),
        
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
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
        },
        
        addUser: function(user) {
            var view = new UserView({model: user});
            this.$("#user-list").append(view.render().el);
        },
        
        createUser: function(e) {
            e.preventDefault(); // Prevent page reload on submit
            if (!this.input.val()) return;
            
            Users.create({name: this.input.val()});
            this.input.val('');
        }
    
    });
    var App = new AppView();
});


