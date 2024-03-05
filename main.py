from flask import request, jsonify, url_for, redirect
from config import app, db
from models import Profile, Follows, Post
from discordAPI import exchange_code
from dbAPI import *
from sqlalchemy import desc
import json
from functools import wraps
import settings
import auth



@app.route("/logout", methods=["GET"])
def delete_csrf():
    response = redirect(settings.FRONTEND_BASE_ROUTE + "/login")
    response.delete_cookie("csrf_token")
    return response, 200

###############################################################################################
###############################################################################################
##################################### AUTH USER METHODS #######################################
###############################################################################################
###############################################################################################

@app.route("/userPosts", methods=["GET"])
def get_user_posts():
    csrf_token = request.cookies.get('csrf_token')
    token_enregistre = auth.CSRFToken.query.filter_by(csrf_token=csrf_token).first()

    if token_enregistre:

        user_Profile = Profile.query.filter_by(user_id=token_enregistre.user_id).first()
        posts = Post.query.filter_by(author_id=user_Profile.id).order_by(desc(Post.timestamp)).limit(10).all()
        json_posts = [post.to_json() for post in posts]

        return json_posts, 200

    return "Invalid CSRF token", 401


@app.route("/auth/user", methods=["GET"])
@auth.csrf_auth_required
def get_authed_user():

    csrf_token = request.cookies.get('csrf_token')
    print("CSRF TOKEN :", csrf_token)
    token_enregistre = auth.CSRFToken.query.filter_by(csrf_token=csrf_token).first()

    if token_enregistre:
        user_Profile = Profile.query.filter_by(user_id=token_enregistre.user_id).first()
        return user_Profile.to_json(), 200
    
    return "Invalid CSRF token", 403
    
###############################################################################################
###############################################################################################
###################################### ADMIN THINGS  ##########################################
###############################################################################################
###############################################################################################

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)



@app.route("/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples

    return ''.join(route+"<br/>" for route in [link[0] for link in links])


@app.route("/profiles", methods=["GET"])
def get_profiles():
    profiles = Profile.query.all()
    json_profiles = list(map(lambda x: x.to_json(), profiles))
    return jsonify({"profiles": json_profiles})


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    json_posts = list(map(lambda x: x.to_json(), posts))
    return jsonify({"posts": json_posts})


@app.route("/createPost", methods=["GET"])
def createPost(token_enregistre):

    print("CATCHED after deecoration : ", token_enregistre)#token_enregistre.user_id) 

    newPost = Post(
        author_id = token_enregistre.user_id,
        title = request.json.get("title"),
        description =  request.json.get("description")
    )

    db.session.add(newPost)
    db.session.commit()

    return jsonify(newPost.to_json()), 201


@app.route("/authUser", methods=["GET"])
def authUser():
    
    # Récupérer l'access_token de l'URL
    code = request.args.get('code')

    user_data = exchange_code(code)

    if not user_data : 
        return "Failed to get discord User"
    # Vérifier si le paramètre "access_token" est présent

    if(not userExist(user_data["id"])) :
        userCreated = createUser(user_data)
        return  redirect(settings.FRONTEND_BASE_ROUTE)
    
    return user_data


@app.route("/get_posts_by_user_ids", methods=["POST"])
def get_posts_by_user_ids():
    user_ids = request.json.get("user_ids")  # Récupérer la liste des identifiants d'utilisateur depuis la requête POST
    # Utiliser une seule requête pour récupérer les 2 derniers posts pour chaque utilisateur spécifié
    posts = []
    limit_per_user = round( 30 / len(user_ids) ) +1

    for user_id in user_ids:
        user_posts = Post.query.filter_by(author_id=user_id).order_by(desc(Post.timestamp)).limit(limit_per_user).all()
        posts.extend(user_posts)
    
    serialized_posts = [post.to_json() for post in posts]  # Sérialiser les posts en JSON
    
    return jsonify(serialized_posts)  # Retourner les posts sous forme JSON

@app.route('/follow', methods=['POST'])
def follow_user():

    data = request.json
    user_follower_id = data.get('user_follower_id')
    user_followed_id = data.get('user_followed_id')

    if user_follower_id is None or user_followed_id is None:
        return jsonify({'error': 'user_follower_id and user_followed_id must be provided'}), 400

    user_follower = Profile.query.filter_by(id=user_follower_id).first()
    user_followed = Profile.query.filter_by(id=user_followed_id).first()

    if user_follower is None or user_followed is None:
        return jsonify({'error': 'One or both users do not exist'}), 404

    if user_followed_id in user_follower.get_follows():
        return jsonify({'error': 'Already Following'}), 404

    new_follow = Follows(follower_id=user_follower_id, followed_id=user_followed_id)
    
    db.session.add(new_follow)
    db.session.commit()

    return user_follower.get_follows()


@app.route('/unfollow', methods=['POST'])
def unfollow_user():

    data = request.json
    user_follower_id = data.get('user_follower_id')
    user_followed_id = data.get('user_followed_id')

    if user_follower_id is None or user_followed_id is None:
        return jsonify({'error': 'user_follower_id et user_followed_id doivent être fournis'}), 400

    user_follower = Profile.query.filter_by(id=user_follower_id).first()
    user_followed = Profile.query.filter_by(id=user_followed_id).first()

    if user_follower is None or user_followed is None:
        return jsonify({'error': 'One or both users do not exist'}), 404


    follow_relationship = Follows.query.filter_by(follower_id=user_follower_id, followed_id=user_followed_id).first()
    
    if follow_relationship is None:
        return jsonify({'message': 'L\'utilisateur {} ne suit pas l\'utilisateur {}'.format(user_follower_id, user_followed_id)}), 404

    db.session.delete(follow_relationship)
    db.session.commit()

    return jsonify({'message': 'L\'utilisateur {} ne suit plus l\'utilisateur {}'.format(user_follower_id, user_followed_id)}), 200


@app.route('/userfollows', methods=['GET'])
def getFollows():
    parametres_url = request.args

    userId = parametres_url['userId']

    USER = Profile.query.filter_by(id=userId).first()

    if not USER: 
        return jsonify({"ERROR":"NO USER HAVE THIS ID"}), 404

    return USER.get_follows()





@app.route('/search-user', methods=['GET'])
def get_user_by_partial_name():
    # Recherche des profils d'utilisateurs correspondant au nom partiel
    parametres_url = request.args
    partialName = parametres_url['partialName']

    if partialName == "":
        return []
        

    # Recherche des profils d'utilisateurs correspondant au nom partiel
    searchResults = Profile.query.join(DiscordUser).filter(DiscordUser.global_name.ilike(f"%{partialName}%")).limit(5).all()

    return [{"id": str(profile.discord_user_id), "avatar": profile.user.avatar, "name": profile.user.global_name.capitalize()} for profile in searchResults]


@app.route('/dsoqiufhdsqiopugfhjdshjgsdqpiugdsqivb', methods=['GET'])
def _():
    Profile.query.delete()

# Confirmer la suppression en effectuant un commit
    db.session.commit()

    s = Profile.query.all()
    return [profile.to_json() for profile in s]

@app.route('/sqfhoiudsqnfaazsfdfdddddddddddddddd', methods=['GET'])
def _ok():
    DiscordUser.query.delete()

# Confirmer la suppression en effectuant un commit
    db.session.commit()

    s = DiscordUser.query.all()
    return [profile.to_json() for profile in s]



@app.route('/followconnection', methods=['GET'])
def gf():

    fs = Follows.query.all()
    return [fj.to_json() for fj in fs]

@app.route('/resetdb', methods=['GET'])
def clear_data():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        db.session.execute(table.delete())
    db.session.commit()

    return "OK"

@app.route('/get-table-content', methods=["GET"])
def getTableContent():
    tablename = request.args['tableName']

    try:

        all_table = db.metadata.sorted_tables

        table = next((table for table in all_table if table.name == tablename), None)
        
        if table != None:
            # Créez une classe modèle pour la table
            class Model(db.Model):
                __table__ = table
            
            # Récupérez le contenu de la table en utilisant la classe modèle
            table_content = Model.query.all()

            print(table_content)
            return [item.to_json() for item in table_content]

        return f"NO TABLE FOUND FOR {tablename}"
        # theTable= 
        # theTable.query.all()
        # return [fj.to_json() for fj in fs]
    except (KeyError, json.JSONDecodeError) as e:
        return f"ERROR MEET {e}"

##########TESTS####################
@app.route("/need_csrf")
def test():

    csrf_token = request.cookies.get('csrf_token')
    print(csrf_token)

    return f"csrf_token = {csrf_token}"

@app.route("/get_csrf")
def csrf_T():
    
    csrf_token = auth.assign_CSRF_to_USER(123456789)
    print(csrf_token)
    response = auth.make_csrf_setting_response(csrf_token, 90)
    response.text = csrf_token
    return response


##############League of Legends API####################
from lolAPI import *
# Route Summoner: /summoner?region=<region>&name=<summoner_name>
@app.route('/summoner', methods=['GET'])
async def summoner():
    region = request.args.get('region')
    name = request.args.get('name')
    summoner_data = await get_summoner(region, name)
    return jsonify(summoner_data)

# Route Rank: /rank?region=<region>&id=<summoner_id>
@app.route('/rank', methods=['GET'])
async def rank():
    region = request.args.get('region')
    id = request.args.get('id')
    rank_data = await get_rank(region, id)
    return jsonify(rank_data)

# Route Mastery: /mastery?region=<region>&id=<summoner_id>
@app.route('/mastery', methods=['GET'])
async def mastery():
    region = request.args.get('region')
    id = request.args.get('id')
    mastery_data = await get_mastery_points(region, id)
    return jsonify(mastery_data)

# Route Matches: /matches?region=<region>&puuid=<summoner_puuid>&page=<page_number>
@app.route('/matches', methods=['GET'])
async def matches():
    region = request.args.get('region')
    puuid = request.args.get('puuid')
    page = request.args.get('page', 17, type=int)
    matches_data = await get_all_matches(region, puuid, page)
    return jsonify(matches_data)

# Route Match: /match?region=<region>&match_id=<match_id>
@app.route('/match', methods=['GET'])
async def match():
    region = request.args.get('region')
    match_id = request.args.get('match_id')
    match_data = await get_match(region, match_id)
    return jsonify(match_data)

# Route Session Games: /session_games?lol_user_name=<summoner_name>
@app.route('/session_games', methods=['GET'])
async def session_games():
    lol_user_name = request.args.get('lol_user_name')
    session_games_data = await get_session_games(lol_user_name)
    return jsonify(session_games_data)

# Route User Rank: /user_rank?lol_user_name=<summoner_name>
@app.route('/user_rank', methods=['GET'])
async def user_rank():
    lol_user_name = request.args.get('lol_user_name')
    user_rank_data = await get_user_rank(lol_user_name)
    return jsonify(user_rank_data)


# @app.route("/create_contact", methods=["POST"])
# def create_contact():
#     first_name = request.json.get("firstName")
#     last_name = request.json.get("lastName")
#     email = request.json.get("email")

#     if not first_name or not last_name or not email:
#         return (
#             jsonify({"message": "You must include a first name, last name and email"}),
#             400,
#         )

#     new_contact = Contact(first_name=first_name, last_name=last_name, email=email)
#     try:
#         db.session.add(new_contact)
#         db.session.commit()
#     except Exception as e:
#         return jsonify({"message": str(e)}), 400

#     return jsonify({"message": "User created!"}), 201


# @app.route("/update_contact/<int:user_id>", methods=["PATCH"])
# def update_contact(user_id):
#     contact = Contact.query.get(user_id)

#     if not contact:
#         return jsonify({"message": "User not found"}), 404

#     data = request.json
#     contact.first_name = data.get("firstName", contact.first_name)
#     contact.last_name = data.get("lastName", contact.last_name)
#     contact.email = data.get("email", contact.email)

#     db.session.commit()

#     return jsonify({"message": "Usr updated."}), 200


# @app.route("/delete_contact/<int:user_id>", methods=["DELETE"])
# def delete_contact(user_id):
#     contact = Contact.query.get(user_id)

#     if not contact:
#         return jsonify({"message": "User not found"}), 404

#     db.session.delete(contact)
#     db.session.commit()

#     return jsonify({"message": "User deleted!"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0")
