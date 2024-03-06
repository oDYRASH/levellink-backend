from flask import request, redirect , make_response
import secrets
from functools import wraps
import settings
import datetime


from config import db 
# Modèle pour stocker les jetons CSRF
class CSRFToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(db.BigInteger, unique=True, nullable=False)
    csrf_token = db.Column(db.String(32), nullable=False)

    def to_json(self):
        return {"id": self.id, "user_id": self.discord_user_id, "csrf_token": self.csrf_token}


def assign_CSRF_to_USER(discord_user_id) -> str:
    csrf_token = secrets.token_hex(16)  # Génère un jeton CSRF aléatoire

    #if token already exist
    token_enregistre = CSRFToken.query.filter_by(discord_user_id=discord_user_id).first()  
    if token_enregistre:
        token_enregistre.csrf_token = csrf_token
        db.session.commit()
        return csrf_token
    

    #else create a new one
    nouveau_token = CSRFToken(discord_user_id=discord_user_id, csrf_token=csrf_token)
    db.session.add(nouveau_token)
    db.session.commit()

    return csrf_token


def verifier_csrf_token_and_discord_user_id(discord_user_id, csrf_token):
    token_enregistre = CSRFToken.query.filter_by(discord_user_id=discord_user_id).first()
    if token_enregistre:
        return token_enregistre.csrf_token == csrf_token
    return False


def user_id_from_csrf(csrf_token):
    token_enregistre = CSRFToken.query.filter_by(csrf_token=csrf_token).first()
    if token_enregistre:
        return token_enregistre.user_id
    return False


def csrf_auth_required(f):

    @wraps(f)
    def decorateur(*args, **kwargs):
        csrf_token = request.cookies.get('csrf_token')

        #pas de Token
        if csrf_token == None : return "No csrf set in this session", 400 #redirect(settings.FRONTEND_BASE_ROUTE + "/login")
         
        token_enregistre = CSRFToken.query.filter_by(csrf_token=csrf_token).first()

        #bad Token
        if not token_enregistre : return "csrf NON valid", 401#redirect(settings.FRONTEND_BASE_ROUTE + "/login")    

        return f(token_enregistre, *args, **kwargs)
    
    return decorateur

def make_csrf_setting_response(csrf_token, live_time_in_days):

    # Définir le cookie CSRF dans la réponse
    max_age = live_time_in_days*24*60*60  #one year
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    
    response = make_response()
    response.set_cookie("csrf_token", csrf_token, max_age=max_age, expires=expires, domain='.levellink.lol')#'.levellink.lol'

    response.status_code = 200

    return response