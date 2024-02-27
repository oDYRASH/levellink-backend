from config import db


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
        }


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
    db.Column('discord_user_id', db.BigInteger, db.ForeignKey('discord_user.id')),
    db.Column('connection_id', db.Integer, db.ForeignKey('connection.id'))
)

class DiscordUser(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
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


class Follows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('profile.id'))

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(db.BigInteger, db.ForeignKey('discord_user.id'))
    user = db.relationship('DiscordUser', backref='profile')
    follows = db.relationship('Profile', secondary='follows', primaryjoin=id == Follows.followed_id, secondaryjoin=id == Follows.follower_id, backref='followed_by')
   
    def to_json(self):
        return {
            'discord_user_id': self.discord_user_id,
            'id': self.id,
            'user': self.user.to_json()
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    content = db.Column(db.Text)
    like = db.Column(db.Integer, default=0)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    like = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', secondary='post_comments', backref='posts')

    def to_json(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'title': self.title,
            'description': self.description,
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
