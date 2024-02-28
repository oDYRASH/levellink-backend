from flask import request, jsonify
from config import app, db
from models import Profile
from discordAPI import getDiscordUser
from dbAPI import *
from sqlalchemy import desc


@app.route("/", methods=["GET"])
def ok():
    return jsonify({"CODE": "200 OK"})

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

@app.route("/create_post", methods=["POST"])
def createPost():

    newPost = Post(
        author_id = request.json.get("author_id"),
        title = request.json.get("title"),
        description =  request.json.get("description")
    )

    db.session.add(newPost)
    db.session.commit()

    return jsonify({"post": "oui"})


@app.route("/authUser", methods=["GET"])
def authUser():
    
    parametres_url = request.args

    # Vérifier si le paramètre "access_token" est présent
    if 'access_token' in parametres_url:

        discordUser = getDiscordUser(parametres_url['access_token'])
        if(not userExist(discordUser["id"])) :
            userCreated = createUser(discordUser)
            return f'Used has been created : {userCreated}'
        return discordUser
    else:
        return "You Don't Come From A Discord Auth Redirect (TOKEN)"


@app.route("/get_posts_by_user_ids", methods=["POST"])
def get_posts_by_user_ids():
    user_ids = request.json.get("user_ids")  # Récupérer la liste des identifiants d'utilisateur depuis la requête POST
    print(user_ids)
    # Utiliser une seule requête pour récupérer les 2 derniers posts pour chaque utilisateur spécifié
    posts = []
    limit_per_user = round( 30 / len(user_ids) ) +1
    print(limit_per_user)
    print(round(0.2))
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

    return USER.get_follows()


@app.route('/followconnection', methods=['GET'])
def gf():

    fs = Follows.query.all()
    return [fj.to_json() for fj in fs]
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
