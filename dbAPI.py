from models import *
from config import db


def userExist(discordUserId):

    user = Profile.query.filter_by(discord_user_id=discordUserId).first()

    return True if user else False

def createUser(discordUser):

    newProfile = Profile(
        discord_user_id = discordUser['id'],
        user = DiscordUser(
            id=discordUser['id'],
            global_name=discordUser['global_name'],
            avatar=discordUser['avatar'],
            public_flags=discordUser['public_flags'],
            flags=discordUser['flags'],
            locale=discordUser['locale'],
            mfa_enabled=discordUser['mfa_enabled'],
            connections=[Connection(**conn) for conn in discordUser["connections"]]

        )
    )

    db.session.add(newProfile)
    db.session.commit()

    return True


