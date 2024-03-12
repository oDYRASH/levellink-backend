from models import Profile, DiscordUser, Connection
from config import db


def userExist(discordUserId):

    user = Profile.query.filter_by(discord_user_id=discordUserId).first()

    return True if user else False


def majProfile(discord_user_data):
    user = Profile.query.filter_by(discord_user_id=discord_user_data["id"]).first()
    user.user.avatar = discord_user_data["avatar"]
    user.user.global_name = discord_user_data["username"]
    user.user.connections=[
        Connection(**conn) for conn in discord_user_data["connections"]
        ]
    db.session.commit()

    return True
def createUser(discordUser):

    newProfile = Profile(
        discord_user_id = discordUser['id'],
        user = DiscordUser(
            id=discordUser['id'],
            global_name=discordUser['username'],
            avatar=discordUser['avatar'],
            public_flags=discordUser['public_flags'],
            flags=discordUser['flags'],
            locale=discordUser['locale'],
            mfa_enabled=discordUser['mfa_enabled'],
            connections=[
                Connection(**conn) for conn in discordUser["connections"]
                ]
        )
    )

    db.session.add(newProfile)
    db.session.commit()

    return True


