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

###############################################################################################
###############################################################################################
##################################### AUTH MANAGEMENT ROUTES ########################################
###############################################################################################
###############################################################################################
@app.route("/authenticate-user", methods=["GET"])
def authUser():

    #get the code from the request
    discordAuthCode = request.args.get('code')

    #get the user data from the code
    discord_user_data = exchange_code(discordAuthCode)

    if discord_user_data == None:
        return 'Auth Failed', 401

    csrf_token = auth.assign_CSRF_to_USER(discord_user_data["id"])
    response   = auth.make_csrf_setting_response(csrf_token, 90)

    if not userExist(discord_user_data["id"]):
        createUser(discord_user_data)
        response.headers['Location'] = settings.FRONTEND_BASE_ROUTE
        response.status_code = 302

        return response

    else:
        response.headers['Location'] = settings.FRONTEND_BASE_ROUTE
        response.status_code = 302

        return response


###############################################################################################
###############################################################################################
##################################### /AUTH ROUTES ############################################
###############################################################################################
###############################################################################################

#get the authed user
@app.route("/auth/user", methods=["GET"])
@auth.csrf_auth_required
def get_authed_user(token_enregistre):

    if token_enregistre:
        user_Profile = Profile.query.filter_by(discord_user_id=token_enregistre.discord_user_id).first()
        profile = user_Profile.to_json()
        
        #getting follows
        follow_connection = Follows.query.filter_by(follower_id=token_enregistre.discord_user_id).all()
        followed_user_array = [str(follow.followed_id) for follow in follow_connection]
        followed_user_array.append(str(token_enregistre.discord_user_id))

        profile["follows"] = followed_user_array

        #getting followers
        coonection = Follows.query.filter_by(followed_id=token_enregistre.discord_user_id).all()
        profile["followers"] = [str(follow.follower_id) for follow in coonection] 

        return profile, 200

    return "Invalid CSRF token", 403


#logout authed user
@app.route("/logout", methods=["GET"])
@auth.csrf_auth_required
def delete_csrf(token_enregistre):

    #dellet the CSRF from the database
    token_enregistre.delete()
    db.session.commit()

    response = redirect(settings.FRONTEND_BASE_ROUTE + "/login")
    response.delete_cookie("csrf_token")
    return response, 302


#get the posts of the authed user
@app.route("/auth/user/posts", methods=["GET"])
@auth.csrf_auth_required
def get_authed_user_posts(token_enregistre):

    if token_enregistre:

        user_Profile = Profile.query.filter_by(discord_user_id=token_enregistre.discord_user_id).first()
        posts = Post.query.filter_by(author_id=user_Profile.id).order_by(desc(Post.timestamp)).limit(10).all()
        json_posts = [post.to_json() for post in posts]

        return json_posts, 200

    return "Invalid CSRF token", 401


#get the follows of the authed user
@app.route("/auth/user/follow", methods=["GET"])
@auth.csrf_auth_required
def get_user_follow(token_enregistre):
    
        if token_enregistre:
            follow_connection = Follows.query.filter_by(follower_id=token_enregistre.discord_user_id).all()
            followed_user_array = [str(follow.followed_id) for follow in follow_connection]
            followed_user_array.append(str(token_enregistre.discord_user_id))
            return jsonify(followed_user_array), 200
            # user_Profile = Profile.query.filter_by(discord_user_id=token_enregistre.discord_user_id).first()
            # followed_users = user_Profile.get_follows()
            # return jsonify(followed_users), 200
    
        return "Invalid CSRF token", 401


#get the followers of the authed user
@app.route("/auth/user/follower", methods=["GET"])
@auth.csrf_auth_required
def get_user_follwer(token_enregistre):
    
        if token_enregistre:
            #in follow find where followed_id = token_enregistre.discord_user_id and return array of follower_id
            coonection = Follows.query.filter_by(followed_id=token_enregistre.discord_user_id).all()
            follower_array = [str(follow.follower_id) for follow in coonection]

            return jsonify(follower_array), 200
    
        return "Invalid CSRF token", 401


#unfollow a user
@app.route('/auth/user/unfollow-user/<string:user_id>', methods=['GET'])
@auth.csrf_auth_required
def unfollow_user(token_enregistre, user_id):

    #finding the follow connection where follower is the authed user and followed is the user to unfollow
    follow_relationship = Follows.query.filter_by(follower_id=token_enregistre.discord_user_id, followed_id=user_id).first()
    #if the follow connection exist
    if follow_relationship:
        #delete the follow connection
        db.session.delete(follow_relationship)
        db.session.commit()

        #use unfollow methode on profile
        user_follower = Profile.query.filter_by(discord_user_id=token_enregistre.discord_user_id).first()
        # user_follower.unfollow(user_id)
        return "OK", 200

    return "No follow connection found", 404


#follow a user
@app.route('/auth/user/follow-user/<string:user_id>', methods=['GET'])
@auth.csrf_auth_required
def follow_user(token_enregistre, user_id):

    user_follower = Profile.query.filter_by(discord_user_id=token_enregistre.discord_user_id).first()
    user_followed = Profile.query.filter_by(discord_user_id=user_id).first()

    if user_follower is None or user_followed is None:
        return jsonify({'error': 'One or both users do not exist'}), 404

    follow_already_exist = Follows.query.filter_by(follower_id=user_follower.discord_user_id, followed_id=user_followed.discord_user_id).first()

    if follow_already_exist:
        return jsonify({'error': 'Already Following'}), 404

    new_follow = Follows(follower_id=user_follower.discord_user_id, followed_id=user_followed.discord_user_id)
    
    db.session.add(new_follow)
    db.session.commit()

    # user_follower.follow(user_id)


    #say ok and user x now following user y
    return jsonify({'message': f'Now following user {user_followed.discord_user_id}'}), 200

##LEAGUE OF LEGENDS API 
@app.route('/auth/user/lol/last-session', methods=['GET'])
@auth.csrf_auth_required
def get_summoner_matches(token_enregistre):

    user = Profile.query.filter_by(discord_user_id=token_enregistre.discord_user_id).first()
    
    lol_name = user.get_LoL_name()

    if lol_name:

        return get_session_games(lol_name), 200

    return "Invalid CSRF token", 401
###############################################################################################
###############################################################################################
##################################### /USER ROUTES ############################################
###############################################################################################
###############################################################################################


#get a user by id
@app.route("/user/<string:user_id>", methods=["GET"])
def get_user(user_id):

    user_Profile = Profile.query.filter_by(discord_user_id=user_id).first()

    if user_Profile:

        profile = user_Profile.to_json()
        #getting follows
        follow_connection = Follows.query.filter_by(follower_id=user_id).all()
        followed_user_array = [str(follow.followed_id) for follow in follow_connection]
        followed_user_array.append(str(user_id))

        profile["follows"] = followed_user_array

        #getting followers
        coonection = Follows.query.filter_by(followed_id=user_id).all()
        profile["followers"] = [str(follow.follower_id) for follow in coonection]

        return profile, 200

    return "No user with this id", 404


#get the posts of a user
@app.route("/user/<string:user_id>/posts", methods=["GET"])
def get_user_posts(user_id):
            
    user_Profile = Profile.query.filter_by(discord_user_id=user_id).first()

    if user_Profile:
        posts = Post.query.filter_by(author_id=user_Profile.discord_user_id).order_by(desc(Post.timestamp)).limit(10).all()
        json_posts = [post.to_json() for post in posts]

        return json_posts, 200

    return "No user with this id", 404


#get the followers of a user
@app.route("/user/<string:user_id>/followers", methods=["GET"])
def get_user_followers(user_id):
            
    user_Profile = Profile.query.filter_by(discord_user_id=user_id).first()

    if user_Profile:
        follow_connection = Follows.query.filter_by(followed_id=user_id).all()
        follower_array = [str(follow.follower_id) for follow in follow_connection]

        return jsonify(follower_array), 200

    return "No user with this id", 404


#get the follows of a user
@app.route("/user/<string:user_id>/follows", methods=["GET"])
def get_user_follows(user_id):
                
    user_Profile = Profile.query.filter_by(discord_user_id=user_id).first()

    if user_Profile:
        follow_connection = Follows.query.filter_by(follower_id=user_id).all()
        followed_user_array = [str(follow.followed_id) for follow in follow_connection]

        return jsonify(followed_user_array), 200

    return "No user with this id", 404


#get user by partial name
@app.route("/user/search-by-partialname/<string:partialname>", methods=["GET"])
def get_user_by_name(partialname):

    if partialname == "":
        return []

    # Recherche des profils d'utilisateurs correspondant au nom partiel
    searchResults = Profile.query.join(DiscordUser).filter(DiscordUser.global_name.ilike(f"%{partialname}%")).limit(5).all()

    return [{"id": str(profile.discord_user_id), "avatar": profile.user.avatar, "name": profile.user.global_name.capitalize()} for profile in searchResults]


##############################################################################
##############################################################################
############################# POSTS ROUTES ###################################
##############################################################################
##############################################################################


#get all posts
@app.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    json_posts = list(map(lambda x: x.to_json(), posts))
    return jsonify({"posts": json_posts})


#create a post
@app.route("/post/create", methods=["POST"])
@auth.csrf_auth_required
def createPost(token_enregistre):

    newPost = Post(
        author_id = token_enregistre.discord_user_id,
        title = request.json.get("title"),
        description =  request.json.get("description")
    )

    db.session.add(newPost)
    db.session.commit()

    return jsonify(newPost.to_json()), 201

#get post by [user_id, user_id, user_id, user_id]
@app.route("/post/by-author/<path:author_ids_str>", methods=["GET"])
def get_posts_by_authors(author_ids_str):
    # Supprimer les crochets et diviser la chaîne pour obtenir les identifiants

    print(author_ids_str)

    author_ids_str = author_ids_str.strip("[]")
    author_ids = [str(id) for id in author_ids_str.split(',')]
    posts = []

    limit_per_user = round( 30 / len(author_ids) ) +1

    for user_id in author_ids:
        user_posts = Post.query.filter_by(author_id=user_id).order_by(desc(Post.timestamp)).limit(limit_per_user).all()
        posts.extend(user_posts)
    
    serialized_posts = [post.to_json() for post in posts]  # Sérialiser les posts en JSON
    
    return jsonify(serialized_posts)  # Retourner les posts sous forme JSON

# @app.route('/search-user', methods=['GET'])
# def get_user_by_partial_name():
#     # Recherche des profils d'utilisateurs correspondant au nom partiel
#     parametres_url = request.args
#     partialName = parametres_url['partialName']

#     if partialName == "":
#         return []

#     # Recherche des profils d'utilisateurs correspondant au nom partiel
#     searchResults = Profile.query.join(DiscordUser).filter(DiscordUser.global_name.ilike(f"%{partialName}%")).limit(5).all()

#     return [{"id": str(profile.discord_user_id), "avatar": profile.user.avatar, "name": profile.user.global_name.capitalize()} for profile in searchResults]



# ##########TESTS####################
# @app.route("/need_csrf")
# def test():

#     csrf_token = request.cookies.get('csrf_token')
#     print(csrf_token)

#     return f"csrf_token = {csrf_token}"

# @app.route("/get_csrf")
# def csrf_T():
    
#     csrf_token = auth.assign_CSRF_to_USER(123456789)
#     print(csrf_token)
#     response = auth.make_csrf_setting_response(csrf_token, 90)
#     response.headers['Location'] = "http://127.0.0.1:5173/"
#     response.status_code = 302

#     return response

###############################################################################################
###############################################################################################
###################################### ADMIN THINGS  ##########################################
###############################################################################################
###############################################################################################

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

#return all routes
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


#get all csrf tokens
@app.route("/csrf", methods=["GET"])
def get_csrf():
    tokens = auth.CSRFToken.query.all()
    return jsonify([token.to_json() for token in tokens])

#get all profiles
@app.route("/profiles", methods=["GET"])
def get_profiles():
    profiles = Profile.query.all()
    json_profiles = list(map(lambda x: x.to_json(), profiles))
    return jsonify({"profiles": json_profiles})


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

###############################################################################################
###############################################################################################
################################### LEAGUE OF LEGENDS API ROUTES ##############################
###############################################################################################
###############################################################################################

from lolAPI import *

@app.route('/summoner/<string:region>', methods=['GET'])
@auth.csrf_auth_required
def get_summoner_info(token_enregistre, region):

    user = Profile.query.filter_by(discord_user_id=token_enregistre.discord_user_id).first()
    
    lol_name = user.get_LoL_name()

    if lol_name:
        response = get_summoner(region, lol_name)
        ok = response['puuid']

        res = get_all_matches("europe", ok)

        print("THE RESPONSE IS THERE :",res)

        return ok, 200
    return "ERRORE", 404

@app.route('/summoner/<string:region>/<string:name>/rank', methods=['GET'])
@auth.csrf_auth_required
def get_summoner_rank(_, region, name):
    return get_rank(region, name), 200

@app.route('/summoner/<string:region>/<string:name>/mastery', methods=['GET'])
@auth.csrf_auth_required
def get_summoner_mastery(_, region, name):
    return get_mastery_points(region, name), 200



@app.route('/summoner/<string:region>/match/<string:match_id>', methods=['GET'])
@auth.csrf_auth_required
def get_match_info(_, region, match_id):
    return get_match(region, match_id), 200

@app.route('/summoner/<string:region>/<string:puuid>/allmatches', methods=['GET'])
@auth.csrf_auth_required
def get_mathc_history(_, region, puuid):
    return get_all_matches(region, puuid), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0")