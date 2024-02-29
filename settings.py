import os

from dotenv import load_dotenv

load_dotenv()

SOCIAL_AUTH_DISCORD_KEY = os.getenv("SOCIAL_AUTH_DISCORD_KEY")
SOCIAL_AUTH_DISCORD_SECRET = os.environ.get("SOCIAL_AUTH_DISCORD_SECRET")
SOCIAL_AUTH_DISCORD_REDIRECT_URI = os.environ.get("SOCIAL_AUTH_DISCORD_REDIRECT_URI")