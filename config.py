from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask("app")

# CORS(app, origins=["https://backend.levellink.lol", "https://levellink.lol"])
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "45a5fc12445dbac2f59c35a5fc12b6"

db = SQLAlchemy(app)