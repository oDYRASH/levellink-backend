from config import db

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(100))

    def to_json(self):
        return {
            'name': self.name,
            'type': self.type,            
        }


discord_user_connection = db.Table('discord_user_connection',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('discord_user_id', db.String(18), db.ForeignKey('discord_user.id')),
    db.Column('connection_id', db.Integer, db.ForeignKey('connection.id'))
)

class DiscordUser(db.Model):
    id = db.Column(db.String(18), primary_key=True)
    global_name = db.Column(db.String(100))
    avatar = db.Column(db.String(100), nullable=True)
    public_flags = db.Column(db.Integer, nullable=True)
    flags = db.Column(db.Integer, nullable=True)
    locale = db.Column(db.String(10), nullable=True)
    mfa_enabled = db.Column(db.Boolean, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    connections = db.relationship('Connection', secondary='discord_user_connection', backref='discord_users')


    def to_json(self):
        return {
            'id': self.id,
            'global_name': self.global_name,
            'avatar': self.avatar,
            'public_flags': self.public_flags,
            'flags': self.flags,
            'locale': self.locale,
            'mfa_enabled': self.mfa_enabled,
            'connections': [connection.to_json() for connection in self.connections]  # Sérialiser les connexions en liste d'ID
        }

    def get_connections(self):
        return [connection.to_json() for connection in self.connections]

class Follows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.String(18), db.ForeignKey('profile.id'))
    followed_id = db.Column(db.String(18), db.ForeignKey('profile.id'))
    
    def to_json(self):
        return {
            "id":self.id,
            "follower_id":self.follower_id,
            "followed_id":self.followed_id
        }


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(db.String(18), db.ForeignKey('discord_user.id'))
    user = db.relationship('DiscordUser', backref='profile')
    follows = db.relationship('DiscordUser', secondary='follows', primaryjoin=discord_user_id == Follows.followed_id, secondaryjoin=discord_user_id == Follows.follower_id, backref='followed_by', cascade='all, delete-orphan', single_parent=True )
   
    def get_name(self):
        return self.user.global_name.capitalize()

    def get_LoL_name(self):

        nom_lol = None

        for game in self.user.get_connections():
            if game["type"] == "leagueoflegends":
                nom_lol = game["name"]
        
        return nom_lol

    def get_follows(self):
        print(self.follows)
        return [follow.id for follow in self.follows]

    def to_json(self):
        return {
            'discord_user_id': self.discord_user_id,
            'id': self.id,
            'user': self.user.to_json()
        }
    
    def follow(self, user):
        if not self.is_following(user):
            self.follows.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.follows.remove(user)
            return self

    def is_following(self, user):
        return user in self.follows



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    content = db.Column(db.Text)
    like = db.Column(db.Integer, default=0)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.String(18), db.ForeignKey('profile.discord_user_id'))
    author = db.relationship('Profile', backref='posts')
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    session_stats = db.Column(db.JSON, default={})
    image = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    like = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', secondary='post_comments', backref='posts')

    def to_json(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'author': self.author.to_json(), # Sérialiser l'auteur en 'global_name
            'title': self.title,
            'description': self.description,
            'session_stats': self.session_stats,
            'timestamp': self.timestamp,  
            'like': self.like,
            'comments': [comment.id for comment in self.comments],  # Sérialiser les commentaires en liste d'ID
        }


post_comments = db.Table('post_comments',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'))
)



#####################
#####################
#####################
#PAS UTILISES POUR LE MOMENT
# class Follows(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     follower_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
#     followed_id = db.Column(db.Integer, db.ForeignKey('profile.id'))

# class Stat(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255))
#     value = db.Column(db.Integer)

# class Embed(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     queue_id = db.Column(db.Integer)
#     time_ago = db.Column(db.Integer)
#     is_won = db.Column(db.Boolean)
#     game_duration = db.Column(db.Integer)
#     champion = db.Column(db.String(30))
#     summoner1_id = db.Column(db.Integer)
#     summoner2_id = db.Column(db.Integer)
#     main_rune = db.Column(db.Integer)
#     secondary_rune = db.Column(db.Integer)
#     items = db.Column(db.ARRAY(db.Integer))
#     stats = db.relationship('Stat', secondary='embed_stats', backref='embed')

# class EmbedStat(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     embed_id = db.Column(db.Integer, db.ForeignKey('embed.id'))
#     stat_id = db.Column(db.Integer, db.ForeignKey('stat.id'))

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     author_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
#     content = db.Column(db.Text)
#     like = db.Column(db.Integer, default=0)

# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     author_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
#     title = db.Column(db.String(255))
#     description = db.Column(db.Text)
#     embed_id = db.Column(db.Integer, db.ForeignKey('embed.id'))
#     timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
#     like = db.Column(db.Integer, default=0)
#     comments = db.relationship('Comment', secondary='post_comments', backref='posts')

# class PostComment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
#     comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

